from datamodels import DataTypeModel
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from sources import DataNotReadyException

from .color import Color
from .plotstrategy import PlotStrategy


class LinePlot(PlotStrategy):
    def __init__(
        self,
        model: DataTypeModel,
        key: tuple[str, str],
    ):
        super().__init__(model, key)
        self.color = None

    @staticmethod
    def name():
        return "Line"

    def __call__(self, ax: Axes, **kwargs):
        x, y = self.model.get_data(self.key)
        try:
            self.artist.set_xdata(x)
            self.artist.set_ydata(y)
            self.artist.recache()
        except AttributeError:
            self._artists = ax.plot(
                x,
                y,
                label=f"{self.key[1]}, {self.key[0]}",
                color=self.color,
                **kwargs,
            )

    @property
    def artist(self) -> Line2D:
        return self._artists[0]

    def remove_artist(self):
        try:
            self.artist.remove()
            del self._artists
        except AttributeError:
            pass

    def set_colorsource(self, colors: Color):
        self.color = colors
