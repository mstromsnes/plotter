from .datatypes import SensorType, Sensor

AVAILABLE_SENSORS: dict[SensorType, list[Sensor]] = {
    SensorType.Temperature: [Sensor.DHT11, Sensor.DS18B20, Sensor.PITEMP],
    SensorType.Humidity: [Sensor.DHT11],
}
