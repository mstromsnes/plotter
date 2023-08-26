from collections.abc import Sequence
from functools import partial

from datamodels import (
    DataIdentifier,
    DataTypeManager,
    DataTypeModel,
    HumidityModel,
    TemperatureModel,
)
from sources import SensorDataFrameHandler
from sources.raspberrysensors.datatypes import Sensor, SensorType


def register_raspberry_sensor_data(
    sensordata_handler: SensorDataFrameHandler,
    datatype_manager: DataTypeManager,
    source_name: str,
) -> Sequence[DataTypeModel]:
    temperature_model = datatype_manager.get_model(TemperatureModel)
    humidity_model = datatype_manager.get_model(HumidityModel)
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

    return temperature_model, humidity_model
