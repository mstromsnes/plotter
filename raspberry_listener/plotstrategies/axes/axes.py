from abc import ABC, abstractmethod
from typing import Callable, Iterator, Sequence

from datamodels import DataIdentifier
from matplotlib.axes import Axes
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
