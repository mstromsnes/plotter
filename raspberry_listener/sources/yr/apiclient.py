import logging
from collections import namedtuple
from datetime import datetime
from enum import Enum

import httpx
from fastapi import HTTPException

FORECAST_URL = "https://api.met.no/weatherapi/locationforecast/2.0/"
HISTORIC_URL = "https://frost.met.no/observations/v0.jsonld"
Location = namedtuple("Location", ["lat", "lon", "altitude"])


class Variant(Enum):
    Complete = "complete"  # JSON forecast with all values
    Compact = "compact"  # JSON forecast with only the most used parameters
    Classic = "classic"  # XML


def download_location(location: Location, variant: Variant):
    query = make_query_string(**location._asdict())
    print(URL + variant.value + query)
    response = httpx.get(URL + variant.value + query)

    if response.status_code != 200:
        raise HTTPException(response.status_code, response)

    log_response(response)

    return response.json()


def download_historic_from_station_between_interval(
    station: str, early: datetime, late: datetime, period: str
):
    interval_str = convert_interval_to_frost_compliant_str(early, late, period)
    query_parameters = {
        "sources": station,
        "referencetime": interval_str,
        "elements": "air_temperature,relative_humidity",
    }
    response = httpx.get(
        HISTORIC_URL, params=query_parameters, auth=(HISTORIC_CLIENT_ID, ""), timeout=30
    )

    if response.status_code != 200:
        print(response.headers)
        raise HTTPException(response.status_code, response)

    return response.json()


def convert_interval_to_frost_compliant_str(
    early: datetime, late: datetime, period: str
) -> str:
    early_str = early.isoformat(sep="T", timespec="seconds")
    late_str = late.isoformat(sep="T", timespec="seconds")
    return "/".join((early_str, late_str))


def make_query_string(**kwargs):
    if len(kwargs) == 0:
        return ""
    query = "?"
    for key, value in kwargs.items():
        query += f"{key}={round(value, 4)}&"  # yr developer guide says not to use more than 4 decimal places
    return query[:-1]  # Cut off the last &


def log_response(response: httpx.Response):
    size = response.headers["content-length"]
    logging.info(f"{format=} Response Size={size}")
    logging.debug(f"{response.status_code=}")
