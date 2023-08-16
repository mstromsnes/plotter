from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import cycle
from typing import Sequence

from datamodels import DataIdentifier
from matplotlib.colors import Colormap

from ..plotstrategy import (
    Color,
    ColormapPlotStrategy,
    PlotStrategy,
    SingleColorPlotStrategy,
)


class ColorStrategy(ABC):
    @abstractmethod
    def get_color(self, dataset: DataIdentifier) -> Color | Sequence[Color] | Colormap:
        pass

    @abstractmethod
    def apply(self, plot: PlotStrategy, dataset: DataIdentifier):
        pass


class ColorMapStrategy(ColorStrategy):
    def __init__(self, colormap: Colormap):
        self._cm = colormap

    def get_color(self, dataset: DataIdentifier) -> Colormap:
        return self._cm

    def apply(self, plot: PlotStrategy, dataset: DataIdentifier):
        assert isinstance(
            plot, ColormapPlotStrategy
        ), "Passed an incompatible PlotStrategy type"
        plot.set_colormap(self._cm)


class CyclicColorStrategy(ColorStrategy):
    def __init__(self, color_sequence: Sequence[Color]):
        self._dataset_to_color: dict[DataIdentifier, Color] = dict()
        self._colorset = cycle(color_sequence)

    def get_color(self, dataset: DataIdentifier) -> Color:
        try:
            return self._dataset_to_color[dataset]
        except KeyError:
            self._dataset_to_color[dataset] = next(self._colorset)
            return self._dataset_to_color[dataset]

    def apply(self, plot: PlotStrategy, dataset: DataIdentifier):
        assert isinstance(
            plot, SingleColorPlotStrategy
        ), "Passed an incompatible PlotStrategy type"
        plot.set_color(self.get_color(dataset))
