from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator
from toolbar import Toolbar
from lineplotwidget import LinePlotWidget
from qtplotwidget import LineChart


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self, data_mediator: DataMediator, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plotwidget = LinePlotWidget()
        self.qt_line_chart = LineChart()
        self.tool_bar = Toolbar(data_mediator)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.plotwidget, "Matplotlib")
        self.tab_widget.addTab(self.qt_line_chart, "Qt")
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.tab_widget)
