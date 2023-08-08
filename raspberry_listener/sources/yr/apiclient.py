import logging
from collections import namedtuple
from enum import Enum

import httpx
from fastapi import HTTPException

URL = "https://api.met.no/weatherapi/locationforecast/2.0/"

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
