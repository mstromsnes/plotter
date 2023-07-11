from abc import ABC, abstractmethod
from typing import Type

import pandas as pd
from plotstrategies.plotstrategy import PlotStrategy

DataSetKeys = tuple

# This type is intended to map the types of plots a datamodel supports to the keys that can offer datasets that supports those plots.
ModelDataSetReturnType = dict[Type[PlotStrategy], list[DataSetKeys]]


class DataSetModel(ABC):
    """This is a model for how a dataframe should be accessed to acquire sensible datasets.
    It specifies a list of logical groupings of data. This might be Temperature and Humidity, or Speed, Heart Rate and Position
    """

    @abstractmethod
    def groups(self) -> list[str]:
        """This returns the names of the tabs the dataframe should create"""
        ...

    @abstractmethod
    def datasets(self, name: str) -> ModelDataSetReturnType:
        """Given the name of a group, this returns a mapping of supported plot strategies to individual datasets."""
        ...


class FrameHandler(ABC):
    """This is the underlying handler for a source of data. It controls data updates to a dataframe, and provides a getter for that dataframe for read-purposes"""

    @property
    @abstractmethod
    def dataframe(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def initial_load(self) -> None:
        ...

    @abstractmethod
    def update_data(self) -> None:
        ...

    @abstractmethod
    def model(self) -> DataSetModel:
        ...


class DataNotReadyException(Exception):
    ...
