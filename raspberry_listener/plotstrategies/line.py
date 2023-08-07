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
        label: str,
    ):
        super().__init__(model, label)
        self.color = None

    @staticmethod
    def name():
        return "Line"

    def __call__(self, ax: Axes, **kwargs):
        try:
            x, y = self.model.get_data(self.label)
        except DataNotReadyException:
            return
        try:
            self.artist.set_xdata(x)
            self.artist.set_ydata(y)
            self.artist.recache()
        except AttributeError:
            self._artists = ax.plot(
                x,
                y,
                label=self.label,
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
