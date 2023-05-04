from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator
from datatypes import DataType
from toolbar import Toolbar
from plottabwidget import PlotTabWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        data_mediator: DataMediator,
        ip_port: tuple[str, int],
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.tool_bar = Toolbar(data_mediator, ip_port)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widgets = {
            datatype: PlotTabWidget(datatype, data_mediator)
            for datatype in DataType.to_set()
        }
        for datatype in DataType.to_set():
            self.tab_widget.addTab(self.tab_widgets[datatype], datatype.tab_name)
        self.tab_widget.currentChanged.connect(self.update_plots)

        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.tab_widget)

    def update_plots(self):
        for widget in self.tab_widgets.values():
            widget.update_plot()
