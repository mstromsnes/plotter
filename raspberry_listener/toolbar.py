from PySide6 import QtWidgets, QtGui, QtCore


class Toolbar(QtWidgets.QToolBar):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
