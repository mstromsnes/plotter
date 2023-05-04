from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, DataType
from drawwidget import DrawWidget


class HistogramWidget(DrawWidget):
    def __init__(self, datatype: DataType, parent: QtWidgets.QWidget | None = None):
        super().__init__(rescale_plot=False, parent=parent)
        self.datatype = datatype
        self.line = None

    def update_graph(self, dataset: DataSet, title: str):
        self._dataset = dataset
        self._title = title

    @DrawWidget.draw
    def plot(self, *args, **kwargs):
        dataset = self._dataset
        for func in self._postprocessing_functions:
            dataset = func(dataset)
        _, data = dataset
        self.ax.hist(
            data,
            linewidth=0.5,
            edgecolor="white",
            log=True,
            density=True,
            orientation="horizontal",
            **kwargs
        )
        self.ax.set_title(self._title)
