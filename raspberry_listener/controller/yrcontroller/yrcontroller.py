from datamodels import HumidityModel, TemperatureModel
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
        pass

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
