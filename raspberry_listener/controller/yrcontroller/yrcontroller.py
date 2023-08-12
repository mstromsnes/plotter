from functools import partial
from typing import Callable

import numpy as np
from datamodels import HumidityModel, TemperatureModel
from pandas import Series
from sources import YrForecast, YrHistoric, get_settings


def register_yr_forecast_data(
    yr_forecast: YrForecast,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    def get_data(location: str, variable: str):
        pass

    settings = get_settings()
    locations: dict[str, dict[str, float]] = settings["yr"]["locations"]
    for location in locations.keys():
        temperature_model.register_data(
            location,
            partial(get_data, location, "temperature"),
            name,
        )
        humidity_model.register_data(
            location,
            partial(get_data, location, "humidity"),
            name,
        )


def register_yr_historic_data(
    yr_historic: YrHistoric,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    def get_data(location: str, variable: str):
        data = yr_historic.data_for_location(location)

        def med_filter(series: Series, window: int) -> Series:
            return series.rolling(window, min_periods=1).median()

        def extract_data(element_id: str, filter: Callable[[Series], Series]):
            frame = data[data["elementId"] == element_id]
            value_series = filter(frame["value"])
            time = frame["referenceTime"].to_numpy(dtype="datetime64[s]")
            value = value_series.to_numpy(dtype=np.float32)
            return time, value

        match variable:
            case "temperature":
                return extract_data("air_temperature", partial(med_filter, window=3))
            case "humidity":
                return extract_data("relative_humidity", partial(med_filter, window=3))
            case _:
                raise KeyError("Unsupported variable type")

    settings = get_settings()
    locations: dict[str, str] = settings["frost"]["stations"]
    for location in locations.keys():
        temperature_model.register_data(
            location,
            partial(get_data, location, "temperature"),
            name,
        )
        humidity_model.register_data(
            location,
            partial(get_data, location, "humidity"),
            name,
        )
