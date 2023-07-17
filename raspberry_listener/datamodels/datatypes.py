from typing import Protocol, Any
from abc import ABC, abstractmethod
from plotstrategies import PlotStrategy


class DataSet_Fn(Protocol):
    def __call__(self) -> Any:
        ...


class DataTypeModel(ABC):
    def __init__(self):
        self._has_data = False

    def has_data(self):
        return self._has_data

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def register_data(self, name: str, dataset_fn: DataSet_Fn):
        ...

    @abstractmethod
    def get_source_name(self, name: str) -> str:
        ...

    @abstractmethod
    def get_data(self, name: str) -> DataSet_Fn:
        ...

    @abstractmethod
    def get_plots(self, name: str) -> list[PlotStrategy]:
        ...

    @abstractmethod
    def get_dataset_names(self) -> set[str]:
        ...

    @abstractmethod
    def get_plot(self, name: str, plot_type: type[PlotStrategy]) -> PlotStrategy:
        ...

    @abstractmethod
    def supported_plots(self) -> set[type[PlotStrategy]]:
        ...

