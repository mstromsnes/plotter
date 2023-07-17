from matplotlib.axes import Axes
from sources import DataNotReadyException, FrameHandler
from matplotlib.lines import Line2D
from .plotstrategy import PlotStrategy


class LinePlot(PlotStrategy):
    def __init__(
        self,
        dataset_fn,
        model,
        label: str | None = None,
    ):
        self.dataset_fn = dataset_fn
        self.label = label

    @staticmethod
    def name():
        return "Line"

    def __call__(self, ax: Axes, **kwargs):
        try:
            x, y = self.dataset_fn()
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
