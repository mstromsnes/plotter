import logging
import tomllib
from collections import namedtuple
from datetime import datetime
from enum import Enum
from pathlib import Path

import httpx
from attrs import define
from fastapi import HTTPException

FORECAST_URL = "https://api.met.no/weatherapi/locationforecast/2.0/"
HISTORIC_URL = "https://frost.met.no/observations/v0.jsonld"
Location = namedtuple("Location", ["lat", "lon", "altitude"])


def client_id() -> str:
    def get_client_id(path: Path):
        with open(path, "rb") as file:
            settings = tomllib.load(file)
            return settings["frost"]["client_id"]

    try:
        return get_client_id(Path("raspberry_listener/frost_secrets.toml"))
    except OSError:
        return get_client_id(Path("frost_secrets.toml"))


class Variant(Enum):
    Complete = "complete"  # JSON forecast with all values
    Compact = "compact"  # JSON forecast with only the most used parameters
    Classic = "classic"  # XML


@define
class APIClient:
    client: httpx.Client = httpx.Client()

    def download_forecast_from_location(self, location: Location, variant: Variant):
        response = self.client.get(
            FORECAST_URL + variant.value, params=location._asdict()
        )

        if response.status_code != 200:
            raise HTTPException(response.status_code, response)

        log_response(response)

        return response.json()

    def download_historic_from_station_between_interval(
        self, station: str, early: datetime, late: datetime
    ):
        interval_str = convert_interval_to_frost_compliant_str(early, late)
        query_parameters = {
            "sources": station,
            "referencetime": interval_str,
            "elements": "air_temperature,relative_humidity",
        }
        response = self.client.get(
            HISTORIC_URL,
            params=query_parameters,
            auth=(client_id(), ""),
            timeout=30,
        )

        if response.status_code != 200:
            print(response.headers)
            print(response.content)
            raise HTTPException(response.status_code, response)

        return response.json()


@define
class AsyncAPIClient:
    async_client: httpx.AsyncClient = httpx.AsyncClient()

    async def download_forecast_from_location(
        self, location: Location, variant: Variant
    ):
        response = await self.async_client.get(
            FORECAST_URL + variant.value, params=location._asdict()
        )

        if response.status_code != 200:
            raise HTTPException(response.status_code, response)

        log_response(response)

        return response.json()

    async def download_historic_from_station_between_interval(
        self, station: str, early: datetime, late: datetime
    ):
        interval_str = convert_interval_to_frost_compliant_str(early, late)
        query_parameters = {
            "sources": station,
            "referencetime": interval_str,
            "elements": "air_temperature,relative_humidity",
        }
        response = await self.async_client.get(
            HISTORIC_URL,
            params=query_parameters,
            auth=(client_id(), ""),
            timeout=30,
        )

        if response.status_code != 200:
            print(response.headers)
            print(response.content)
            raise HTTPException(response.status_code, response)

        return response.json()


def convert_interval_to_frost_compliant_str(early: datetime, late: datetime) -> str:
    early_str = early.isoformat(sep="T", timespec="seconds")
    late_str = late.isoformat(sep="T", timespec="seconds")
    return "/".join((early_str, late_str))


def log_response(response: httpx.Response):
    size = response.headers["content-length"]
    logging.info(f"{format=} Response Size={size}")
    logging.debug(f"{response.status_code=}")
