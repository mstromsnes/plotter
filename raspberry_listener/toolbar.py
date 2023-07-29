from PySide6 import QtCore, QtGui, QtWidgets


class Toolbar(QtWidgets.QToolBar):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
