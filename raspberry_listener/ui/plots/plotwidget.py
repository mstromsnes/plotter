from functools import wraps
from typing import Self

from datamodels import DataIdentifier
from plotmanager import PlotManager
from PySide6 import QtWidgets
from ui.dataselector import DataSelector
from ui.drawwidget import DrawWidget


class ManagerNotSetException(Exception):
    ...


class PlotWidget(DrawWidget):
    @staticmethod
    def ensure_manager(fn):
        @wraps(fn)
        def wrapper(self: Self, *args, **kwargs):
            try:
                assert self.manager is not None
                fn(self, *args, **kwargs)
            except AssertionError:
                raise ManagerNotSetException

        return wrapper

    def __init__(
        self,
        selector: DataSelector,
        rescale_plot: bool,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(rescale_plot, parent=parent)
        self.manager: PlotManager = None  # type: ignore
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(selector.widget())
        self.h_layout.addLayout(self.canvas_toolbar_layout, stretch=1)
        selector.data_toggled.connect(self.toggle_data)  # type: ignore
        self.setLayout(self.h_layout)

    @ensure_manager
    def toggle_data(self, dataset: DataIdentifier, checked: bool):
        if checked:
            self.manager.add_plotting_strategy(dataset)
        else:
            self.manager.remove_plotting_strategy(dataset)

    @ensure_manager
    def plot(self):
        self.manager.plot()

    def set_manager(self, manager: PlotManager):
        self.manager = manager
