import tomllib
from functools import cache
from pathlib import Path

SETTINGS_FILE = Path("sources.toml")


@cache
def get_settings():
    with open(SETTINGS_FILE, "rb") as file:
        return tomllib.load(file)
