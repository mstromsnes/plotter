from abc import ABC, abstractmethod
from itertools import cycle
from typing import Sequence

from matplotlib.colors import Colormap

from ..plotstrategy import (
    Color,
    ColormapPlotStrategy,
    PlotStrategy,
    SingleColorPlotStrategy,
)


class ColorStrategy(ABC):
    @abstractmethod
    def get_color(self, key: tuple[str, str]) -> Color | Sequence[Color] | Colormap:
        pass

    @abstractmethod
    def apply(self, plot: PlotStrategy, key: tuple[str, str]):
        pass


class ColorMapStrategy(ColorStrategy):
    def __init__(self, colormap: Colormap):
        self._cm = colormap

    def get_color(self, key: tuple[str, str]) -> Colormap:
        return self._cm

    def apply(self, plot: PlotStrategy, key: tuple[str, str]):
        assert isinstance(
            plot, ColormapPlotStrategy
        ), "Passed an incompatible PlotStrategy type"
        plot.set_colormap(self._cm)


class CyclicColorStrategy(ColorStrategy):
    def __init__(self, color_sequence: Sequence[Color]):
        self._dataset_to_color: dict[tuple[str, str], Color] = {}
        self._colorset = cycle(color_sequence)

    def get_color(self, key: tuple[str, str]) -> Color:
        try:
            return self._dataset_to_color[key]
        except KeyError:
            self._dataset_to_color[key] = next(self._colorset)
            return self._dataset_to_color[key]

    def apply(self, plot: PlotStrategy, key: tuple[str, str]):
        assert isinstance(
            plot, SingleColorPlotStrategy
        ), "Passed an incompatible PlotStrategy type"
        plot.set_color(self.get_color(key))
