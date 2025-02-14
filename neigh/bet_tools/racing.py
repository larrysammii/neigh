import asyncio
from neigh.models.racing import Horse
from neigh.core.connection import HTTPConcurrentPoll
from typing import Union
from parsel import Selector
import logging
import datetime
import re

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

    async def _start_polling(self):
        """Start the polling process"""
        try:
            async with self.poller.connect():
                async for data in self.poller.read():
                    # Process the scraped data here
                    await self.process_horse_profile(data)
        except asyncio.CancelledError:
            logger.info("Polling stopped")
            raise
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise

    """
    For horse profiles only.
    Process the scraped data from polled horse profiles endpoints.
    """

    async def process_horse_profile(self, data: Union[str, bytes]) -> dict:
        """Process horse profile data from HTML.

        Args:
            data: HTML data containing horse profile

        Returns:
            dict: Processed horse profile data
        """
        try:
            selector = Selector(text=data)
            rows = self._extract_rows(selector)
            profile = self._process_rows(rows)
            profile = self._clean_profile_values(profile)
            print(profile)
            return profile

        except Exception as e:
            logger.error(f"Error processing scraped data: {e}")
            raise

    def _clean_key(self, key: str) -> str:
        """Clean key by removing special characters and converting spaces to underscores.

        Args:
            key: The key to clean

        Returns:
            str: Cleaned key
        """
        # Remove special characters except spaces
        key = "".join(char for char in key if char.isalnum() or char.isspace())
        # Convert spaces to underscores and ensure lowercase
        return key.strip().lower().replace(" ", "_")

    def _extract_rows(self, selector: Selector) -> list:
        """Extract raw rows from HTML selector.

        Args:
            selector: Parsel selector containing HTML

        Returns:
            list: List of (key, value) tuples
        """
        rows = []
        outer_table = selector.css("table.horseProfile table.table_eng_text")
        for inner_table in outer_table:
            for row in inner_table.css("tr"):
                key = row.css("td:first-child::text").get()
                if not key:
                    continue
                # Clean key using the dedicated method
                key = self._clean_key(key.rstrip("*"))

                value = row.css("td:last-child")
                if value.css("*") and value.xpath(".//select"):
                    value = [
                        v.strip().lower()
                        for v in value.xpath(".//select/option/text()").getall()
                    ]
                elif value.css("*") and value.xpath(".//a"):
                    value = [
                        {
                            "text": a.xpath(".//text()").get().strip().lower(),
                            "url": a.xpath("@href").get(),
                        }
                        for a in value.xpath(".//a")
                    ]
                else:
                    value = value.xpath(".//text()").get()
                    if value:
                        value = value.strip().lower()

                rows.append((key, value))
        return rows

    def _process_rows(self, rows: list) -> dict:
        """Process extracted rows into structured data.

        Args:
            rows: List of (key, value) tuples

        Returns:
            dict: Processed profile data
        """
        special_cases = {}
        normal_cases = {}

        for key, value in rows:
            if not isinstance(value, str):
                normal_cases[key] = value
                continue

            if "/" in key:
                self._handle_split_fields(key, value, special_cases, normal_cases)
            elif "1-2-3-" in key:
                self._handle_placement_fields(value, normal_cases)
            elif "current stable" in key:
                self._handle_stable_info(value, special_cases)
            else:
                normal_cases[key] = value

        profile = {}
        profile.update(special_cases)
        profile.update(normal_cases)
        return profile

    def _handle_split_fields(
        self, key: str, value: str, special_cases: dict, normal_cases: dict
    ) -> None:
        """Handle fields that are split by forward slash.

        Args:
            key: The original key containing forward slashes
            value: The corresponding value
            special_cases: Dict to store special case results
            normal_cases: Dict to store normal case results
        """
        keys = [k.strip() for k in key.split("/")]
        values = [v.strip() for v in value.split("/")]

        if "colour" in keys:
            special_cases["colour"] = values[:-1]
            special_cases["sex"] = values[-1]
        elif len(keys) == len(values):
            normal_cases.update(dict(zip(keys, values)))

    def _handle_placement_fields(self, value: str, normal_cases: dict) -> None:
        """Handle placement fields (1-2-3).

        Args:
            value: The placement values string
            normal_cases: Dict to store results
        """
        values = value.split("-")
        fields = [
            "first_place",
            "second_place",
            "third_place",
            "total_starts_participation",
        ]
        normal_cases.update(dict(zip(fields, (v.strip() for v in values))))

    def _handle_stable_info(self, value: str, special_cases: dict) -> None:
        """Handle stable information fields.

        Args:
            value: The stable info string
            special_cases: Dict to store results
        """
        if "(" in value:
            location, date_part = value.split("(", 1)
            special_cases["current_stable_location"] = location.strip()
            special_cases["arrival_date"] = date_part.rstrip(")")

    def _clean_profile_values(self, profile: dict) -> dict:
        """Clean and normalize profile values.

        Args:
            profile: Dict containing profile data

        Returns:
            dict: Cleaned profile data
        """
        return {
            k: int(re.sub(r"[^\d]", "", v))
            if isinstance(v, str) and (v.isdigit() or "$" in v)
            else v
            for k, v in profile.items()
        }
