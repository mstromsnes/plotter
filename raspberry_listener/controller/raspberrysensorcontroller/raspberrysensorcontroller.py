from functools import partial

from datamodels import DataIdentifier, HumidityModel, TemperatureModel
from sources import SensorDataFrameHandler
from sources.raspberrysensors.datatypes import Sensor, SensorType


def register_raspberry_sensor_data(
    sensordata_handler: SensorDataFrameHandler,
    temperature_model: TemperatureModel,
    humidity_model: HumidityModel,
    source_name: str,
):
    temperature_model.register_data(
        DataIdentifier(source_name, Sensor.DHT11.value),
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.DHT11)),
    )
    temperature_model.register_data(
        DataIdentifier(source_name, Sensor.DS18B20.value),
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.DS18B20)),
    )
    temperature_model.register_data(
        DataIdentifier(source_name, Sensor.PITEMP.value),
        partial(sensordata_handler.get_data, (SensorType.Temperature, Sensor.PITEMP)),
    )
    humidity_model.register_data(
        DataIdentifier(source_name, Sensor.DHT11.value),
        partial(sensordata_handler.get_data, (SensorType.Humidity, Sensor.DHT11)),
    )
