from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator
from toolbar import Toolbar


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self, data_mediator: DataMediator, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.tool_bar = Toolbar(data_mediator)
        self.addToolBar(self.tool_bar)
