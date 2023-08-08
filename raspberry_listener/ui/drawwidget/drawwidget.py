from typing import Protocol

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6 import QtWidgets


class LayoutBuilder(Protocol):
    def build(self, widget: "DrawWidget") -> QtWidgets.QHBoxLayout:
        ...


class DrawWidget(QtWidgets.QWidget):
    def __init__(self, rescale_plot=True, parent=None):
        super().__init__(parent)

        self.canvas_toolbar_layout = QtWidgets.QVBoxLayout()
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas_toolbar_layout.addWidget(self.canvas)
        self.plot_live = True
        self.rescale_plot = rescale_plot

    def add_axes(self, *args, subplot=True, **kwargs):
        if subplot:
            ax = self.figure.add_subplot(*args, **kwargs)
        else:
            ax = self.figure.add_axes(*args, **kwargs)
        return ax

    def remove_axes(self, ax):
        self.figure.delaxes(ax)

    def add_navigation_bar(self, builder: LayoutBuilder):
        self.canvas_toolbar_layout.addLayout(builder.build(self))
