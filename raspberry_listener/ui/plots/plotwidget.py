from functools import wraps
from typing import Self

import matplotlib
import plotstrategies
from datamodels import DataTypeModel
from plotmanager import PlotManager
from plotstrategies import PlotStrategy
from plotstrategies.axes import SingleAxesStrategy
from plotstrategies.color import ColorMapStrategy, CyclicColorStrategy
from plotstrategies.legend import ColorbarLegend, ExternalLegend, InternalLegend
from PySide6 import QtWidgets
from ui.drawwidget import DrawWidget, NavBarBuilder


class ManagerNotSetException(Exception):
    ...


class PlotWidget(DrawWidget):
    @staticmethod
    def ensure_manager(fn):
        @wraps(fn)
        def wrapper(self: Self, *args, **kwargs):
            try:
                assert self.manager is not None
                fn(self, *args, **kwargs)
            except AssertionError:
                raise ManagerNotSetException

        return wrapper

    def __init__(
        self,
        rescale_plot: bool,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(rescale_plot, parent=parent)
        self.manager: PlotManager = None  # type: ignore

    @ensure_manager
    def toggle_data(self, label, checked):
        if checked:
            self.manager.add_plotting_strategy(label)
        else:
            self.manager.remove_plotting_strategy(label)

    @ensure_manager
    def plot(self):
        self.manager.plot()

    def set_manager(self, manager: PlotManager):
        self.manager = manager


class PlotWidgetFactory:
    @classmethod
    def build(cls, plot_type: type[PlotStrategy], model: DataTypeModel) -> PlotWidget:
        match plot_type:
            case plotstrategies.LinePlot:
                return cls._build_lineplot_widget(model)
            case plotstrategies.HistogramPlot:
                return cls._build_histogram_widget(model)
            case plotstrategies.TimeOfDayPlot:
                return cls._build_timeofday_widget(model)
            case _:
                raise NotImplementedError

    @classmethod
    def _build_lineplot_widget(cls, model: DataTypeModel) -> PlotWidget:
        lineplot_widget = PlotWidget(rescale_plot=True)
        axes = SingleAxesStrategy(
            lineplot_widget.figure, lambda figure: figure.subplots(1)
        )
        color = CyclicColorStrategy(matplotlib.color_sequences["tab10"])  # type: ignore
        manager = PlotManager(
            lineplot_widget,
            model,
            plotstrategies.LinePlot,
            axes,
            color,
            ExternalLegend(),
        )
        lineplot_widget.set_manager(manager)
        lineplot_widget.add_navigation_bar(
            NavBarBuilder()
            .navigation_toolbar()
            .freeze_plot()
            .simplify_plot()
            .rescale_plot()
        )
        return lineplot_widget

    @classmethod
    def _build_histogram_widget(cls, model: DataTypeModel) -> PlotWidget:
        histogram_widget = PlotWidget(rescale_plot=True)
        axes = SingleAxesStrategy(
            histogram_widget.figure, lambda figure: figure.subplots(1)
        )
        color = CyclicColorStrategy(matplotlib.color_sequences["tab10"])  # type: ignore
        manager = PlotManager(
            histogram_widget,
            model,
            plotstrategies.HistogramPlot,
            axes,
            color,
            ExternalLegend(),
        )
        histogram_widget.set_manager(manager)
        histogram_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot().rescale_plot()
        )
        return histogram_widget

    @classmethod
    def _build_timeofday_widget(cls, model: DataTypeModel) -> PlotWidget:
        timeofday_widget = PlotWidget(rescale_plot=False)
        axes = SingleAxesStrategy(
            timeofday_widget.figure,
            lambda figure: figure.subplots(1, subplot_kw={"projection": "polar"}),
        )
        color = ColorMapStrategy(matplotlib.colormaps["turbo"])  # type: ignore
        manager = PlotManager(
            timeofday_widget,
            model,
            plotstrategies.TimeOfDayPlot,
            axes,
            color,
            ColorbarLegend(),
        )
        timeofday_widget.set_manager(manager)
        timeofday_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot()
        )
        return timeofday_widget
