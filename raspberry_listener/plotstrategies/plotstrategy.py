from typing import Sequence
from abc import ABC, abstractmethod
from matplotlib.axes import Axes
from matplotlib.artist import Artist

class PlotNotReadyException(Exception):
    ...


class PlotStrategy(ABC):
    def __init__(
        self,
        model: DataTypeModel,
        label: str,
    ):
        self.model = model
        self.label = label

    @abstractmethod
    def __call__(self, ax: Axes, **kwargs):
        """A method that plots something from self on axes ax."""
        ...

    @property
    @abstractmethod
    def artist(self) -> Artist | Sequence[Artist]:
        ...

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @abstractmethod
    def remove_artist(self):
        ...

    @abstractmethod
    def set_tick_formatter(self, ax: Axes):
        ...
