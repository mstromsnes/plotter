from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, DataHandler
from drawwidget import DrawWidget
from matplotlib.ticker import MaxNLocator

# import numpy as np
# from math import ceil
# from numpy.typing import ArrayLike


class HistogramWidget(DrawWidget):
    MAX_BUCKETS = 16

    def __init__(
        self,
        datatype: DataHandler,
        use_integer=False,
        parent: QtWidgets.QWidget | None = None,
        **kwargs
    ):
        super().__init__(rescale_plot=False, parent=parent)
        self.datatype = datatype
        self.drawn = False
        self.ax = self.figure.add_subplot(**kwargs)
        self._use_integer = use_integer
        if use_integer:
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    def update_graph(self, dataset: DataSet, title: str):
        self._dataset = dataset
        self._title = title

    @DrawWidget.draw
    def plot(self, *args, **kwargs):
        dataset = self._dataset
        for func in self._postprocessing_functions:
            dataset = func(dataset)
        _, data = dataset
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.clear()
        self.ax.hist(
            data,
            self._dataset.bins(self.MAX_BUCKETS),
            linewidth=0.5,
            edgecolor="white",
            log=True,
            density=True,
            orientation="horizontal",
            **kwargs
        )
        if self._use_integer:
            # We need to reset this because of the ax.clear() call earlier
            self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        if not self.rescale_plot and self.drawn:
            self._keep_current_scale(xlim, ylim)
        self.ax.set_title(self._title)
        self.drawn = True

    def _keep_current_scale(self, xlim, ylim):
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)

    # """Many of the sensors have a fixed resolution or quantization. Maybe 1 K, maybe 1/8 K or similar. The DHT11 measures room temp 15-30 C in 1 degree increments. This means the number of expected values is ~15.
    # The humidity is 1% from 20-80%, giving 60 possible and expected values. For such low dynamic range data it would be nice to center the histogram bins on these values. For high dynamic range like the cpu temp we don't care as much.
    # We don't care about the actual dynamic range of the sensor, only the dynamic range in the dataset."""

    # @classmethod
    # def dynamic_range(cls, dataset: DataSet) -> int:
    #     dataset_value_range = dataset[1].max() - dataset[1].min()
    #     return ceil(
    #         dataset_value_range / cls.smallest_difference_between_unique_values(dataset)
    #     )

    # @classmethod
    # def reduced_dynamic_range(
    #     cls, dataset: DataSet, value_difference: float | int
    # ) -> int | float:
    #     dataset_value_range = dataset[1].max() - dataset[1].min()
    #     return ceil(dataset_value_range / value_difference)

    # @classmethod
    # def smallest_difference_between_unique_values(cls, dataset: DataSet) -> float | int:
    #     return np.diff(np.unique(dataset[1])).min()

    # @property
    # def dataset_dynamic_range(self) -> int:
    #     return self.dynamic_range(self._dataset)

    # @property
    # def _smallest_difference_between_unique_values_in_dataset(self):
    #     return self.smallest_difference_between_unique_values(self._dataset)

    # @property
    # def bins(self) -> ArrayLike | None:
    #     if not self._low_dynamic_range:
    #         return None
    #     discretization = self._smallest_difference_between_unique_values_in_dataset
    #     while (
    #         self.reduced_dynamic_range(self._dataset, discretization) > self.MAX_BUCKETS
    #     ):
    #         # Limits the number of buckets to MAX_BUCKETS. Doesn't guarantee 16 buckets if data-range is greater than 16
    #         discretization = discretization * 2
    #     left_of_first_bin = self._dataset[1].min() - float(discretization) / 2
    #     right_of_last_bin_plus_one = self._dataset[1].max() + 3 * (
    #         float(discretization) / 2
    #     )
    #     # Plus 1 as arange is not inclusive. We want the final element so we go one extra.
    #     return np.arange(left_of_first_bin, right_of_last_bin_plus_one, discretization)
