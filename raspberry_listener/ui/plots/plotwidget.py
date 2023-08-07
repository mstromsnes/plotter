from functools import partial, wraps
from typing import Self

import matplotlib
import plotstrategies
from datamodels import DataTypeModel
from matplotlib.ticker import FuncFormatter, NullFormatter
from plotmanager import PlotManager
from plotstrategies import PlotStrategy
from plotstrategies.axes import SingleAxesStrategy
from plotstrategies.color import ColorMapStrategy, CyclicColorStrategy
from plotstrategies.legend import ColorbarLegend, ExternalLegend, InternalLegend
from plotstrategies.tick import (
    clock_time_of_day_formatter,
    concise_date_formatter,
    flat_time_of_day_formatter,
    major_tickformatter,
    minor_tickformatter,
)
from PySide6 import QtWidgets
from ui.dataselector import DataSelector, SideBar, SideBarButtonType
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
        selector: DataSelector,
        rescale_plot: bool,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(rescale_plot, parent=parent)
        self.manager: PlotManager = None  # type: ignore
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(selector.widget())
        self.h_layout.addLayout(self.canvas_toolbar_layout, stretch=1)
        selector.data_toggled.connect(self.toggle_data)  # type: ignore
        self.setLayout(self.h_layout)

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
    def build(
        cls,
        model: DataTypeModel,
        plot_type: type[PlotStrategy],
    ) -> PlotWidget:
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
        selector = cls._build_checkbox_sidebar(model)
        lineplot_widget = PlotWidget(selector, rescale_plot=True)
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
            major_tick_formatter=partial(concise_date_formatter, model=model),
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
        selector = cls._build_checkbox_sidebar(model)
        histogram_widget = PlotWidget(selector, rescale_plot=True)
        axes = SingleAxesStrategy(
            histogram_widget.figure, lambda figure: figure.subplots(1)
        )
        color = CyclicColorStrategy(matplotlib.color_sequences["tab10"])  # type: ignore
        unit_symbol_formatter = FuncFormatter(lambda x, pos: f"{x}{model.unit.short}")
        unit_symbol_formatter.set_offset_string(model.unit.explanation)
        manager = PlotManager(
            histogram_widget,
            model,
            plotstrategies.HistogramPlot,
            axes,
            color,
            ExternalLegend(),
            major_tick_formatter=major_tickformatter(x_formatter=unit_symbol_formatter),
        )
        histogram_widget.set_manager(manager)
        histogram_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot().rescale_plot()
        )
        return histogram_widget

    @classmethod
    def _build_timeofday_widget(cls, model: DataTypeModel) -> PlotWidget:
        selector = cls._build_radiobutton_sidebar(model)
        timeofday_widget = PlotWidget(selector, rescale_plot=False)
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
            major_tick_formatter=clock_time_of_day_formatter,  # type: ignore
        )
        timeofday_widget.set_manager(manager)
        timeofday_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot()
        )
        return timeofday_widget

    @classmethod
    def _build_checkbox_sidebar(cls, model: DataTypeModel) -> SideBar:
        return cls._build_sidebar(model, QtWidgets.QCheckBox)

    @classmethod
    def _build_radiobutton_sidebar(cls, model: DataTypeModel) -> SideBar:
        return cls._build_sidebar(model, QtWidgets.QRadioButton)

    @classmethod
    def _build_sidebar(
        cls,
        model: DataTypeModel,
        button_type: SideBarButtonType,
    ) -> SideBar:
        return SideBar(model, button_type)
