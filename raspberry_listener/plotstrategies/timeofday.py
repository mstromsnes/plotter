from matplotlib.projections.polar import PolarAxes
from sources import DataNotReadyException
from matplotlib.container import BarContainer
from typing import Sequence
from .plotstrategy import PlotStrategy
from datamodels import DataTypeModel
import numpy as np
import pandas as pd


class TimeOfDayPlot(PlotStrategy):

    def __init__(
        self,
        model: DataTypeModel,
        label: str,
    ):
        self.model = model
        self.label = label

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
        self.set_tick_formatter(ax)

    def plot_clock(self, ax: PolarAxes, counts: np.ndarray, bins: np.ndarray, **kwargs):
        bottom = np.zeros(24)
        self._artists = []
        for i in range(len(bins) - 1):
            centre_value = (bins[i] + bins[i + 1]) / 2
            theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
            width = theta[1] - theta[0]
            height = counts.T[i]
            artist = ax.bar(
                x=theta,
                height=height,
                width=width,
                bottom=bottom,
                align="edge",
                label=f"{centre_value:.2f}",
                **kwargs,
            )
            bottom += height
            self._artists.append(artist)
        angle_step = 360 // 24
        angles = (float(i * angle_step) for i in range(24))
        labels = (str(i) for i in range(24))
        ax.set_thetagrids(tuple(angles), tuple(labels))
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xlim((0, 2 * np.pi))

    def time_of_day_histogram(self):
        timeseries, data = self.model.get_data(self.label)
        # Here we get the bins for the entire range of values in the dataset. Each hour can have a different range of values, producing different bins
        # In order to properly compare we want to use the same bins for every hour
        first_edge = np.min(data)
        last_edge = np.max(data)
        bin_count = 10
        bin_edges = np.linspace(
            first_edge, last_edge, bin_count + 1, endpoint=True, dtype=data.dtype
        )
        frame = pd.DataFrame(data, index=pd.DatetimeIndex(timeseries))
        counts = self._density_count_by_hour(frame, bin_edges)
        return counts, bin_edges

    def _density_count_by_hour(self, frame: pd.DataFrame, bins):
        assert isinstance(frame.index, pd.DatetimeIndex)
        grouping = frame.groupby(frame.index.hour)

        def count_without_bins(array, bins):
            count, _ = np.histogram(array, bins, density=True)
            return count / sum(
                count
            )  # The density integral is 1, not the sum. They are equal if the bin-width is 1, which is not the case here.

        counts = [count_without_bins(group, bins) for _, group in grouping]
        return np.array(counts)

    @property
    def artist(self) -> Sequence[BarContainer]:
        return self._artists

    def set_tick_formatter(self, ax):
        ax.yaxis.set_major_formatter(NullFormatter())

    def remove_artist(self):
        try:
            [artist.remove() for artist in self.artist]
            del self._artists
        except AttributeError:
            pass
