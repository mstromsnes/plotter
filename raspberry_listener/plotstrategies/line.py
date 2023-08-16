from datamodels import DataTypeModel
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from .plotstrategy import Color, DataIdentifier, SingleColorPlotStrategy


class LinePlot(SingleColorPlotStrategy):
    def __init__(self, model: DataTypeModel, dataset: DataIdentifier):
        super().__init__(model, dataset)
        self.color = None

    @staticmethod
    def name():
        return "Line"

    def __call__(self, ax: Axes, **kwargs):
        x, y = self.model.get_data(self.dataset)
        try:
            self.artist.set_xdata(x)
            self.artist.set_ydata(y)
            self.artist.recache()
        except AttributeError:
            self._artists = ax.plot(
                x,
                y,
                label=f"{self.dataset.data}, {self.dataset.source}",
                color=self.color,
                **kwargs,
            )

    @property
    def artist(self) -> Line2D:
        return self._artists[0]

    def remove_artist(self):
        self.artist.remove()
        del self._artists

    def set_color(self, color: Color):
        self.color = color
