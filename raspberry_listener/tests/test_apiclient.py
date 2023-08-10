from json.decoder import JSONDecodeError

import pytest
from sources.yr.apiclient import Variant, download_forecast_from_location
from sources.yr.yrforecast import ARNA, OSLO


def test_location():
    # Just test it doesn't raise any exceptions
    download_forecast_from_location(ARNA, Variant.Compact)
    download_forecast_from_location(OSLO, Variant.Compact)

    download_forecast_from_location(ARNA, Variant.Complete)
    download_forecast_from_location(OSLO, Variant.Complete)

    # Classic returns XML and should give us a JSONDecodeError, but still a 200 OK response code
    with pytest.raises(JSONDecodeError):
        download_forecast_from_location(ARNA, Variant.Classic)
    with pytest.raises(JSONDecodeError):
        download_forecast_from_location(OSLO, Variant.Classic)
