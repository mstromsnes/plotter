from abc import ABC, abstractmethod
from typing import Callable, Iterator, Sequence

from matplotlib.axes import Axes
from matplotlib.figure import Figure


class AxesStrategy(ABC):
    def __init__(self, figure: Figure) -> None:
        self.figure = figure

    @property
    @abstractmethod
    def axes(self) -> Sequence[Axes]:
        ...

    @abstractmethod
    def from_label(self, label: str) -> Axes:
        ...

    def __iter__(self) -> Iterator[Axes]:
        self.it = iter(self.axes)
        return self

    def __next__(self) -> Axes:
        it = self.it
        return next(it)


class SingleAxesStrategy(AxesStrategy):
    def __init__(self, figure: Figure, axes_fn: Callable[[Figure], Axes]) -> None:
        super().__init__(figure)
        self.ax: Axes = axes_fn(figure)

    @property
    def axes(self):
        return [self.ax]

    def from_label(self, label: str):
        return self.ax
