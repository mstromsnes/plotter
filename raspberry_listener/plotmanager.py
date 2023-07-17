from ui.drawwidget import DrawWidget
from matplotlib.axes import Axes
from typing import Sequence, Hashable, Mapping, Any, Callable
from plotstrategies import PlotStrategy
from abc import ABC, abstractmethod
from functools import wraps
from collections import defaultdict
from matplotlib.axes import Axes
from matplotlib.artist import Artist
from sources import DataNotReadyException


class LayoutManager(ABC):
    @abstractmethod
    def add_axes(self) -> Axes:
        ...

    @abstractmethod
    def remove_axes(self):
        ...


class VerticalLayoutManager(LayoutManager):
    def __init__(self, widget: DrawWidget, plotmanager: "PlotManager"):
        self._widget = widget
        self._plotmanager = plotmanager
        self._axes: dict[Hashable, tuple[Axes, tuple[int, int, int]]] = {}

    def add_axes(self, key: Hashable):
        num_axes = len(self._plotmanager.axes)


class PlotManager(ABC):
    @staticmethod
    def draw(func):
        """Decorator for plotting functions. Prevents plotting if the canvas is not visible and if the widget has deactivated live plotting."""

        @wraps(func)
        def wrapper(self: "PlotManager", *args, **kwargs):
            if self.widget.plot_live and self.widget.isVisible():
                func(self, *args, **kwargs)
                if self.widget.rescale_plot:
                    self._rescale()
                self.widget.canvas.draw_idle()

        return wrapper

    def __init__(self, draw_widget: DrawWidget, title: str | None):
        self.widget = draw_widget
        self.set_title(title)

    def set_title(self, title: str | None):
        ...
        # self.title = title
        # if self.title is not None:
        #     self.widget.figure.suptitle(self.title)

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
    def plot(self, kwarg_supplier: Callable[[PlotStrategy], dict[str, Any]]):
        for ax in self.axes:
            for plot in self.plotting_strategies[ax]:
                try:
                    plot(ax, **kwarg_supplier(plot))
                except DataNotReadyException:
                    pass

    @abstractmethod
    def remove_plotting_strategy(self, *args, **kwargs):
        ...


class OneAxesPrStrategyPlotManager(PlotManager):
    """Creates a new axes for each plot"""

    def __init__(self, draw_widget: DrawWidget, title: str):
        super().__init__(draw_widget, title)
        self._axes: dict[PlotStrategy, Axes] = {}
        self._plotting_strategies: dict[Hashable, PlotStrategy] = {}
        self._plotting_kwargs: dict[PlotStrategy, dict[str, Any]] = {}

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
        self._plotting_kwargs[strategy] = kwargs
        self.plot()

    def remove_plotting_strategy(self, key: Hashable, *args, **kwargs):
        strategy = self._plotting_strategies[key]
        strategy.remove_artist()
        ax = self._axes[strategy]
        self.widget.remove_axes(ax)
        del self._plotting_strategies[key]
        del self._axes[strategy]
        self.plot()

    def plot(self):
        return super().plot(lambda plot: self._plotting_kwargs[plot])


class OneAxesPrSensorTypeManager(PlotManager):
    """Groups plots into axes determined by axes_key"""

    def __init__(self, widget: DrawWidget, title: str | None = None):
        super().__init__(widget, title)
        self._axes: dict[Hashable, Axes] = {}
        self._plotting_strategies: dict[Hashable, dict[Hashable, PlotStrategy]] = {}
        self._keyed_plotting_kwargs: dict[
            Hashable, dict[Hashable, dict[str, Any]]
        ] = defaultdict(lambda: defaultdict(dict))
        self._plotting_kwargs: dict[PlotStrategy, dict[str, Any]] = {}

    @property
    def axes(self):
        return self._axes.values()

    @property
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        return {
            ax: list(self._plotting_strategies[key].values())
            for key, ax in self._axes.items()
        }

    def plot(self):
        return super().plot(lambda plot: self._plotting_kwargs[plot])

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
                )
            except GeneratorExit:
                return
        self._plotting_strategies[axes_key][strategy_key] = strategy
        self.update_plotting_kwargs(axes_key, strategy_key, **kwargs)
        self.plot()

    def set_plotting_kwargs(self, axes_key: Hashable, strategy_key: Hashable, **kwargs):
        self._keyed_plotting_kwargs[axes_key][strategy_key] = kwargs
        strategy = self._plotting_strategies[axes_key][strategy_key]
        self._plotting_kwargs[strategy] = kwargs

    def update_plotting_kwargs(
        self, axes_key: Hashable, strategy_key: Hashable, **kwargs
    ):
        self._keyed_plotting_kwargs[axes_key][strategy_key].update(**kwargs)
        strategy = self._plotting_strategies[axes_key][strategy_key]
        self._plotting_kwargs[strategy] = kwargs

    def remove_plotting_strategy(
        self, axes_key: Hashable, strategy_key: Hashable, *args, **kwargs
    ):
        if axes_key in self._axes:
            # If axes exist, delete the strategy from that axes
            strategy = self._plotting_strategies[axes_key][strategy_key]
            strategy.remove_artist()
            del self._plotting_strategies[axes_key][strategy_key]
            del self._plotting_kwargs[strategy]
        if not self._plotting_strategies[axes_key]:
            # If dict of strategies for that axes is (now) empty, remove the axes completely
            ax = self._axes[axes_key]
            self.widget.remove_axes(ax)
            del self._axes[axes_key]
            del self._plotting_strategies[axes_key]

        self.plot()

    def _add_axes(self, key: Hashable, *args, **kwargs):
        if key in self.axes:
            raise KeyError(f"Axes already exist for this key {key}")
        ax = self.widget.add_axes(*args, **kwargs)
        self._axes[key] = ax
        self._plotting_strategies[key] = dict()


class OneAxesPlotManager(PlotManager):
    """Draws all plots in a single axes."""

    def __init__(self, widget: DrawWidget, title: str | None = None):
        super().__init__(widget, title)
        self._axes: Axes | None = None
        self._plotting_strategies: set[PlotStrategy] = set()
        self._plotting_kwargs: dict[PlotStrategy, dict[str, Any]] = defaultdict(dict)

    @property
    def axes(self):
        return [self._axes] if self._axes is not None else []

    @property
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        return (
            {self._axes: list(self._plotting_strategies)}
            if self._axes is not None
            else {}
        )

    def plot(self):
        return super().plot(lambda plot: self._plotting_kwargs[plot])

    def add_plotting_strategy(self, strategy: PlotStrategy, *args, **kwargs):
        if self._axes is None:
            self._axes = self.widget.add_axes()
        self._plotting_strategies.add(strategy)
        self.plot()

    def remove_plotting_strategy(self, strategy: PlotStrategy, *args, **kwargs):
        strategy.remove_artist()
        self._plotting_strategies.remove(strategy)
        if not self._plotting_strategies:
            self.widget.remove_axes(self._axes)
            self._axes = None
        self.plot()

    def update_plotting_kwargs(self, strategy: PlotStrategy, **kwargs):
        self._plotting_kwargs[strategy] = kwargs

    def set_plotting_kwargs(self, strategy: PlotStrategy, **kwargs):
        self._plotting_kwargs[strategy] = kwargs
