import numpy as np
from datamodels import DataTypeModel
from matplotlib.axes import Axes

from .plotstrategy import Color, SingleColorPlotStrategy


class HistogramPlot(SingleColorPlotStrategy):
    def __init__(self, model: DataTypeModel, key: tuple[str, str]):
        super().__init__(model, key)
        self.color = None

    @staticmethod
    def name():
        return "Histogram"

    def __call__(self, ax: Axes, **kwargs):
        time_series, barchart_data = self.model.get_data(
            self.key
        )  # We don't care about the time_series
        unique_values = len(np.unique(barchart_data))
        histogram, bin_edges = np.histogram(
            barchart_data, bins=np.min((16, unique_values)), density=True
        )
        histogram = histogram / np.sum(histogram)
        try:
            self.remove_artist()
        except AttributeError:
            pass
        width = bin_edges[1] - bin_edges[0]
        self.artist = ax.bar(
            bin_edges[:-1],
            histogram,
            width=width,
            align="center",
            label=f"{self.key[1]}, {self.key[0]}",
            log=True,
            alpha=0.8,
            color=self.color,
            **kwargs,
        )

    def remove_artist(self):
        self.artist.remove()
        del self.artist

    def set_color(self, color: Color):
        self.color = color
