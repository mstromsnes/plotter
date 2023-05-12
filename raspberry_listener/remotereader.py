import requests
from fastapi import HTTPException
from io import BytesIO
import logging


logger = logging.getLogger("remotereader")
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
