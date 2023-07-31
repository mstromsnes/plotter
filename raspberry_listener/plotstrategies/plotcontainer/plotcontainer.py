from matplotlib.axes import Axes

from ..plotstrategy import PlotStrategy


class PlotContainer:
    def __init__(self) -> None:
        self.a_plots: dict[Axes, list[PlotStrategy]] = {}
        self.l_plots: dict[str, PlotStrategy] = {}
        self.enabled: dict[PlotStrategy, bool] = {}

    def add_plot_strategy(self, label: str, ax: Axes, plot: PlotStrategy):
        try:
            if plot not in self.a_plots[ax]:
                self.a_plots[ax].append(plot)
        except KeyError:
            self.a_plots[ax] = [plot]
        self.l_plots[label] = plot

    def enable_plot(self, label: str):
        self.enabled[self.l_plots[label]] = True

    def plot_already_constructed(self, label):
        return label in self.l_plots.keys()

    def remove_plot_strategy(self, label: str):
        try:
            plot = self.l_plots[label]
            plot.remove_artist()
            self.enabled[self.l_plots[label]] = False
        except KeyError:
            pass

    def from_axes(self, ax: Axes, enabled: bool | None = True) -> list[PlotStrategy]:
        """_summary_

        Args:
            ax (Axes): The Axes the PlotStrategy are attached to
            enabled (bool | None, optional):  Changes which stratetgies get returned. If None, return all of them.

        Returns:
            list[PlotStrategy]: The list of PlotStrategy that have been constructed and attached to a specific Axes.
        """
        try:
            plots = self.a_plots[ax]
        except KeyError:
            return []
        if enabled is None:
            return plots
        return [plot for plot in plots if self.enabled[plot]]

    def from_label(self, label: str, enabled: bool | None = True) -> PlotStrategy:
        """_summary_

        Args:
            label (str): Identifier of the PlotStrategy
            enabled (bool | None, optional): Returns depending on whether the strategy is enabled or not. If None return anyway. Defaults to True.

        Raises:
            KeyError: If a plotstrategy isn't found, or doesn't match enabled keyword, raises a KeyError

        Returns:
            PlotStrategy: _description_
        """
        plot = self.l_plots[label]
        if enabled is None:
            return plot
        if self.enabled[plot] == enabled:
            return plot
        else:
            raise KeyError

    def axes_has_strategies(self, ax: Axes) -> bool:
        return bool(self.from_axes(ax, enabled=True))
