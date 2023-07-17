from abc import ABC, abstractmethod

import pandas as pd


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


class DataNotReadyException(Exception):
    ...
