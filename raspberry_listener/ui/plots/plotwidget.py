import matplotlib
import plotstrategies
from datamodels import DataTypeModel
from plotmanager import OneAxesPlotManager, PlotManager
from plotstrategies import PlotStrategy
from plotstrategies.color import ColorMapStrategy, ColorStrategy, CyclicColorStrategy
from plotstrategies.legend import (
    ColorbarLegend,
    ExternalLegend,
    InternalLegend,
    LegendStrategy,
)
from PySide6 import QtWidgets
from ui.drawwidget import DrawWidget, NavBarBuilder


class PlotWidget(DrawWidget):
    def __init__(
        self,
        model: DataTypeModel,
        manager_type: type[PlotManager],
        color_manager: ColorStrategy,
        legend_strategy: LegendStrategy,
        plot_type: type[PlotStrategy],
        rescale_plot: bool,
        subplot_kwargs: dict = {},
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(rescale_plot, parent=parent)
        self.model = model
        self.manager = manager_type(
            self, model, color_manager, legend_strategy, subplot_kwargs
        )
        self.plot_type = plot_type

    def toggle_data(self, label, checked):
        if checked:
            self.manager.add_plotting_strategy(label, self.plot_type)
        else:
            self.manager.remove_plotting_strategy(label)

    def plot(self):
        self.manager.plot()


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
            case plotstrategies.FlatTimeOfDay:
                return cls._build_flat_timeofday_widget(model)
            case _:
                raise NotImplementedError

    @classmethod
    def _build_lineplot_widget(cls, model: DataTypeModel) -> PlotWidget:
        lineplot_widget = PlotWidget(
            model,
            OneAxesPlotManager,
            CyclicColorStrategy(matplotlib.color_sequences["tab10"]),  # type: ignore
            ExternalLegend(),
            plotstrategies.LinePlot,
            rescale_plot=True,
        )
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
        histogram_widget = PlotWidget(
            model,
            OneAxesPlotManager,
            CyclicColorStrategy(matplotlib.color_sequences["tab10"]),  # type: ignore
            ExternalLegend(),
            plotstrategies.HistogramPlot,
            rescale_plot=True,
        )
        histogram_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot().rescale_plot()
        )
        return histogram_widget

    @classmethod
    def _build_timeofday_widget(cls, model: DataTypeModel) -> PlotWidget:
        timeofday_widget = PlotWidget(
            model,
            OneAxesPlotManager,
            ColorMapStrategy(matplotlib.colormaps["turbo"]),  # type: ignore
            ColorbarLegend(),
            plotstrategies.TimeOfDayPlot,
            rescale_plot=False,
            subplot_kwargs={"projection": "polar"},
        )
        timeofday_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot()
        )
        return timeofday_widget

    @classmethod
    def _build_flat_timeofday_widget(cls, model: DataTypeModel) -> PlotWidget:
        timeofday_widget = PlotWidget(
            model,
            OneAxesPlotManager,
            ColorMapStrategy(matplotlib.colormaps["turbo"]),  # type: ignore
            ColorbarLegend(),
            plotstrategies.FlatTimeOfDay,
            rescale_plot=False,
        )
        timeofday_widget.add_navigation_bar(
            NavBarBuilder().navigation_toolbar().freeze_plot()
        )
        return timeofday_widget
