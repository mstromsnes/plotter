from functools import partial

import matplotlib
import plotstrategies
from datamodels import DataTypeModel
from matplotlib.ticker import FuncFormatter
from plotmanager import PlotManager
from plotstrategies.axes import (
    HorizontalOneSubfigureAxesPrPlotStrategy,
    SingleAxesStrategy,
    SingleAxesSubFigureStrategy,
)
from plotstrategies.color import ColorMapStrategy, CyclicColorStrategy
from plotstrategies.legend import ColorbarLegend, ExternalLegend, InternalLegend
from plotstrategies.tick import (
    TickStrategy,
    clock_time_of_day_formatter,
    concise_date_formatter,
    flat_time_of_day_formatter,
    major_tickformatter,
    minor_tickformatter,
)
from PySide6 import QtWidgets
from ui.dataselector import SideBar, SideBarButtonType
from ui.drawwidget import NavBarBuilder
from ui.plots import PlotWidget


def build_timeseries_widgets(
    model: DataTypeModel,
) -> dict[str, PlotWidget]:
    return {
        "Line": build_lineplot_widget(model),
        "Histogram": build_histogram_widget(model),
        "Clock Time of Day": build_clock_timeofday_widget(model),
        "Flat Time of Day": build_flat_timeofday_widget(model),
    }


def build_lineplot_widget(model: DataTypeModel) -> PlotWidget:
    selector = build_checkbox_sidebar(model)
    lineplot_widget = PlotWidget(selector, rescale_plot=True)
    axes = SingleAxesSubFigureStrategy(
        lineplot_widget.figure, major_tick=partial(concise_date_formatter, model=model)
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


def build_histogram_widget(model: DataTypeModel) -> PlotWidget:
    selector = build_checkbox_sidebar(model)
    histogram_widget = PlotWidget(selector, rescale_plot=True)
    color = CyclicColorStrategy(matplotlib.color_sequences["tab10"])  # type: ignore
    unit_symbol_formatter = FuncFormatter(lambda x, pos: f"{x}{model.unit.short}")
    unit_symbol_formatter.set_offset_string(model.unit.explanation)
    axes = SingleAxesStrategy(histogram_widget.figure, major_tick=unit_symbol_formatter)
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


def build_timeofday_widget(
    model: DataTypeModel, subplot_kw: dict, tick_formatter: TickStrategy
) -> PlotWidget:
    selector = build_checkbox_sidebar(model)
    timeofday_widget = PlotWidget(selector, rescale_plot=False)
    axes = HorizontalOneSubfigureAxesPrPlotStrategy(
        timeofday_widget.figure, major_tick=tick_formatter, subplot_kw=subplot_kw
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


def build_clock_timeofday_widget(model) -> PlotWidget:
    subplot_kw = {"projection": "polar"}
    tick_strategy = clock_time_of_day_formatter
    return build_timeofday_widget(model, subplot_kw, tick_strategy)


def build_flat_timeofday_widget(model) -> PlotWidget:
    tick_strategy = flat_time_of_day_formatter
    return build_timeofday_widget(model, {}, tick_strategy)


def build_checkbox_sidebar(model: DataTypeModel) -> SideBar:
    return build_sidebar(model, QtWidgets.QCheckBox)


def build_radiobutton_sidebar(model: DataTypeModel) -> SideBar:
    return build_sidebar(model, QtWidgets.QRadioButton)


def build_sidebar(
    model: DataTypeModel,
    button_type: SideBarButtonType,
) -> SideBar:
    return SideBar(model, button_type)
