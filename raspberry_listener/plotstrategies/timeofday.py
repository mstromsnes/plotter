from time import perf_counter
from typing import Sequence

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, Normalize
from matplotlib.container import BarContainer
from matplotlib.projections.polar import PolarAxes
from matplotlib.ticker import NullFormatter
from sources import DataNotReadyException

from .plotstrategy import PlotNotReadyException, PlotStrategy


class TimeOfDayPlot(PlotStrategy):
    @staticmethod
    def name():
        return "Time of Day"

    def __call__(self, ax: PolarAxes, **kwargs):
        try:
            before = perf_counter()
            counts, bins = self.time_of_day_histogram()
            after = perf_counter()
            print(f"{after-before} seconds for histogram calculation")
        except DataNotReadyException:
            return
        try:
            self.remove_artist()
        except AttributeError:
            pass
        before = perf_counter()
        self.plot_clock(ax, counts, bins, **kwargs)
        after = perf_counter()
        print(f"{after-before} seconds for plotting")

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
            color = self.colormap(X=normalizer(centre_value))
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
        self.set_grid(ax)
        self._used_norm = normalizer

    def set_grid(self, ax: PolarAxes):
        angle_step = 360 // 24
        angles = (float(i * angle_step) for i in range(24))
        labels = (str(i) for i in range(24))
        ax.set_thetagrids(tuple(angles), tuple(labels))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xlim((0, 2 * np.pi))

    def time_of_day_histogram(self):
        full_timeseries, full_data = self.model.get_data(self.label)
        timeseries = full_timeseries[::1]
        data = full_data[0::1]
        # Here we get the bins for the entire range of values in the dataset. Each hour can have a different range of values, producing different bins
        # In order to properly compare we want to use the same bins for every hour
        first_edge = np.min(data)
        last_edge = np.max(data)
        bin_count = min(64, len(np.unique(data)))
        print(bin_count)
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

    def set_tick_formatter(self, ax):
        ax.yaxis.set_major_formatter(NullFormatter())

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


class FlatTimeOfDay(PlotStrategy):
    @staticmethod
    def name():
        return "Flat Time of Day"

    def __call__(self, ax: PolarAxes, **kwargs):
        try:
            counts, bins, mean_x_values, mean_values = self.get_plot_data()
        except DataNotReadyException:
            return
        try:
            self.remove_artist()
        except AttributeError:
            pass
        self.plot_stacked_bar(ax, counts, bins, **kwargs)
        self.plot_mean_line(ax, mean_x_values, mean_values)

        self.set_tick_formatter(ax)

    def get_plot_data(self):
        full_timeseries, full_data = self.model.get_data(self.label)
        timeseries = full_timeseries[::1]
        data = full_data[0::1]
        counts, bins = self.time_of_day_histogram(timeseries, data)
        mean_x_values, mean_values = self.time_of_day_mean(timeseries, data)
        return counts, bins, mean_x_values, mean_values

    def plot_mean_line(self, ax: Axes, mean_x_axis, mean_values: np.ndarray):
        range = np.max(mean_values) - np.min(mean_values)
        excess_space = 0.1 * range
        normalizer = Normalize(
            np.min(mean_values) - excess_space, np.max(mean_values) + excess_space
        )

        secy_axis = ax.secondary_yaxis(
            "left", functions=(normalizer.inverse, normalizer)
        )
        secy_axis.set_ylabel(f"Mean {self.model.name()}")
        ax.plot(mean_x_axis, normalizer(mean_values))

    def plot_stacked_bar(
        self,
        ax: Axes,
        counts: np.ndarray,
        bins: np.ndarray,
        **kwargs,
    ):
        normalizer = Normalize(bins[0], bins[-2])
        bottom = np.zeros(24)
        self.artists: Sequence[BarContainer] = []
        x = range(24)
        width = 1
        for i in range(len(bins) - 1):
            centre_value = (bins[-(i + 1)] + bins[-(i + 1) - 1]) / 2
            left_value = bins[-(i + 1)]
            color = self.colormap(X=normalizer(centre_value))
            height = counts.T[-(i + 1)]
            artist = ax.bar(
                x=x,
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
        self.set_grid(ax)
        self._used_norm = normalizer

    def time_of_day_histogram(self, timeseries, data):
        # Here we get the bins for the entire range of values in the dataset. Each hour can have a different range of values, producing different bins
        # In order to properly compare we want to use the same bins for every hour
        first_edge = np.min(data)
        last_edge = np.max(data)
        bin_count = min(64, len(np.unique(data)))
        print(bin_count)
        bin_edges = np.linspace(
            first_edge, last_edge, bin_count, endpoint=True, dtype=data.dtype
        )
        bin_edges = np.append(bin_edges, bin_edges[-1] + (bin_edges[1] - bin_edges[0]))
        frame = pd.DataFrame(data, index=pd.DatetimeIndex(timeseries))
        histogram = self._density_count_by_hour(frame, bin_edges)
        return histogram, bin_edges

    def time_of_day_mean(self, timeseries, data):
        frame = pd.DataFrame(data, index=pd.DatetimeIndex(timeseries))
        assert isinstance(frame.index, pd.DatetimeIndex)
        frame["timeofday"] = list(
            # zip(frame.index.hour, frame.index.minute, frame.index.second)
            zip(frame.index.hour, frame.index.minute)
        )
        grouping = frame.groupby("timeofday")
        mean_data = grouping.mean()
        x_value_count = mean_data.size
        x_axis_values = np.linspace(0, 24, x_value_count, endpoint=False)
        return x_axis_values, mean_data

    def set_grid(self, ax: Axes):
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 1)

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

    def set_tick_formatter(self, ax):
        ax.yaxis.set_major_formatter(NullFormatter())

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
