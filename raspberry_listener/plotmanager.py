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

    @staticmethod
    def _remove_artist(strategy: PlotStrategy):
        try:
            artist = strategy.artist
            if isinstance(artist, Sequence):
                [art.remove() for art in artist]
            elif isinstance(artist, Artist):
                artist.remove()
        except AttributeError:
            pass

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
    """Creates a new axes for each plot"""

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

    def add_plotting_strategy(
        self, strategy: PlotStrategy, key: Hashable, *args, **kwargs
    ):
        ax = self.widget.add_axes()
        self._axes[strategy] = ax
        self._plotting_strategies[key] = strategy
        self.plot()

    def remove_plotting_strategy(self, key: Hashable, *args, **kwargs):
        strategy = self._plotting_strategies[key]
        self._remove_artist(strategy)
        ax = self._axes[strategy]
        self.widget.remove_axes(ax)
        del self._plotting_strategies[key]
        del self._axes[strategy]
        self.plot()


class OneAxesPrSensorTypeManager(PlotManager):
    """Groups plots into axes determined by axes_key"""

    def __init__(self, widget: DrawWidget, title: str | None = None):
        super().__init__(widget, title)
        self._axes: dict[Hashable, Axes] = {}
        self._plotting_strategies: dict[Hashable, dict[Hashable, PlotStrategy]] = {}
        self.subplots = self._subplot_generator()

    @property
    def axes(self):
        return self._axes.values()

    @property
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        return {
            ax: list(self._plotting_strategies[key].values())
            for key, ax in self._axes.items()
        }

    def add_plotting_strategy(
        self,
        strategy: PlotStrategy,
        axes_key: Hashable,
        strategy_key: Hashable,
        *args,
        **kwargs,
    ):
        if axes_key not in self._axes:
            try:
                self._add_axes(
                    axes_key,
                    next(self.subplots),
                    subplot=True,
                    title=axes_key.value.capitalize(),
                )
            except GeneratorExit:
                return
        self._plotting_strategies[axes_key][strategy_key] = strategy
        self.plot()

    def remove_plotting_strategy(
        self, axes_key: Hashable, strategy_key: Hashable, *args, **kwargs
    ):
        if axes_key in self._axes:
            # If axes exist, delete the strategy from that axes
            strategy = self._plotting_strategies[axes_key][strategy_key]
            self._remove_artist(strategy)
            del self._plotting_strategies[axes_key][strategy_key]
        if not self._plotting_strategies[axes_key]:
            # If dict of strategies for that axes is (now) empty, remove the axes completely
            ax = self._axes[axes_key]
            self.widget.remove_axes(ax)
            del self._axes[axes_key]
            del self._plotting_strategies[axes_key]

        self.plot()

    def _add_axes(self, key: Hashable, *args, subplot=True, **kwargs):
        if key in self.axes:
            raise KeyError(f"Axes already exist for this key {key}")
        ax = self.widget.add_axes(*args, subplot=subplot, **kwargs)
        self._axes[key] = ax
        self._plotting_strategies[key] = dict()

    def _subplot_generator(self):
        while True:
            yield 211
            yield 212
