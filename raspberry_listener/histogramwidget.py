from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, Sensor, SensorType
from drawwidget import DrawWidget
from matplotlib.ticker import MaxNLocator


class HistogramWidget(DrawWidget):
    MAX_BUCKETS = 16

    def __init__(
        self,
        sensor: Sensor,
        sensor_type: SensorType,
        use_integer=False,
        parent: QtWidgets.QWidget | None = None,
        **kwargs
    ):
        super().__init__(rescale_plot=False, parent=parent)
        self.sensor = sensor
        self.sensor_type = sensor_type
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

    def _keep_current_scale(self, xlim: tuple[float, float], ylim: tuple[float, float]):
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
