from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol


class DataSet_Fn(Protocol):
    def __call__(self) -> Any:
        ...


@dataclass
class Unit:
    short: str
    long: str
    explanation: str


class DataTypeModel(ABC):
    _unit: Unit

    def __init__(self):
        self._has_data = False

    def has_data(self):
        return self._has_data

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        ...

    @abstractmethod
    def get_data(self, key: tuple[str, str]) -> Any:
        ...

    @abstractmethod
    def get_dataset_names(self) -> set[tuple[str, str]]:
        ...

    @abstractmethod
    def get_dataset_names(self) -> set[str]:
        ...

    @classmethod
    @property
    def unit(cls):
        return cls._unit


class DataTypeManager:
    def __init__(self):
        self._datatypemodels: dict[type[DataTypeModel], DataTypeModel] = {}

    def register_datatype(self, datatype: DataTypeModel):
        if type(datatype) in self._datatypemodels.keys():
            raise KeyError(f"Datatype of type {type(datatype)} already registered.")
        self._datatypemodels[type(datatype)] = datatype

    def get_types(self) -> set[type[DataTypeModel]]:
        return set(self._datatypemodels.keys())

    def get_model(self, type: type[DataTypeModel]) -> DataTypeModel:
        return self._datatypemodels[type]
