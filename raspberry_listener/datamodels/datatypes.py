from dataclasses import astuple, dataclass
from typing import Any, Callable, Protocol, Self

from PySide6 import QtCore


@dataclass(frozen=True)
class DataIdentifier:
    source: str
    data: str

    def __iter__(self):
        return iter(astuple(self))


class DataSet_Fn(Protocol):
    def __call__(self) -> Any:
        ...


@dataclass
class Unit:
    short: str
    long: str
    explanation: str


Observer = Callable[[DataIdentifier], None]


class DataTypeModel(QtCore.QObject):
    source_updated = QtCore.Signal(str)
    dataline_registered = QtCore.Signal(DataIdentifier)
    _unit: Unit

    def __init__(self: Self):
        super().__init__(None)

    def name(self) -> str:
        raise NotImplementedError

    @QtCore.Slot(str)
    def forward_source_updated(self, source_name: str):
        self.source_updated.emit(source_name)

    def register_data(self, dataset: DataIdentifier, dataset_fn: DataSet_Fn):
        raise NotImplementedError
        ...

    def get_data_name_from_source(self, source_name: str) -> list[str]:
        raise NotImplementedError

    def get_data(self, data_identifier: DataIdentifier) -> Any:
        raise NotImplementedError

    def get_data_identifiers(self) -> set[DataIdentifier]:
        raise NotImplementedError

    def get_source_names(self) -> set[str]:
        raise NotImplementedError

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
