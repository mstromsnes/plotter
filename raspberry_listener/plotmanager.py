from functools import wraps
from typing import Sequence

from datamodels import DataTypeModel
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from plotstrategies import PlotStrategy
from plotstrategies.axes import AxesStrategy
from plotstrategies.color import ColorStrategy
from plotstrategies.legend import LegendStrategy
from plotstrategies.plotcontainer.plotcontainer import PlotContainer
from sources import DataNotReadyException
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
                    self._rescale()
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
        self.axes = axes
        self.color = color
        self.legend = legend
        self.plots = PlotContainer()

    def _rescale(self):
        for ax in self.axes:
            ax.relim()
            ax.autoscale()

    def add_plotting_strategy(self, label: str):
        if not self.plots.plot_already_constructed(label):
            plot = self.plot_strategy(self.model, label)
            plot.set_colorsource(self.color.get_color(label))
            ax = self.axes.from_label(label)
            self.plots.add_plot_strategy(label, ax, plot)
        self.plots.enable_plot(label)
        self.plot()

    def remove_plotting_strategy(self, label: str):
        self.plots.remove_plot_strategy(label)
        ax = self.axes.from_label(label)
        if not self.plots.axes_has_strategies(ax):
            self.legend.remove_legend()
        self.plot()

    @draw
    def plot(self):
        for ax in self.axes:
            if self.plots.axes_has_strategies(ax):
                self.draw_plots_to_axes(ax)

    def draw_plots_to_axes(self, ax: Axes):
        # This is where we ask Matplotlib to do the heavy lifting of creating the graphs
        # Qt doesn't yet draw it to the screen
        plots = self.plots.from_axes(ax)
        for plot in plots:
            try:
                plot(ax)
            except DataNotReadyException:
                pass
        self.draw_legend(ax, self.widget.figure, plots)

    def draw_legend(self, ax: Axes, figure: Figure, strategies: Sequence[PlotStrategy]):
        self.legend(ax, figure, strategies)

    def has_strategies(self) -> bool:
        return any(self.plots.axes_has_strategies(ax) for ax in self.axes)
