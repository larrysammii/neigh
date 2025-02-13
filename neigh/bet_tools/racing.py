import asyncio
from neigh.models.racing import Horse
from neigh.core.connection import HTTPConcurrentPoll
from typing import Union
from parsel import Selector
import logging
import datetime

logger = logging.getLogger(__name__)


class Racing:
    BASE_URL = "https://racing.hkjc.com"
    HORSE_PROFILE_BASE_URL = "/racing/information/English/Horse/Horse.aspx"
    TEST_URL = [
        "https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2023_J456&Option=1",
        "https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2020_E486&Option=1",
    ]
    HORSE_ID = "HK_2023_J456"
    SHOW_ALL_OPT = "&Option=1"

    @classmethod
    def joinurl(cls, base_url: str, endpoint: str, param: str, show_all: str) -> str:
        return base_url + endpoint + param + show_all

    @classmethod
    def date_normalize(cls, date_str: str) -> datetime.date:
        datetime.date.strftime(date_str, "%d/%m/%y")

    def __init__(
        self,
        channel: str,
        poll_interval: float = 60.0,
        sleep: float = 5,
    ):
        self.channel = channel

        """
        TODO: remove TEST_URL
        """
        self.poller = HTTPConcurrentPoll(
            # address=self.BASE_URL + self.HORSE_PROFILE_BASE_URL + self.TEST_URL,
            address=self.TEST_URL,
            conn_id=f"Racing: {channel}",
            delay=poll_interval,
            sleep=sleep,
        )

    async def start_polling(self):
        """Start the polling process"""
        try:
            async with self.poller.connect():
                async for data in self.poller.read():
                    # Process the scraped data here
                    await self.process_scraped_data(data)
        except asyncio.CancelledError:
            logger.info("Polling stopped")
            raise
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise

    async def process_scraped_data(self, data: Union[str, bytes]):
        """Process the scraped data from any of the polled endpoints"""
        try:
            if isinstance(data, bytes):
                text = data.decode("utf-8")
            else:
                text = data

            selector = Selector(text=text)

            # Parse the profile using your existing logic
            profile = {}
            outer_table = selector.css("table.horseProfile table.table_eng_text")
            for inner_table in outer_table:
                for row in inner_table.css("tr"):
                    key = row.css("td:first-child::text").get()
                    if not key:
                        continue
                    key = key.strip()
                    value = row.css("td:last-child")

                    if value.css("*") and value.xpath(".//select"):
                        value = value.xpath(".//select/option/text()").getall()
                    elif value.css("*") and value.xpath(".//a"):
                        value = [
                            {
                                "text": a.xpath(".//text()").get().strip(),
                                "url": a.xpath("@href").get(),
                            }
                            for a in value.xpath(".//a")
                        ]
                    else:
                        value = value.xpath(".//text()").get()
                        if value:
                            value = value.strip()

                    profile[key] = value

            # TODO: Deserialise
            print(profile)

        except Exception as e:
            logger.error(f"Error processing scraped data: {e}")
            raise
