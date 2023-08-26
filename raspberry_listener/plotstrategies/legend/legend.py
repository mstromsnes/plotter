from abc import ABC, abstractmethod
from typing import Self

from datamodels import DataIdentifier
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.legend import Legend

from ..plotitem import PlotItem, PlotStatus
from ..plotstrategy import ColormapPlotStrategy, PlotNotReadyException


class LegendStrategy(ABC):
    @abstractmethod
    def __call__(self, plot_items: list[PlotItem]):
        ...


class InternalLegend(LegendStrategy):
    def __init__(self) -> None:
        self.legends: dict[Axes, Legend] = {}

    def __call__(self, plot_items: list[PlotItem]):
        unique_axes = {
            plot.ax for plot in plot_items if plot.status != PlotStatus.Disabled
        }
        for ax in unique_axes:
            self.remove_legend(ax)
        self.legends = {ax: ax.legend() for ax in unique_axes}

    def remove_legend(self, ax: Axes):
        try:
            self.legends[ax].remove()
        except KeyError:
            pass


class ExternalLegend(LegendStrategy):
    def __init__(self) -> None:
        self.legends: dict[Figure, Legend] = {}

    def __call__(self, plot_items: list[PlotItem]):
        if not plot_items:
            return
        fig = None
        for plot in plot_items:
            if plot.visible:
                fig = plot.figure
                self.remove_legend(fig)
                self.legends[fig] = fig.legend()

    def remove_legend(self, fig: Figure):
        try:
            self.legends[fig].remove()
            del self.legends[fig]
        except KeyError:
            pass


class ColorbarLegend(LegendStrategy):
    def __init__(self: Self):
        self.colorbars: dict[DataIdentifier, Colorbar] = {}

    def __call__(self, plot_items: list[PlotItem]):
        for plot in plot_items:
            self.draw_legend(plot)
            self.set_title(plot)

    def draw_legend(self, plot_item: PlotItem):
        ax = plot_item.ax
        strategy = plot_item.plot_strategy
        dataset = plot_item.identifier
        fig = ax.figure
        assert isinstance(
            strategy, ColormapPlotStrategy
        ), "Passed an incompatible PlotStrategy type"
        try:
            norm = strategy.get_normalizer()
            cmap = strategy.get_colormap()
            mappable = ScalarMappable(norm, cmap)
        except PlotNotReadyException:
            return
        colorbar = self.colorbars.get(dataset)
        if colorbar is None:
            self.colorbars[dataset] = fig.colorbar(mappable, ax=ax)
            self.colorbars[dataset].ax.set_label(f"Colorbar: {str(dataset)}")
        else:
            if colorbar.ax in fig.axes:
                colorbar.update_normal(mappable)
            else:
                try:
                    colorbar.remove()
                except AttributeError:
                    pass
                self.colorbars[dataset] = fig.colorbar(mappable, ax=ax)

    def set_title(self, plot_item: PlotItem):
        fig = plot_item.ax.figure
        fig.suptitle(str(plot_item.identifier))

    def remove_legend(self):
        for colorbar in self.colorbars.values():
            colorbar.update_normal(ScalarMappable(Normalize(0, 1), "Greys"))
