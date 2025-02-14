import logging
import requests
import time
from typing import List, AsyncIterable, Union
import aiohttp
from aiohttp.client_reqrep import ClientResponse
from aiohttp.typedefs import StrOrURL
import atexit
import asyncio
from asyncio import Queue, CancelledError
from contextlib import asynccontextmanager, suppress
# from decimal import Decimal

"""
TODO: Most of the code needs explanations for myself
"""

LOG = logging.getLogger(__name__)

"""
Connection Base Class.
Methods:
    raw_data_callback: For handling raw data, defaults to None.
    read(self): An abstract class method hat must be implemented by subclasses.
"""


class Connection:
    raw_data_callback = None

    async def read(self) -> bytes:
        raise NotImplementedError


"""
Synchronous HTTP requests class.
Methods:
    Inherited the read function (must be implemented here) from Connection.
    process_response: Calls the raw data callback if set to True. 
    read: Makes a get request to an url, with optional params.
"""


class HTTPSync(Connection):
    def process_response(
        self,
        r,
        address,
        # json=False,
        # text=False,
        uuid=None,
    ):
        if self.raw_data_callback:
            self.raw_data_callback.sync_callback(
                r.text, time.time(), str(uuid), endpoint=address
            )

        r.raise_for_status()
        # if json:
        #     return json_parser.loads(r.text, parse_float=Decimal)
        # if text:
        #     return r.text
        return r

    def read(
        self, url: str, params=None, headers=None, json=False, text=True, uuid=None
    ):
        LOG.debug("HTTPSync: Requesting data from %s", url)
        r = requests.get(url, headers=headers, params=params)
        return self.process_response(r, url, json=json, text=text, uuid=uuid)

    """
    TODO: No need to write, right?
    """


"""
Base class for async connections.
Keeps track of connection count and handles connection life cycle.
Methods:
    init: Initialize with connection ID
    connect: Context manager for handling connections. Awaits for the connection to open, else close.
    close: Close the connection.
    _open: Abstract method for opening connections, implementation required in subclasses.
    is_open: Check if connection is active. Implementation required in subclasses.
"""


class AsyncConnection(Connection):
    conn_count: int = 0

    def __init__(
        self,
        conn_id: str,
        # authentication=None,
        # subscription=None,
    ):
        """
        conn_id: str
            the unique identifier for the connection
        """
        AsyncConnection.conn_count += 1
        self.id: str = conn_id
        self.received: int = 0
        self.conn: aiohttp.ClientSession = None
        atexit.register(self.__del__)

    def __del__(self):
        try:
            if self.is_open:
                asyncio.ensure_future(self.close())
        except (RuntimeError, RuntimeWarning):
            # no event loop, ignore error
            pass

    @property
    def uuid(self):
        return self.id

    @asynccontextmanager
    async def connect(self):
        await self._open()
        try:
            yield self
        finally:
            await self.close()

    async def _open(self):
        raise NotImplementedError

    @property
    def is_open(self) -> bool:
        raise NotImplementedError

    async def close(self):
        if self.is_open:
            conn = self.conn
            self.conn = None
            await conn.close()
            LOG.info("%s: closed connection %r", self.id, conn.__class__.__name__)


"""
Handles async HTTP connections.
Methods:
    init: Initialize with connection ID and optional proxy.
    _handle_error: Handles HTTP error responses.
    read: Makes async GET requests with retry logic.
"""


class HTTPAsyncConn(AsyncConnection):
    def __init__(self, conn_id: str, proxy: StrOrURL = None):
        """
        conn_id: str
            id associated with the connection
        proxy: str, URL
            proxy url (GET only)
        """
        super().__init__(f"{conn_id}.http.{self.conn_count}")
        self.proxy = proxy

    @property
    def is_open(self) -> bool:
        return self.conn and not self.conn.closed

    def _handle_error(self, resp: ClientResponse, data: bytes):
        if resp.status != 200:
            LOG.error("%s: Status code %d for URL %s", self.id, resp.status, resp.url)
            LOG.error("%s: Headers: %s", self.id, resp.headers)
            LOG.error("%s: Resp: %s", self.id, data)
            resp.raise_for_status()

    async def _open(self):
        if self.is_open:
            LOG.warning("%s: HTTP session already created", self.id)
        else:
            LOG.debug("%s: create HTTP session", self.id)
            """
            Create an aiohttp ClientSession for making asynchronous HTTP requests
            This session can be reused for multiple requests, improving efficiency
            It handles connection pooling, cookie storage, and other HTTP-related tasks
            """
            self.conn = aiohttp.ClientSession()
            self.sent = 0
            self.received = 0
            self.last_message = None

    async def read(
        self,
        address: str,
        header=None,
        params=None,
        return_headers=False,
        retry_count=0,  # Retry or not?
        retry_delay=60,  # Delay before retry.
    ) -> str:
        """
        Essential. If connection is not open, don't start to read.
        """
        if not self.is_open:
            await self._open()

        LOG.debug("%s: requesting data from %s", self.id, address)

        """
        The logic that keeps the program running.
        """
        while True:
            """
            Async GET request.
            The conn is aiohttp.ClientSession()
            """
            async with self.conn.get(
                address, headers=header, params=params, proxy=self.proxy
            ) as response:
                data = await response.text()
                self.last_message = time.time()
                """
                self.received: Set by _open. If received, count +1.
                """
                self.received += 1

                """
                From the base class. If raw_data_callback != None.
                """
                if self.raw_data_callback:
                    await self.raw_data_callback(
                        data,
                        self.last_message,
                        self.id,
                        endpoint=address,
                        header=None
                        if return_headers is False
                        else dict(response.headers),
                    )
                if response.status == 429 and retry_count:
                    LOG.warning(
                        "%s: encountered a rate limit for address %s, retrying in %i seconds",
                        self.id,
                        address,
                        self.retry_delay,
                    )
                    retry_count -= 1
                    if retry_count < 0:
                        self._handle_error(response, data)
                    """
                    Await for the delay before retry.
                    """
                    await asyncio.sleep(retry_delay)

                    continue

                self._handle_error(response, data)
                if return_headers:
                    return data, response.headers
                return data


