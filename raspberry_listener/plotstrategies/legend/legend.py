from abc import ABC, abstractmethod
from typing import Sequence

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.legend import Legend

from raspberry_listener.plotstrategies.plotstrategy import ColormapStrategy

from ..plotstrategy import ColormapStrategy, PlotNotReadyException, PlotStrategy


class LegendStrategy(ABC):
    @abstractmethod
    def __call__(
        self,
        ax: Axes,
        fig: Figure,
        strategies: Sequence[ColormapStrategy] | Sequence[PlotStrategy],
    ):
        ...

    @abstractmethod
    def remove_legend(self):
        ...


class InternalLegend(LegendStrategy):
    def __init__(self) -> None:
        self.legend: Legend | None = None

    def __call__(self, ax: Axes, fig: Figure, strategies):
        self.remove_legend()
        self.legend = ax.legend()

    def remove_legend(self):
        if self.legend is None:
            return
        self.legend.remove()
        self.legend = None


class ExternalLegend(LegendStrategy):
    def __init__(self) -> None:
        self.legend: Legend | None = None

    def __call__(self, ax: Axes, fig: Figure, strategies):
        self.remove_legend()
        self.legend = fig.legend()

    def remove_legend(self):
        if self.legend is None:
            return
        self.legend.remove()
        self.legend = None


class ColorbarLegend(LegendStrategy):
    def __init__(self):
        self.colorbar: Colorbar | None = None

    def __call__(self, ax: Axes, fig: Figure, strategies: Sequence[ColormapStrategy]):
        # Only draw the colorbar for the last strategy. We don't really support multiple strategies.
        strategy = strategies[-1]
        try:
            norm = strategy.get_normalizer()
            cmap = strategy.get_colormap()
            mappable = ScalarMappable(norm, cmap)
        except PlotNotReadyException:
            return
        if self.colorbar is None:
            print("CREATE")
            self.colorbar = fig.colorbar(mappable)
        else:
            self.colorbar.update_normal(mappable)

    def remove_legend(self):
        print("REMOVE")
        if self.colorbar is None:
            return
        self.colorbar.update_normal(ScalarMappable(Normalize(0, 1), "Greys"))
