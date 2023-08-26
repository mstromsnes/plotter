from functools import wraps

from datamodels import DataIdentifier, DataTypeModel
from plotstrategies import PlotStrategy
from plotstrategies.axes import AxesStrategy
from plotstrategies.color import ColorStrategy
from plotstrategies.legend import LegendStrategy
from plotstrategies.plotitem import PlotItem, PlotStatus
from ui.drawwidget import DrawWidget


class PlotManager:
    @staticmethod
    def draw(func):
        """Decorator for plotting functions. Prevents plotting if the canvas is not visible and if the widget has deactivated live plotting."""

        @wraps(func)
        def wrapper(self: "PlotManager", *args, **kwargs):
            if self.widget.plot_live and self.widget.isVisible():
                func(self, *args, **kwargs)
                if self.widget.rescale_plot:
                    self.rescale()
                self.widget.canvas.draw_idle()

        return wrapper

    def __init__(
        self,
        draw_widget: DrawWidget,
        model: DataTypeModel,
        plot_strategy: type[PlotStrategy],
        axes: AxesStrategy,
        color: ColorStrategy,
        legend: LegendStrategy,
    ):
        self.widget = draw_widget
        self.model = model
        self.plot_strategy = plot_strategy
        self.color = color
        self.legend = legend
        self.axes_strategy = axes
        self.model.source_updated.connect(self.source_updated)
        self.model.dataline_registered.connect(self.construct_plot_strategy)

        self.plots: dict[DataIdentifier, PlotItem] = {}
        self.construct_plot_strategies()

    def source_updated(self, source_name: str):
        data_names = self.model.get_data_name_from_source(source_name)
        plots = [DataIdentifier(source_name, data_name) for data_name in data_names]
        self.draw_plots(plots)

    def construct_plot_strategies(self):
        datasets = self.model.get_data_identifiers()
        for dataset in datasets:
            self.construct_plot_strategy(dataset)

    def construct_plot_strategy(self, dataset: DataIdentifier):
        constructed_strategy = self.plot_strategy(self.model, dataset)
        self.color.apply(constructed_strategy, dataset)
        self.plots[dataset] = PlotItem(
            dataset, constructed_strategy, PlotStatus.Disabled, self.axes_strategy
        )

    def rescale(self):
        for ax in self.axes_strategy:
            ax.relim()
            ax.autoscale()

    def add_plotting_strategy(self, dataset: DataIdentifier):
        self.plots[dataset].status = PlotStatus.Enabled
        self.plot()

    def remove_plotting_strategy(self, dataset: DataIdentifier):
        self.plots[dataset].status = PlotStatus.Disabled
        self.plot()

    @draw
    def draw_plots(self, plots: list[DataIdentifier]):
        drawn_plots = []
        for dataset in plots:
            if self.plots[dataset].visible:
                self.plots[dataset].draw_plot()
                drawn_plots.append(self.plots[dataset])
        self.legend(drawn_plots)

    def plot(self):
        datasets_to_plot = list(self.plots.keys())
        self.draw_plots(datasets_to_plot)
