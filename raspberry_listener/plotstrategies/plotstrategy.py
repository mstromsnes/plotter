from typing import Sequence
from abc import ABC, abstractmethod
from matplotlib.axes import Axes
from matplotlib.artist import Artist
from datamodels import DataTypeModel


class PlotStrategy(ABC):
    @abstractmethod
    def __init__(
        self,
        model: DataTypeModel,
        label: str | None = None,
    ):
        ...

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
