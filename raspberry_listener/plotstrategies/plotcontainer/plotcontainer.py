from matplotlib.axes import Axes

from ..plotstrategy import PlotStrategy


class PlotContainer:
    def __init__(self) -> None:
        self.a_plots: dict[Axes, list[PlotStrategy]] = {}
        self.k_plots: dict[tuple[str, str], PlotStrategy] = {}
        self.enabled: dict[PlotStrategy, bool] = {}

    def add_plot_strategy(self, key: tuple[str, str], ax: Axes, plot: PlotStrategy):
        try:
            if plot not in self.a_plots[ax]:
                self.a_plots[ax].append(plot)
        except KeyError:
            self.a_plots[ax] = [plot]
        self.k_plots[key] = plot

    def enable_plot(self, key: tuple[str, str]):
        self.enabled[self.k_plots[key]] = True

    def plot_already_constructed(self, label):
        return label in self.k_plots.keys()

    def remove_plot_strategy(self, key: tuple[str, str]):
        try:
            plot = self.k_plots[key]
            plot.remove_artist()
            self.enabled[self.k_plots[key]] = False
        except (KeyError, AttributeError):
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

    def from_key(
        self, key: tuple[str, str], enabled: bool | None = True
    ) -> PlotStrategy:
        """_summary_

        Args:
            key (tuple[str,str]): Identifier of the PlotStrategy. It's a tuple of the (source_name, dataset_name)
            enabled (bool | None, optional): Returns depending on whether the strategy is enabled or not. If None return anyway. Defaults to True.

        Raises:
            KeyError: If a plotstrategy isn't found, or doesn't match enabled keyword, raises a KeyError

        Returns:
            PlotStrategy: _description_
        """
        plot = self.k_plots[key]
        if enabled is None:
            return plot
        if self.enabled[plot] == enabled:
            return plot
        else:
            raise KeyError

    def axes_has_strategies(self, ax: Axes) -> bool:
        return bool(self.from_axes(ax, enabled=True))
