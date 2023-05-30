from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


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
    def __init__(self, rescale_plot=True, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.plot_live = True
        self.rescale_plot = rescale_plot
        self.main_layout.addWidget(self.canvas)
        self.navigation_layout = QtWidgets.QHBoxLayout()
        self.navigation_layout.addWidget(
            NavigationToolbar(self.canvas, self, coordinates=False)
        )
        self.navigation_layout.addWidget(RescalePlotButton(self))
        self.navigation_layout.addStretch(1)
        self.navigation_layout.addWidget(FreezePlotButton(self))
        self.main_layout.addLayout(self.navigation_layout)

    def add_axes(self, *args, subplot=True, **kwargs):
        if subplot:
            ax = self.figure.add_subplot(*args, **kwargs)
        else:
            ax = self.figure.add_axes(*args, **kwargs)
        return ax

    def remove_axes(self, ax):
        self.figure.delaxes(ax)
