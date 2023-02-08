from typing import Callable, Any, Protocol
from enum import Enum


class DataHandler(Protocol):
    def datatype(self, value: str) -> Any:
        ...

    def request(self) -> str:
        ...


class CPUHandler:
    def request(self) -> str:
        return "cpu"

    def datatype(self, value: str) -> float:
        return float(value)


class DataType(Enum):
    CPU_TEMP = CPUHandler()

    @property
    def value(self) -> DataHandler:
        return super().value

    def datatype(self, value: str):
        return self.value.datatype(value)

    def request(self) -> str:
        return self.value.request()
