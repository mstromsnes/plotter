from typing import Sequence

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize
from matplotlib.container import BarContainer

from .plotstrategy import ColormapPlotStrategy, PlotNotReadyException


class ColorNotSetException(Exception):
    ...


class TimeOfDayPlot(ColormapPlotStrategy):
    def __call__(self, ax: Axes, **kwargs):
        counts, bins = self.time_of_day_histogram(max_bincount=64)
        try:
            self.remove_artist()
        except AttributeError:
            pass
        self.plot_clock(ax, counts, bins, **kwargs)

    def plot_clock(
        self,
        ax: Axes,
        counts: np.ndarray,
        bins: np.ndarray,
        **kwargs,
    ):
        normalizer = Normalize(bins[0], bins[-2])
        bottom = np.zeros(24)
        self.artists: Sequence[BarContainer] = []
        theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        width = theta[1] - theta[0]
        for i in range(len(bins) - 1):
            centre_value = (bins[i] + bins[i + 1]) / 2
            left_value = bins[i]
            try:
                color = self.colormap(X=normalizer(centre_value))
            except AttributeError:
                raise ColorNotSetException
            height = counts.T[i]
            artist = ax.bar(
                x=theta,
                height=height,
                width=width,
                bottom=bottom,
                align="edge",
                label=f"{left_value:.2f}",
                color=color,
                edgecolor=color,
                **kwargs,
            )
            bottom += height
            self.artists.append(artist)
        for border in theta:
            ax.axvline(border, 0, 1, color="grey", linewidth=0.3)
        self._used_norm = normalizer

    def time_of_day_histogram(self, max_bincount):
        full_timeseries, full_data = self.model.get_data(self.dataset)
        timeseries = full_timeseries[::1]
        data = full_data[0::1]
        # Here we get the bins for the entire range of values in the dataset. Each hour can have a different range of values, producing different bins
        # In order to properly compare we want to use the same bins for every hour
        first_edge = np.min(data)
        last_edge = np.max(data)
        bin_count = min(max_bincount, len(np.unique(data)))
        bin_edges = np.linspace(
            first_edge, last_edge, bin_count, endpoint=True, dtype=data.dtype
        )
        bin_edges = np.append(bin_edges, bin_edges[-1] + (bin_edges[1] - bin_edges[0]))
        frame = pd.DataFrame(data, index=pd.DatetimeIndex(timeseries))
        histogram = self._density_count_by_hour(frame, bin_edges)
        return histogram, bin_edges

    def _density_count_by_hour(self, frame: pd.DataFrame, bins):
        assert isinstance(frame.index, pd.DatetimeIndex)
        grouping = frame.groupby(frame.index.hour)

        def count_without_bins(array, bins):
            count, _ = np.histogram(array, bins, density=True)
            return count / np.sum(
                count
            )  # The density integral is 1, not the sum. They are equal if the bin-width is 1, which is not the case here.

        counts = np.array([count_without_bins(group, bins) for _, group in grouping])
        return counts

    def artist(self):
        pass

    def remove_artist(self):
        [artist.remove() for artist in self.artists]
        del self.artists

    def set_colormap(self, colors: Colormap):
        self.colormap = colors

    def get_colormap(self):
        return self.colormap

    def get_normalizer(self):
        try:
            return self._used_norm
        except AttributeError:
            raise PlotNotReadyException
