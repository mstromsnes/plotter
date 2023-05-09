from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, Sensor, SensorType
from drawwidget import DrawWidget
import numpy as np
import numpy.typing as npt
import pandas as pd
from collections import namedtuple
import matplotlib.ticker
import matplotlib as mpl
from dataclasses import dataclass


class IncompatibleDatatypeException(Exception):
    ...


@dataclass
class BinInfo:
    counts: npt.ArrayLike
    bins: npt.ArrayLike

    def __post_init__(self):
        self.difference_between_bins = np.diff(self.bins)[0]


class TimeOfDayWidget(DrawWidget):
    MAX_BUCKETS = 16
    colormap = mpl.colormaps["viridis"]

    def __init__(
        self,
        sensor: Sensor,
        sensor_type: SensorType,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(rescale_plot=False, parent=parent)
        self.sensor = sensor
        self.sensor_type = sensor_type
        self.clocks = [
            self.figure.add_subplot(1, 2, 1, projection="polar"),
            self.figure.add_subplot(1, 2, 2, projection="polar"),
        ]
        self._norm = mpl.colors.Normalize(0, 1)

    def update_graph(self, dataset: DataSet, title: str):
        dataframe = self._group_time_of_day(dataset)
        self._dataset = dataset
        self.sufficient_data = True
        try:
            self._bins: BinInfo = self._get_binned_count_by_hour(dataframe)
            self._norm = mpl.colors.Normalize(
                self._dataset[1].min(), self._dataset[1].max()
            )
        except KeyError:
            self.sufficient_data = False
        self._title = title

    @DrawWidget.draw
    def plot(self, *args, **kwargs):
        [clock.clear() for clock in self.clocks]
        # There is no fallback for missing data, so if we don't have data for all 24 hours, don't draw anything
        if self.sufficient_data:
            for offset, clock in enumerate(self.clocks):
                self._plot_clock(clock, offset, **kwargs)
            self.figure.legend(loc="upper right")

    def _get_binned_count_by_hour(self, dataframe: pd.DataFrame):
        """Return the counts of data in bins of width self.step_size for each hour"""
        counts = []
        bins = self._dataset.bins(self.MAX_BUCKETS)
        for i in np.arange(24):
            data = dataframe[i]
            count, _ = np.histogram(data, bins=bins, density=True)
            counts.append(count)
        return BinInfo(np.array(counts), bins)

    def _label_maker(self, bin, offset):
        if offset:
            return None
        if isinstance(
            self._dataset.smallest_difference_between_unique_values, np.int64
        ):
            if (
                self._dataset.smallest_difference_between_unique_values
                == self._bins.difference_between_bins
            ):
                return f"{int(bin+self._bins.difference_between_bins/2.0):d}"
            else:
                return f"{int(bin):d}-{int(bin+self._bins.difference_between_bins-1):d}"

        return f"{bin:.2f}-{bin+self._bins.difference_between_bins:.2f}"

    def _plot_clock(self, clock, offset, **kwargs):
        """Plot a single radial stacked barplot showing the temperature density for the hour"""
        bottom = np.zeros(12)
        Bound = namedtuple("Bound", ["lower", "upper"])
        hour_range = Bound(12 * offset, 12 * (offset + 1))  # (0,12) and (12,24)
        data = self._bins.counts[hour_range.lower : hour_range.upper]
        for i, bin in enumerate(self._bins.bins[:-1]):
            label = self._label_maker(bin, offset)
            theta = np.linspace(0, 2 * np.pi, 12, endpoint=False)
            width = theta[1] - theta[0]
            clock.bar(
                theta,
                data.T[i],
                width=width,
                bottom=bottom,
                label=label,
                align="edge",
                color=self.colormap(self._norm(bin)),
                **kwargs,
            )
            bottom += data.T[i]
        clock.set_theta_offset(np.pi / 2)
        clock.set_theta_direction(-1)
        angle_step = 360 // 12
        angles = [(i * angle_step) for i in range(12)]
        labels = range(hour_range.lower, hour_range.upper)
        clock.set_thetagrids(angles, labels)
        clock.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())

    def _group_time_of_day(self, dataset):
        """Given a tuple of numpy arrays containing the data and the time series index for that data, construct a pandas dataframe with a multiindex.
        The multiindex allows requesting all data that occured within a specific hour of every day.
        """
        time, data = dataset
        df = pd.DataFrame({self.datatype.dataframe_names[0]: data}, index=time)
        df = df.groupby(df.index.hour, group_keys=True)[
            self.datatype.dataframe_names[0]
        ].apply(
            lambda x: x
        )  # Dataframe with multiindex on the hour
        return df
