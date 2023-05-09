from enum import Enum
import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, validator
import pandera as pa
from pandera.typing import DataFrame, Series, Index
from pandera.api.extensions import register_check_method
from datetime import datetime


from math import ceil
from functools import cache


class DataSet(tuple):
    def __new__(cls, time_array: np.ndarray, data_array: np.ndarray):
        return tuple.__new__(DataSet, (time_array, data_array))

    # """Many of the sensors have a fixed resolution or quantization. Maybe 1 K, maybe 1/8 K or similar.
    # These methods are useful for determining bin-size for histograms.
    # The DHT11 measures room temp 15-30 C in 1 degree increments.
    # This means the number of expected values is ~15.
    # The humidity is 1% from 20-80%, giving 60 possible and expected values. For such low dynamic range data it would be nice to center the histogram bins on these values."""
    @property
    @cache
    def dynamic_range(self) -> int:
        dataset_value_range = self[1].max() - self[1].min()
        return ceil(
            dataset_value_range / self.smallest_difference_between_unique_values
        )

    def _reduced_dynamic_range(self, value_difference: float | int) -> int | float:
        dataset_value_range = self[1].max() - self[1].min()
        return ceil(dataset_value_range / value_difference)

    @property
    @cache
    def smallest_difference_between_unique_values(self) -> float | int:
        return np.diff(np.unique(self[1])).min()

    def bins(self, bincount) -> npt.ArrayLike:
        discretization = self.smallest_difference_between_unique_values
        while self._reduced_dynamic_range(discretization) > bincount:
            # Limits the number of buckets to maximally bincount. Doesn't guarantee bincount buckets, but nearest lower power of 2.
            discretization = discretization * 2
        left_of_first_bin = self[1].min() - float(discretization) / 2
        right_of_last_bin_plus_one = self[1].max() + 3 * (float(discretization) / 2)
        # Plus 1 as arange is not inclusive. We want the final element so we go one extra.
        return np.arange(left_of_first_bin, right_of_last_bin_plus_one, discretization)

    def __hash__(self):
        # The standard hash for tuple is to hash its elements. np.ndarrays are unhashable.
        # We want hash for @cache decorator. This makes a hash of the last 5 elements multiplied by the size of the data.
        # The DHT11 should have the same last 5 elements all the time, but different dataset sizes.
        # This is fairly fragile but should do for now.
        return hash(sum(self[1][-5:]) * 10 * len(self[1]))


class MemberStrEnum(Enum):
    """A workaround to get valid str values from the enum. Python 3.12 will allow us to test for values directly"""

    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]


class Sensor(MemberStrEnum):
    DHT11 = "DHT11"
    PITEMP = "PI_CPU"
    DS18B20 = "DS18B20"


class SensorType(MemberStrEnum):
    Temperature = "temperature"
    Humidity = "humidity"


class Unit(MemberStrEnum):
    Celsius = "C"
    RelativeHumidity = "%"


@register_check_method(statistics=["enum"])
def is_in_enum(df, *, enum: MemberStrEnum):
    return df.isin(enum.values())


class SensorData(pa.DataFrameModel):
    sensor_type: Index[str] = pa.Field(
        is_in_enum=SensorType,
    )
    sensor: Index[str] = pa.Field(is_in_enum=Sensor)
    timestamp: Index[pa.DateTime] = pa.Field(check_name=True)

    reading: Series[float]
    unit: Series[str] = pa.Field(is_in_enum=Unit)


class SensorReading(BaseModel):
    timestamp: datetime
    sensor_type: str
    sensor: str

    reading: float
    unit: str

    @validator("sensor")
    @classmethod
    def is_in_sensor(cls, v):
        if v not in Sensor.values():
            raise ValueError("Not a legitimate Sensor value")
        return v

    @validator("unit")
    @classmethod
    def is_in_unit(cls, v):
        if v not in Unit.values():
            raise ValueError("Not a legitimate Unit value")
        return v

    @validator("sensor_type")
    @classmethod
    def is_in_sensor_type(cls, v):
        if v not in SensorType.values():
            raise ValueError("Not a legitimate SensorType value")
        return v

    _indexes = ["timestamp", "sensor", "sensor_type"]
    _columns = ["reading", "unit"]
