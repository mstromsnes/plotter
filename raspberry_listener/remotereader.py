import requests
from fastapi import HTTPException
from io import BytesIO


def download_archived_file() -> BytesIO:
    response = requests.get("http://192.168.4.141:8000/archive")
    if response.status_code != 200:
        raise HTTPException(response.status_code, response.json())
    buffer = BytesIO()
    buffer.write(response.content)
    print(response.headers["content-length"])
    return buffer


def get_latest_archive():
    return download_archived_file()
