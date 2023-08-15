from collections.abc import Callable
from functools import partial

import numpy as np
from datamodels import HumidityModel, TemperatureModel
from pandas import Series, Timedelta
from sources import YrForecast, YrHistoric, get_settings


def time_resolution_indexer(time_series: Series, delta: Timedelta) -> Series:
    """Generates a boolean indexer into the Series/Dataframe
    based on the difference between timestamps in the
    provided timeseries.

    Args:
        time_series (Series): The underlying timeseries used to create the boolean indexer on
        delta (Timedelta): The indexer returns true for all differences less than or equal to this delta

    Returns:
        Series: A list of booleans useful for indexing a dataframe
    """
    difference = time_series.diff()
    difference[0] = difference[1]
    return difference <= delta


def register_yr_forecast_data(
    yr_forecast: YrForecast,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    def get_data(location: str, variable: str):
        data = yr_forecast.data_for_location(location)

        def extract_data(variable: str, indexer_fn: Callable[[Series], Series]):
            indexer = indexer_fn(data["time"])
            reduced_frame = data[["time", variable]].dropna()[indexer]
            return (
                reduced_frame["time"].to_numpy(),
                reduced_frame[variable].to_numpy(),
            )

        # The forecast has a lot of data with 6 hour gaps.
        # They look very out of place, and aren't informative
        # without percentile error ranges, so we remove them
        one_hour_resolution = partial(time_resolution_indexer, delta=Timedelta("1h"))
        match variable:
            case "temperature":
                return extract_data("air_temperature", one_hour_resolution)
            case "humidity":
                return extract_data("relative_humidity", one_hour_resolution)
            case _:
                raise KeyError("Unsupported variable type")

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
