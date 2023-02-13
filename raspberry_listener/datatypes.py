from typing import Callable, Any, Protocol, Self
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

DataSet = tuple[np.ndarray, np.ndarray]


class DataHandler(ABC, str):
    @abstractmethod
    def datatype(self) -> Callable[[str], Any]:
        ...


class CPUHandler(DataHandler):
    def datatype(self):
        return float


class DataType(Enum):
    CPU_TEMP = CPUHandler("CPU_Temp")

    def datatype(self):
        return self.value.datatype()

    @classmethod
    def to_set(cls) -> set[DataHandler]:
        return set((member.value for _, member in cls.__members__.items()))
