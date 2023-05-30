from drawwidget import DrawWidget
from matplotlib.axes import Axes
from typing import Sequence, Hashable, Mapping
from plotstrategies import PlotStrategy
from abc import ABC, abstractmethod
from functools import wraps
from matplotlib.axes import Axes
from matplotlib.artist import Artist


class PlotManager(ABC):
    @staticmethod
    def draw(func):
        """Decorator for plotting functions. Prevents plotting if the canvas is not visible and if the widget has deactivated live plotting."""

        @wraps(func)
        def wrapper(self: "PlotManager", *args, **kwargs):
            if self.widget.plot_live and self.widget.canvas.isVisible():
                func(self, *args, **kwargs)
                if self.widget.rescale_plot:
                    self._rescale()
                self.widget.canvas.draw_idle()

        return wrapper

    def __init__(self, draw_widget: DrawWidget, title: str | None):
        self.widget = draw_widget
        self.set_title(title)

    def set_title(self, title: str | None):
        self.title = title
        if self.title is not None:
            self.widget.figure.suptitle(self.title)

    def _rescale(self):
        for ax in self.axes:
            ax.relim()
            ax.autoscale()

    @property
    @abstractmethod
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        ...

    @property
    @abstractmethod
    def axes(self) -> Sequence[Axes]:
        ...

    @abstractmethod
    def add_plotting_strategy(self, strategy: PlotStrategy, *args, **kwargs):
        ...

    @draw
    def plot(self):
        for ax in self.axes:
            for plot in self.plotting_strategies[ax]:
                plot(ax)

    def update_plot(self):
        self.plot()

    @abstractmethod
    def remove_plotting_strategy(self, *args, **kwargs):
        ...


class OneAxesPrStrategyPlotManager(PlotManager):
    def __init__(self, draw_widget: DrawWidget, title: str):
        super().__init__(draw_widget, title)
        self._axes: dict[PlotStrategy, Axes] = {}
        self._plotting_strategies: dict[Hashable, PlotStrategy] = {}

    @property
    def axes(self):
        return self._axes.values()

    @property
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        return {ax: [strategy] for strategy, ax in self._axes.items()}

    def add_plotting_strategy(self, strategy: PlotStrategy, key: Hashable):
        ax = self.widget.add_axes()
        self._axes[strategy] = ax
        self._plotting_strategies[key] = strategy
        self.plot()

    def remove_plotting_strategy(self, key: Hashable):
        strategy = self._plotting_strategies[key]
        ax = self._axes[strategy]
        self.widget.remove_axes(ax)
        del self._plotting_strategies[key]
        del self._axes[strategy]
        self.plot()

