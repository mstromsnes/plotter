from datamodels import HumidityModel, TemperatureModel
from sources import YrForecast, YrHistoric


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


def register_yr_historic_data(
    yr_historic: YrHistoric,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    temperature_model.register_data(
        "Arna",
        lambda: (yr_historic.time, yr_historic.temperature),
        name,
    )
    humidity_model.register_data(
        "Arna",
        lambda: (yr_historic.time, yr_historic.humidity),
        name,
    )
