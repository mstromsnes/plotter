from typing import Protocol, Sequence
from matplotlib.axes import Axes
from matplotlib.artist import Artist


class PlotStrategy(Protocol):
    def __call__(self, ax: Axes, **kwargs):
        """A method that plots something from self on axes ax."""
        ...

    @property
    def artist(self) -> Artist | Sequence[Artist]:
        ...
