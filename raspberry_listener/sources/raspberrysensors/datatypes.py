from enum import Enum
import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, validator
import pandas as pd
import pandera as pa
from pandera.typing import Series, Index
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


def make_dtype_kwargs(enum):
    return {"categories": enum.values(), "ordered": False}


class SensorData(pa.DataFrameModel):
    sensor_type: Index[pd.CategoricalDtype] = pa.Field(
        dtype_kwargs=make_dtype_kwargs(SensorType), isin=SensorType.values()
    )
    sensor: Index[pd.CategoricalDtype] = pa.Field(
        dtype_kwargs=make_dtype_kwargs(Sensor), isin=Sensor.values()
    )
    timestamp: Index[pa.DateTime]

    reading: Series[float]
    unit: Series[pd.CategoricalDtype] = pa.Field(
        dtype_kwargs=make_dtype_kwargs(Unit), isin=Unit.values()
    )

    @classmethod
    def repair_dataframe(cls, df) -> pd.DataFrame:
        """The dataframe multiindex doesn't save correctly in parquet. The categorical types are dropped. To fix this, the index is first reset before saving, making them regular columns.
        The columns do preserve the categorical types."""
        df = cls._convert_columns(df)
        df = df.set_index(SensorReading._indexes, drop=True)
        return df

    @staticmethod
    def _convert_columns(df: pd.DataFrame) -> pd.DataFrame:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["sensor_type"] = pd.Categorical(
            df["sensor_type"], **make_dtype_kwargs(SensorType)
        )
        df["sensor"] = pd.Categorical(df["sensor"], **make_dtype_kwargs(Sensor))
        df["unit"] = pd.Categorical(df["unit"], **make_dtype_kwargs(Unit))
        return df


class SensorReading(BaseModel):
    sensor_type: str
    sensor: str
    timestamp: datetime

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

    _indexes = ["sensor_type", "sensor", "timestamp"]
    _columns = ["reading", "unit"]
