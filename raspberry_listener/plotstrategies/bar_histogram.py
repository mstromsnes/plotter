from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from sources import DataNotReadyException
from datamodels import DataTypeModel
import numpy as np


class HistogramPlot(PlotStrategy):
    def __init__(
        self,
        model: DataTypeModel,
        label: str,
    ):
        self.label = label
        self.model = model

    @staticmethod
    def name():
        return "Histogram"

    def __call__(self, ax: Axes, **kwargs):
        try:
            time_series, barchart_data = self.model.get_data(
                self.label
            )  # We don't care about the time_series
        except DataNotReadyException:
            return
        unique_values = len(np.unique(barchart_data))
        histogram, bin_edges = np.histogram(
            barchart_data, bins=np.min((16, unique_values)), density=True
        )
        try:
            self._artists.remove()
        except AttributeError:
            pass
        if not "color" in kwargs.keys():
            kwargs["color"] = self.get_color()
        width = bin_edges[1] - bin_edges[0]
        self._artists = ax.bar(
            bin_edges[:-1],
            histogram,
            width=width,
            align="center",
            label=self.label,
            log=True,
            alpha=0.8,
            **kwargs,
        )
        self.set_tick_formatter(ax)

    def get_color(self):
        try:
            return self._artists.patches[0].get_facecolor()
        except AttributeError:
            pass
        return None

    @property
    def artist(self):
        return self._artists

    def set_tick_formatter(self, ax):
        formatter = FuncFormatter(lambda x, pos: f"{x}{self.model.unit.short}")
        formatter.set_offset_string(self.model.unit.explanation)
        ax.xaxis.set_major_formatter(formatter)

    def remove_artist(self):
        try:
            self.artist.remove()
            del self._artists
        except AttributeError:
            pass
