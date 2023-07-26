from matplotlib.axes import Axes
from sources import DataNotReadyException
from matplotlib.lines import Line2D
from .plotstrategy import PlotStrategy
from datamodels import DataTypeModel


class LinePlot(PlotStrategy):
    def __init__(
        self,
        model: DataTypeModel,
        label: str,
    ):
        self.model = model
        self.label = label

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
