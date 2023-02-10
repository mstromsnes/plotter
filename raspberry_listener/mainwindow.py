from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator
from datatypes import DataSet
from toolbar import Toolbar
from lineplotwidget import LinePlotWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self, data_mediator: DataMediator, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plotwidget = LinePlotWidget()
        self.qt_line_chart = LineChart()
        
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.plotwidget, "Matplotlib")
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.tab_widget)

    def update_data(self, dataset: DataSet, title: str):
        self.plotwidget.update_graph(dataset, title)
        self.plotwidget.plot()
