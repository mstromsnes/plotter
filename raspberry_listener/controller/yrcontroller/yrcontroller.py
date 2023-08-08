from functools import partial

import numpy as np
from datamodels import HumidityModel, TemperatureModel
from sources import YrForecast
from sources.raspberrysensors.datatypes import Sensor, SensorType


def register_yr_forecast_data(
    yr_forecast: YrForecast,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    temperature_model.register_data(
        "Arna",
        lambda: (yr_forecast.time, yr_forecast.temperature),
        name,
    )
    humidity_model.register_data(
        "Arna",
        lambda: (yr_forecast.time, yr_forecast.humidity),
        name,
    )
