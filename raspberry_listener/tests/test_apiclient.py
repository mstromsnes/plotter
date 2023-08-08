from json.decoder import JSONDecodeError

import pytest
from sources.yr.apiclient import Variant, download_location
from sources.yr.yr import ARNA, OSLO, Location


def test_location():
    # Just test it doesn't raise any exceptions
    download_location(ARNA, Variant.Compact)
    download_location(OSLO, Variant.Compact)

    download_location(ARNA, Variant.Complete)
    download_location(OSLO, Variant.Complete)

    # Classic returns XML and should give us a JSONDecodeError, but still a 200 OK response code
    with pytest.raises(JSONDecodeError):
        download_location(ARNA, Variant.Classic)
    with pytest.raises(JSONDecodeError):
        download_location(OSLO, Variant.Classic)
