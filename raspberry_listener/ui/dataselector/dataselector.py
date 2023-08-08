from typing import Protocol

from PySide6 import QtCore, QtWidgets


class DataSelector(Protocol):
    @property
    def data_toggled(self) -> QtCore.Signal:
        ...

    def widget(self) -> QtWidgets.QWidget:
        ...
