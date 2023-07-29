from enum import Enum, auto
from typing import Self

from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from PySide6 import QtWidgets

from .components import FreezePlotButton, RescalePlotButton, SimplifyPlotSpinBox
from .drawwidget import DrawWidget


class Side(Enum):
    Left = auto()
    Right = auto()


class NavBarBuilder:
    """This is a toolbar sitting below the plot that usually offers the built-in navigation toolbar provided by matplotlib.
    It has an additional number of features that can be added on to either end of the toolbar by invoking the functions of the builder
    """

    def __init__(self):
        self.navbar = QtWidgets.QHBoxLayout()
        self.nav_layouts = {
            Side.Left: QtWidgets.QHBoxLayout(),
            Side.Right: QtWidgets.QHBoxLayout(),
        }
        self.navbar.addLayout(self.nav_layouts[Side.Left])
        self.navbar.addStretch(1)
        self.navbar.addLayout(self.nav_layouts[Side.Right])
        self.queue = []

    def navigation_toolbar(self, coordinates=False, side: Side = Side.Left) -> Self:
        self.queue.append(
            lambda widget: self.nav_layouts[side].addWidget(
                NavigationToolbar(widget.canvas, widget, coordinates=coordinates)
            )
        )
        return self

    def freeze_plot(self, side: Side = Side.Right) -> Self:
        self.queue.append(
            lambda widget: self.nav_layouts[side].addWidget(FreezePlotButton(widget))
        )
        return self

    def rescale_plot(self, side: Side = Side.Left) -> Self:
        self.queue.append(
            lambda widget: self.nav_layouts[side].addWidget(RescalePlotButton(widget))
        )
        return self

    def simplify_plot(self, side: Side = Side.Right) -> Self:
        self.queue.append(
            lambda widget: self.nav_layouts[side].addWidget(SimplifyPlotSpinBox(widget))
        )
        return self

    def build(self, widget: "DrawWidget") -> QtWidgets.QHBoxLayout:
        for callable in self.queue:
            callable(widget)
        return self.navbar
