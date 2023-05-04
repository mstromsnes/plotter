from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator
from datatypes import DataSet, DataType
from toolbar import Toolbar
from lineplotwidget import LinePlotWidget
from histogramwidget import HistogramWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        data_mediator: DataMediator,
        ip_port: tuple[str, int],
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.linewidget = LinePlotWidget(DataType.CPU_TEMP)
        self.histogramwidget = HistogramWidget(DataType.CPU_TEMP)
        self.tool_bar = Toolbar(data_mediator, ip_port)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.linewidget, "Line")
        self.tab_widget.addTab(self.histogramwidget, "Histogram")
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.tab_widget)

    def update_data(self, dataset: DataSet, title: str):
        self.linewidget.update_graph(dataset, title)
        self.histogramwidget.update_graph(dataset, title)

    def plot(self):
        self.linewidget.plot()
        self.histogramwidget.plot(color="royalblue")