"""
Polls one or more HTTP endpoints periodically.
Methods:
    init: Sets up polling with:
        addresses(either a list or an url string), 
        delays(retry delays, default to 60 seconds), 
        sleep(Time before polls again, default to 1 second).
    _read_address: Reads from a single address.
    read: Polls all configured addresses.
"""


class HTTPPoll(HTTPAsyncConn):
    def __init__(
        self,
        address: Union[List, str],
        conn_id: str,
        delay: float = 60,
        sleep: float = 1,
        proxy: StrOrURL = None,
    ):
        super().__init__(f"{conn_id}.http.{self.conn_count}", proxy)
        if isinstance(address, str):
            address = [address]
        self.address = address

        self.sleep = sleep
        self.delay = delay

    """
    Basically the read method is the orchestrator,
    based on the wait time set on sleep,
    calls the _read_address function to make a GET request.
    """

    async def _read_address(self, address: str, header=None) -> str:
        LOG.debug("%s: polling %s", self.id, address)
        while True:
            if not self.is_open:
                LOG.error("%s: connection closed in read()", self.id)
                # raise error

            async with self.conn.get(
                address, headers=header, proxy=self.proxy
            ) as response:
                data = await response.text()
                self.received += 1
                self.last_message = time.time()
                if self.raw_data_callback:
                    await self.raw_data_callback(
                        data, self.last_message, self.id, endpoint=address
                    )
                if response.status != 429:
                    response.raise_for_status()
                    return data
            LOG.warning(
                "%s: encountered a rate limit for address %s, retrying in %f seconds",
                self.id,
                address,
                self.delay,
            )
            await asyncio.sleep(self.delay)

    async def read(self, header=None) -> AsyncIterable[str]:
        while True:
            for addr in self.address:
                yield await self._read_address(addr, header)
            await asyncio.sleep(self.sleep)


"""
More advanced version of HTTPPoll that handles multiple endpoints concurrently
Uses an async queue for managing concurrent requests.
Methods:
    _poll_address: Polls a single address concurrently.
    read: Sets up concurrent polling for all addresses.
"""


class HTTPConcurrentPoll(HTTPPoll):
    """Polls each address concurrently in it's own Task"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Initialize an async queue. Queue() is from asyncio.
        """
        self._queue = Queue()

    async def _poll_address(self, address: str, header=None):
        while True:
            """
            Polls a single address concurrently, and put the data into queue.
            """
            data = await self._read_address(address, header)
            await self._queue.put(data)
            await asyncio.sleep(self.sleep)

    async def read(self, header=None) -> AsyncIterable[str]:
        """
        asyncio.gather: Returns aggregated futures from the poll (or coroutine or future whatever you wanna call it.)
        """
        tasks = asyncio.gather(
            *(self._poll_address(address, header) for address in self.address)
        )

        try:
            """
            Runs a continuous loop that waits for data to arrive in the queue.
            It uses a 1-second timeout to avoid blocking indefinitely.

            If no data arrives within 1 second, it continues the loop.

            When data is received, it's yielded to the caller.
            This loop continues until all polling tasks are completed.

            The 'finally' block ensures proper cleanup:
            - If tasks are still running, it cancels them.
            - It waits for cancelled tasks to finish.
            - If any task raised an exception, it's re-raised here.
            """
            while not tasks.done():
                with suppress(asyncio.exceptions.TimeoutError):
                    yield await asyncio.wait_for(self._queue.get(), timeout=1)

        finally:
            if not tasks.done():
                tasks.cancel()
                with suppress(CancelledError):
                    await tasks
            elif tasks.exception() is not None:
                raise tasks.exception()
