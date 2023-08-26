from abc import ABC, abstractmethod
from typing import Callable, Iterator, Sequence

from datamodels import DataIdentifier
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure
from plotstrategies.tick import TickStrategy, major_tickformatter, minor_tickformatter


class AxesStrategy(ABC):
    def __init__(
        self,
        figure: Figure,
        major_tick: TickStrategy = major_tickformatter(),
        minor_tick: TickStrategy = minor_tickformatter(),
        subplot_kw: dict = {},
    ) -> None:
        self.figure = figure
        self.major_tick = major_tick
        self.minor_tick = minor_tick
        self.subplot_kw = subplot_kw

    @property
    @abstractmethod
    def axes(self) -> Sequence[Axes]:
        ...

    @abstractmethod
    def from_dataidentifier(self, dataset: DataIdentifier) -> Axes:
        ...

    @abstractmethod
    def add_plot(self, dataset: DataIdentifier):
        ...

    @abstractmethod
    def remove_plot(self, dataset: DataIdentifier):
        ...

    def __iter__(self) -> Iterator[Axes]:
        self.it = iter(self.axes)
        return self

    def __next__(self) -> Axes:
        it = self.it
        return next(it)


class SingleAxesSubFigureStrategy(AxesStrategy):
    def __init__(
        self,
        figure: Figure,
        major_tick: TickStrategy = major_tickformatter(),
        minor_tick: TickStrategy = minor_tickformatter(),
        subplot_kw: dict = {},
    ) -> None:
        super().__init__(figure, major_tick, minor_tick, subplot_kw)
        subfigure: SubFigure = figure.subfigures(1, 1)
        self.ax: Axes = subfigure.subplots(1, subplot_kw=subplot_kw)
        self.major_tick(self.ax)
        self.minor_tick(self.ax)

    @property
    def axes(self):
        return [self.ax]

    def from_dataidentifier(self, dataset: DataIdentifier):
        return self.ax

    def add_plot(self, dataset: DataIdentifier):
        pass

    def remove_plot(self, dataset: DataIdentifier):
        pass


class HorizontalOneSubfigureAxesPrPlotStrategy(AxesStrategy):
    def __init__(
        self,
        figure: Figure,
        major_tick: TickStrategy = major_tickformatter(),
        minor_tick: TickStrategy = minor_tickformatter(),
        subplot_kw: dict = {},
    ) -> None:
        super().__init__(figure, major_tick, minor_tick, subplot_kw)
        self._axes: dict[DataIdentifier, Axes] = {}

    @property
    def axes(self):
        return list(self._axes.values())

    def add_plot(self, dataset: DataIdentifier):
        if dataset in self._axes:
            return
        subfigures: list[list[SubFigure]] = self.figure.subfigures(
            1, len(self._axes) + 1, squeeze=False
        )
        for i, identifier in enumerate(self._axes.keys()):
            self.replace_axes_for_dataset(identifier, subfigures[0][i])
        self._axes[dataset] = self.create_axes(dataset, subfigures[0][-1])

    def replace_axes_for_dataset(self, dataset: DataIdentifier, subfigure: SubFigure):
        self._axes[dataset].remove()
        self._axes[dataset] = self.create_axes(dataset, subfigure)

    def create_axes(self, dataset: DataIdentifier, subfigure: SubFigure):
        ax = subfigure.subplots(1, subplot_kw=self.subplot_kw)
        ax.set_label(str(dataset))
        self.major_tick(ax)
        self.minor_tick(ax)
        return ax

    def remove_plot(self, dataset: DataIdentifier):
        if dataset not in self._axes:
            return
        self._axes[dataset].remove()
        del self._axes[dataset]
        cols = len(self._axes)
        if cols > 0:
            subfigures: list[list[SubFigure]] = self.figure.subfigures(
                1, cols, squeeze=False
            )
            for i, identifier in enumerate(self._axes.keys()):
                self.replace_axes_for_dataset(identifier, subfigures[0][i])

    def from_dataidentifier(self, dataset: DataIdentifier) -> Axes:
        return self._axes[dataset]


class SingleAxesStrategy(AxesStrategy):
    def __init__(
        self,
        figure: Figure,
        major_tick: TickStrategy = major_tickformatter(),
        minor_tick: TickStrategy = minor_tickformatter(),
        subplot_kw: dict = {},
    ) -> None:
        super().__init__(figure, major_tick, minor_tick, subplot_kw)
        self.ax: Axes = figure.subplots(1, subplot_kw=subplot_kw)
        self.major_tick(self.ax)
        self.minor_tick(self.ax)

    @property
    def axes(self):
        return [self.ax]

    def from_dataidentifier(self, dataset: DataIdentifier):
        return self.ax

    def add_plot(self, dataset: DataIdentifier):
        pass

    def remove_plot(self, dataset: DataIdentifier):
        pass
