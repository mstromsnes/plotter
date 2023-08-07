from abc import ABC, abstractmethod
from typing import Protocol, Sequence

from datamodels import DataTypeModel
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize

from .color import Color


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

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @abstractmethod
    def remove_artist(self):
        ...


    @abstractmethod
    def set_colorsource(self, colors: Sequence[Color] | Colormap | Color):
        ...


class ColormapStrategy(Protocol):
    def get_colormap(self) -> Colormap:
        ...

    def get_normalizer(self) -> Normalize:
        ...
