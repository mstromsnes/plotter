from abc import ABC, abstractmethod
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Hashable, Mapping, Sequence

from datamodels import DataTypeModel
from matplotlib.axes import Axes
from plotstrategies import PlotStrategy
from sources import DataNotReadyException
from ui.drawwidget import DrawWidget


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

    def __init__(
        self,
        draw_widget: DrawWidget,
        model: DataTypeModel,
        subplot_kwargs: dict = {},
    ):
        self.widget = draw_widget
        self.model = model
        self.subplot_kwargs = subplot_kwargs

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
        kwarg_supplier = self.get_kwarg_supplier()
        for ax in self.axes:
            for plot in self.plotting_strategies[ax]:
                try:
                    plot(ax, **kwarg_supplier(plot))
                except DataNotReadyException:
                    pass
            ax.legend()

    @abstractmethod
    def get_kwarg_supplier(self) -> Callable[[PlotStrategy], dict[str, Any]]:
        ...

    @abstractmethod
    def remove_plotting_strategy(self, *args, **kwargs):
        ...


class OneAxesPlotManager(PlotManager):
    """Draws all plots in a single axes."""

    def __init__(
        self,
        widget: DrawWidget,
        model: DataTypeModel,
        subplot_kwargs: dict = {},
    ):
        super().__init__(widget, model, subplot_kwargs)
        self._axes: Axes | None = None
        self._plotting_strategies: dict[str, PlotStrategy] = {}
        self._enabled_strategy_labels: dict[str, bool] = {}
        self._plotting_kwargs: dict[PlotStrategy, dict[str, Any]] = defaultdict(dict)

    @property
    def axes(self):
        return [self._axes] if self._axes is not None else []

    @property
    def plotting_strategies(self) -> Mapping[Axes, Sequence[PlotStrategy]]:
        if self._axes is not None:
            return {
                self._axes: [
                    plot_strategy
                    for k, plot_strategy in self._plotting_strategies.items()
                    if self._enabled_strategy_labels[k]
                ]
            }
        else:
            return {}

    def get_kwarg_supplier(self) -> Callable[[PlotStrategy], dict[str, Any]]:
        return lambda plot: self._plotting_kwargs[plot]

    def _create_plot(self, label: str, plot_type: type[PlotStrategy], *args, **kwargs):
        strategy = plot_type(self.model, label)
        self._plotting_strategies[label] = strategy

    def _enable_strategy(self, label):
        self._enabled_strategy_labels[label] = True

    def _disable_strategy(self, label: str):
        self._enabled_strategy_labels[label] = False

    def add_plotting_strategy(
        self, label: str, plot_type: type[PlotStrategy], *args, **kwargs
    ):
        if self._axes is None:
            self._axes = self.widget.add_axes(**self.subplot_kwargs)
        if not label in self._plotting_strategies.keys():
            self._create_plot(label, plot_type, *args, **kwargs)
        self._enable_strategy(label)
        self.plot()

    def remove_plotting_strategy(self, label: str, *args, **kwargs):
        strategy = self._plotting_strategies[label]
        strategy.remove_artist()
        self._disable_strategy(label)
        if not any(self._enabled_strategy_labels.values()):
            self.widget.remove_axes(self._axes)
            self._axes = None
        self.plot()

    def update_plotting_kwargs(self, strategy: PlotStrategy, **kwargs):
        self._plotting_kwargs[strategy] = kwargs

    def set_plotting_kwargs(self, strategy: PlotStrategy, **kwargs):
        self._plotting_kwargs[strategy] = kwargs
