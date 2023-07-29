from abc import ABC, abstractmethod
from itertools import cycle
from typing import Sequence

from matplotlib.colors import Colormap

Color = tuple[float, float, float] | str


class ColorStrategy(ABC):
    @abstractmethod
    def get_color(self, label) -> Color | Sequence[Color] | Colormap:
        pass


class ColorMapStrategy(ColorStrategy):
    def __init__(self, colormap: Colormap):
        self._cm = colormap

    def get_color(self, label) -> Colormap:
        return self._cm


class CyclicColorStrategy(ColorStrategy):
    def __init__(self, color_sequence: Sequence[Color]):
        self._dataset_to_color = {}
        self._colorset = cycle(color_sequence)  # type: ignore

    def get_color(self, label: str) -> Color:
        try:
            return self._dataset_to_color[label]
        except KeyError:
            self._dataset_to_color[label] = next(self._colorset)
            return self._dataset_to_color[label]
