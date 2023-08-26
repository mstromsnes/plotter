import numpy as np
from datamodels import DataIdentifier, DataTypeModel
from matplotlib.axes import Axes

from .plotstrategy import Color, SingleColorPlotStrategy


class HistogramPlot(SingleColorPlotStrategy):
    def __init__(self, model: DataTypeModel, dataset: DataIdentifier):
        super().__init__(model, dataset)
        self.color = None

    def __call__(self, ax: Axes, **kwargs):
        time_series, barchart_data = self.model.get_data(
            self.dataset
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
        self._artist = ax.bar(
            bin_edges[:-1],
            histogram,
            width=width,
            align="center",
            label=f"{self.dataset.data}, {self.dataset.source}",
            log=True,
            alpha=0.8,
            color=self.color,
            **kwargs,
        )

    def remove_artist(self):
        self._artist.remove()
        del self._artist

    def artist(self):
        return self._artist

    def set_color(self, color: Color):
        self.color = color
