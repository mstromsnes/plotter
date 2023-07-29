from functools import partial

from datamodels import HumidityModel, TemperatureModel
from sources import SensorDataFrameHandler
from sources.raspberrysensors.datatypes import Sensor, SensorType


def register_raspberry_sensor_data(
    sensordata_handler: SensorDataFrameHandler,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    name: str,
):
    temperature_model.register_data(
        Sensor.DHT11.value,
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.DHT11)),
        name,
    )
    temperature_model.register_data(
        Sensor.DS18B20.value,
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.DS18B20)),
        name,
    )
    temperature_model.register_data(
        Sensor.PITEMP.value,
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.PITEMP)),
        name,
    )
    humidity_model.register_data(
        Sensor.DHT11.value,
        partial(sensordata_handler.get_data, (SensorType.Humidity, Sensor.DHT11)),
        name,
    )
