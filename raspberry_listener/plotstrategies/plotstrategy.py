from abc import ABC, abstractmethod

from datamodels import DataIdentifier, DataTypeModel
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize

Color = tuple[float, float, float] | str


class PlotNotReadyException(Exception):
    ...


class PlotStrategy(ABC):
    def __init__(self, model: DataTypeModel, dataset: DataIdentifier):
        self.model = model
        self.dataset = dataset

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


class SingleColorPlotStrategy(PlotStrategy):
    @abstractmethod
    def set_color(self, color: Color):
        ...


class ColormapPlotStrategy(PlotStrategy):
    @abstractmethod
    def set_colormap(self, colormap: Colormap) -> None:
        ...

    @abstractmethod
    def get_colormap(self) -> Colormap:
        ...

    @abstractmethod
    def get_normalizer(self) -> Normalize:
        ...
