from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, DataHandler
from drawwidget import DrawWidget
import numpy as np
import pandas as pd
from collections import namedtuple
import matplotlib.ticker


class IncompatibleDatatypeException(Exception):
    ...


class TimeOfDayWidget(DrawWidget):
    MAX_BUCKETS = 16
    _FALLBACK_STEP_SIZE = 2

    def __init__(self, datatype: DataHandler, parent: QtWidgets.QWidget | None = None):
        if datatype.ndims != 1:
            raise IncompatibleDatatypeException("Can only handle 1 dimensional data")
        super().__init__(rescale_plot=False, parent=parent)
        self.datatype = datatype
        self.clocks = [
            self.figure.add_subplot(1, 2, 1, projection="polar"),
            self.figure.add_subplot(1, 2, 2, projection="polar"),
        ]

    def update_graph(self, dataset: DataSet, title: str):
        dataframe = self._group_time_of_day(dataset)
        self._dataset = dataset
        self.sufficient_data = True
        try:
            self._counts, self._bins = self._get_binned_count_by_hour(dataframe)
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
        # min_bin = np.floor(dataframe.min() / self.step_size) * self.step_size
        # max_bin = np.ceil(dataframe.max() / self.step_size) * self.step_size
        # bins = list(np.arange(min_bin, max_bin + self.step_size, self.step_size))
        bins = self._dataset.bins(self.MAX_BUCKETS)
        for i in np.arange(24):
            data = dataframe[i]
            count, _ = np.histogram(data, bins=bins, density=True)
            counts.append(
                count * self._dataset.smallest_difference_between_unique_values
            )
        return np.array(counts), bins

    def _plot_clock(self, clock, offset, **kwargs):
        """Plot a single radial stacked barplot showing the temperature density for the hour"""
        bottom = np.zeros(12)
        Bound = namedtuple("Bound", ["lower", "upper"])
        hour_range = Bound(12 * offset, 12 * (offset + 1))  # (0,12) and (12,24)
        data = self._counts[hour_range.lower : hour_range.upper]
        for i, bin in enumerate(self._bins[:-1]):
            label = (
                f"{bin:.2f}-{bin+self._dataset.smallest_difference_between_unique_values:.2f}"
                if not offset
                else None
            )
            theta = np.linspace(0, 2 * np.pi, 12, endpoint=False)
            width = theta[1] - theta[0]
            clock.bar(
                theta,
                data.T[i],
                width=width,
                bottom=bottom,
                label=label,
                align="edge",
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
