import requests
from fastapi import HTTPException
from io import BytesIO
import pandera as pa
from enum import Enum
import logging

URL = "http://192.168.4.141:8000"
# URL = "http://localhost:8000"
ARCHIVE_ENDPOINT = "/archive/"

logger = logging.getLogger("remotereader")


class ArchiveNotAvailableException(Exception):
    ...


class Format(Enum):
    Parquet = "parquet/"
    JSON = "json/"


def download_archive(
    timestamp: pa.DateTime | None = None, format: Format = Format.Parquet
):
    try:
        response = send_request(timestamp, format)
    except requests.ConnectionError:
        raise ArchiveNotAvailableException

    if response.status_code != 200:
        raise HTTPException(response.status_code, response.json())

    log_response(response)

    return extract_payload(response, format)


def send_request(timestamp: pa.DateTime | None, format: Format = Format.Parquet):
    format_endpoint = format.value
    query = make_query_string(start=timestamp) if timestamp is not None else ""
    request_url = URL + ARCHIVE_ENDPOINT + format_endpoint + query
    if timestamp is None:
        response = requests.get(request_url)
    else:
        response = requests.post(request_url, json=str(timestamp))
    return response


def make_query_string(**kwargs):
    if len(kwargs) == 0:
        return ""
    query = "?"
    for key, value in kwargs.items():
        query += f"{key}={value}&"
    return query[:-1]  # Cut off the last &


def get_bytes_content(response: requests.Response) -> BytesIO:
    buffer = BytesIO()
    buffer.write(response.content)
    buffer.seek(0)
    return buffer


def extract_payload(response: requests.Response, format):
    match format:
        case Format.Parquet:
            return get_bytes_content(response)
        case Format.JSON:
            return response.json()


def log_response(response: requests.Response):
    size = response.headers["content-length"]
    logging.info(f"{format=} Response Size={size}")
    logging.debug(f"{response.status_code=}")
