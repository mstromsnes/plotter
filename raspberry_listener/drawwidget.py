from PySide6 import QtWidgets, QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from functools import wraps
from datatypes import DataSet
import numpy as np
from typing import Callable

UnpackedDataSet = tuple[np.ndarray, np.ndarray]


class FreezePlotButton(QtWidgets.QPushButton):
    def __init__(
        self, plot_widget: "DrawWidget", parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.clicked.connect(self.toggle_plotting)
        self.update_text()

    def update_text(self):
        text = "Freeze Plot" if self.plot_widget.plot_live else "Resume"
        self.setText(text)

    def toggle_plotting(self):
        self.plot_widget.plot_live = not self.plot_widget.plot_live
        self.update_text()


class RescalePlotButton(QtWidgets.QCheckBox):
    def __init__(
        self, plot_widget: "DrawWidget", parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.setText("Automatically rescale plot")
        self.stateChanged.connect(self.set_rescaling)
        self.setChecked(self.plot_widget.rescale_plot)

    def set_rescaling(self, checked):
        self.plot_widget.rescale_plot = checked


class DrawWidget(QtWidgets.QWidget):
    @staticmethod
    def draw(func):
        @wraps(func)
        def wrapper(self: "DrawWidget", *args, **kwargs):
            if self.plot_live and self.canvas.isVisible():
                func(self, *args, **kwargs)
                if self.rescale_plot:
                    self._rescale()
                self.canvas.draw_idle()

        return wrapper

    def __init__(self, rescale_plot=True, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.plot_live = True
        self.rescale_plot = rescale_plot
        self.main_layout.addWidget(self.canvas, stretch=1)
        self.navigation_layout = QtWidgets.QHBoxLayout()
        self.navigation_layout.addWidget(
            NavigationToolbar(self.canvas, self, coordinates=False)
        )
        self.navigation_layout.addWidget(RescalePlotButton(self))
        self.navigation_layout.addStretch(1)
        self.navigation_layout.addWidget(FreezePlotButton(self))
        self.main_layout.addLayout(self.navigation_layout)

        self.plot_once = False
        self._postprocessing_functions = []

    def update_graph(self, dataset: DataSet, title: str):
        ...

    def add_postprocessing_function(
        self, func: Callable[[UnpackedDataSet], UnpackedDataSet]
    ):
        self._postprocessing_functions.append(func)

    def plot(self, *args, **kwargs):
        ...

    def _rescale(self):
        ...
