from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Self


class DataSet_Fn(Protocol):
    def __call__(self) -> Any:
        ...


@dataclass
class Unit:
    short: str
    long: str
    explanation: str


Observer = Callable[[str], None]


class DataTypeModel(ABC):
    _unit: Unit

    def __init__(self):
        self._has_data = False
        self._observers: set[Observer] = set()

    def has_data(self):
        return self._has_data

    def register_observer(self, observer: Observer):
        self._observers.add(observer)

    def remove_observer(self, observer: Observer):
        try:
            self._observers.remove(observer)
        except KeyError:
            pass

    @abstractmethod
    def name(self) -> str:
        ...

    # This is essentially a decorator that only decorates the private _register_data method.
    def register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        self._register_data(name, dataset_fn, source_name)
        for obs in self._observers:
            obs(source_name)

    @abstractmethod
    def _register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        ...

    @abstractmethod
    def get_data_name_from_source(self, source_name: str) -> list[str]:
        ...

    @abstractmethod
    def get_data(self, key: tuple[str, str]) -> Any:
        ...

    @abstractmethod
    def get_dataset_names(self) -> set[tuple[str, str]]:
        ...

    @abstractmethod
    def get_source_names(self) -> set[str]:
        ...

    @classmethod
    @property
    def unit(cls):
        return cls._unit


class DataTypeManager:
    def __init__(self: Self):
        self._datatypemodels: dict[type[DataTypeModel], DataTypeModel] = {}

    def register_datatype(self, datatype: DataTypeModel):
        if type(datatype) in self._datatypemodels.keys():
            raise KeyError(f"Datatype of type {type(datatype)} already registered.")
        self._datatypemodels[type(datatype)] = datatype

    def get_types(self) -> set[type[DataTypeModel]]:
        return set(self._datatypemodels.keys())

    def get_model(self, type: type[DataTypeModel]) -> DataTypeModel:
        return self._datatypemodels[type]
