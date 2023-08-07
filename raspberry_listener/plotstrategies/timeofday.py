from typing import Sequence

import numpy as np
import pandas as pd
from matplotlib.colors import Colormap, Normalize
from matplotlib.container import BarContainer
from matplotlib.projections.polar import PolarAxes
from sources import DataNotReadyException

from .plotstrategy import PlotNotReadyException, PlotStrategy


class ColorNotSetException(Exception):
    ...


class TimeOfDayPlot(PlotStrategy):
    @staticmethod
    def name():
        return "Time of Day"

    def __call__(self, ax: PolarAxes, **kwargs):
        try:
            counts, bins = self.time_of_day_histogram()
        except DataNotReadyException:
            return
        try:
            self.remove_artist()
        except AttributeError:
            pass
        self.plot_clock(ax, counts, bins, **kwargs)
        self.set_tick_formatter(ax)

    def plot_clock(
        self,
        ax: PolarAxes,
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
        self._used_norm = normalizer

    def time_of_day_histogram(self):
        full_timeseries, full_data = self.model.get_data(self.label)
        timeseries = full_timeseries[::1]
        data = full_data[0::1]
        # Here we get the bins for the entire range of values in the dataset. Each hour can have a different range of values, producing different bins
        # In order to properly compare we want to use the same bins for every hour
        first_edge = np.min(data)
        last_edge = np.max(data)
        bin_count = min(64, len(np.unique(data)))
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

        counts = [count_without_bins(group, bins) for _, group in grouping]
        counts = np.array(counts)
        return counts

    def remove_artist(self):
        try:
            [artist.remove() for artist in self.artists]
            del self.artists
        except AttributeError:
            pass

    def set_colorsource(self, colors: Colormap):
        self.colormap = colors

    def get_colormap(self):
        return self.colormap

    def get_normalizer(self):
        try:
            return self._used_norm
        except AttributeError:
            raise PlotNotReadyException
