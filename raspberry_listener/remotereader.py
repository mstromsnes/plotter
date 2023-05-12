import requests
from fastapi import HTTPException
from io import BytesIO
from enum import Enum
import logging


logger = logging.getLogger("remotereader")

class Format(Enum):
    Parquet = "parquet/"
    JSON = "json/"

    if response.status_code != 200:
        raise HTTPException(response.status_code, response.json())
    log_response(response)
    buffer = BytesIO()
    buffer.write(response.content)
    print(response.headers["content-length"])
    return buffer



def log_response(response: requests.Response):
    size = response.headers["content-length"]
    logging.info(f"{format=} Response Size={size}")
    logging.debug(f"{response.status_code=}")
