from datamodels import DataIdentifier
from matplotlib.axes import Axes

from ..plotstrategy import PlotStrategy


class PlotContainer:
    def __init__(self) -> None:
        self.axes_to_plots_map: dict[Axes, list[PlotStrategy]] = {}
        self.identifier_to_plot_map: dict[DataIdentifier, PlotStrategy] = {}
        self.enabled: dict[PlotStrategy, bool] = {}

    def add_plot_strategy(self, dataset: DataIdentifier, ax: Axes, plot: PlotStrategy):
        try:
            if plot not in self.axes_to_plots_map[ax]:
                self.axes_to_plots_map[ax].append(plot)
        except KeyError:
            self.axes_to_plots_map[ax] = [plot]
        self.identifier_to_plot_map[dataset] = plot

    def enable_plot(self, dataset: DataIdentifier):
        self.enabled[self.identifier_to_plot_map[dataset]] = True

    def plot_already_constructed(self, dataset: DataIdentifier):
        return dataset in self.identifier_to_plot_map

    def remove_plot_strategy(self, dataset: DataIdentifier):
        try:
            plot = self.identifier_to_plot_map[dataset]
            self.enabled[self.identifier_to_plot_map[dataset]] = False
            plot.remove_artist()
        except (KeyError, AttributeError):
            pass

    def from_axes(self, ax: Axes, enabled: bool | None = True) -> list[PlotStrategy]:
        """Get the list of all plots from a particular axes

        Args:
            ax (Axes): The Axes the PlotStrategy are attached to
            enabled (bool | None, optional):  Changes which stratetgies get returned. If None, return all of them.

        Returns:
            list[PlotStrategy]: The list of PlotStrategy that have been constructed and attached to a specific Axes.
        """
        try:
            plots = self.axes_to_plots_map[ax]
        except KeyError:
            return []
        if enabled is None:
            return plots
        return [plot for plot in plots if self.enabled[plot]]

    def from_source_with_name(
        self, source: str, enabled: bool | None = True
    ) -> dict[str, PlotStrategy]:
        plots = {
            identifier.data: strategy
            for identifier, strategy in self.identifier_to_plot_map.items()
            if identifier.source == source
        }
        if enabled is None:
            return plots
        return {
            name: strategy
            for name, strategy in plots.items()
            if self.enabled[strategy] == enabled
        }

    def from_dataidentifier(
        self, dataset: DataIdentifier, enabled: bool | None = True
    ) -> PlotStrategy:
        """_summary_

        Args:
            dataset (DataIdentifier): Identifier of the PlotStrategy.
            enabled (bool | None, optional): Returns depending on whether the strategy is enabled or not. If None return anyway. Defaults to True.

        Raises:
            KeyError: If a plotstrategy isn't found, or doesn't match enabled keyword, raises a KeyError

        Returns:
            PlotStrategy: _description_
        """
        plot = self.identifier_to_plot_map[dataset]
        if enabled is None:
            return plot
        if self.enabled[plot] == enabled:
            return plot
        else:
            raise KeyError

    def axes_has_strategies(self, ax: Axes) -> bool:
        return bool(self.from_axes(ax, enabled=True))
