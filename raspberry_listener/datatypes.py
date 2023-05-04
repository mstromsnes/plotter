from typing import Callable, Any, Protocol, Self, Iterable
from enum import Enum
import numpy as np
import numpy.typing as npt

# from abc import ABC, abstractmethod
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

    def bins(self, bincount) -> npt.ArrayLike | None:
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


class DataHandler(Protocol):
    def datatype(self) -> npt.DTypeLike:
        ...

    @property
    def ndims(self) -> int:
        ...

    @property
    def dataframe_names(self) -> list[str]:
        ...

    @property
    def tab_name(self) -> str:
        ...


class CPUHandler:
    @property
    def ndims(self):
        return 1

    def datatype(self):
        return float

    @property
    def dataframe_names(self):
        return ["PI_CPU_Temp"]

    @property
    def tab_name(self):
        return "PI CPU"


class MPUHandler:
    @property
    def ndims(self):
        return 1

    def datatype(self):
        return float

    @property
    def dataframe_names(self):
        return ["MPU_Temp"]

    @property
    def tab_name(self):
        return "MPU"


class DS18B20Handler:
    @property
    def ndims(self):
        return 1

    def datatype(self):
        return float

    @property
    def dataframe_names(self) -> list[str]:
        return ["DS18B20_Temp"]

    @property
    def tab_name(self):
        return "DS18B20"


class DHT11TemperatureHandler:
    @property
    def ndims(self):
        return 1

    def datatype(self):
        return int

    @property
    def dataframe_names(self):
        return ["DHT11_Temp"]

    @property
    def tab_name(self):
        return "DHT_T"


class DHT11HumidityHandler:
    @property
    def ndims(self):
        return 1

    def datatype(self):
        return int

    @property
    def dataframe_names(self):
        return ["DHT11_Humidity"]

    @property
    def tab_name(self):
        return "DHT_H"


class MPUAccelHandler:
    @property
    def ndims(self):
        return 3

    def datatype(self):
        return float

    @property
    def dataframe_names(self):
        return ["mpu_accel_x", "mpu_accel_y", "mpu_accel_z"]

    @property
    def tab_name(self):
        return "MPU_Accel"


class DataType(Enum):
    CPU_TEMP = CPUHandler()
    DHT_TEMP = DHT11TemperatureHandler()
    DHT_HUMIDITY = DHT11HumidityHandler()
    DS18B20_TEMP = DS18B20Handler()
    # MPU_TEMP = MPUHandler()
    # MPU_ACCEL = MPUAccelHandler()

    @classmethod
    def to_set(cls) -> set[DataHandler]:
        return set((member.value for _, member in cls.__members__.items()))
