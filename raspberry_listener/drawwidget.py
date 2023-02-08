from PySide6 import QtWidgets, QtCore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import rcParams
from functools import wraps


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


class SimplifyPlotSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setValue(rcParams["path.simplify_threshold"])
        self.valueChanged.connect(self.update_threshold)
        self.setSingleStep(0.1)
        self.setMinimum(0)
        self.setMaximum(1)

    @QtCore.Slot(float)
    def update_threshold(self, v):
        rcParams["path.simplify_threshold"] = v


class DrawWidget(QtWidgets.QWidget):
    @staticmethod
    def draw(func):
        @wraps(func)
        def wrapper(self: "DrawWidget", *args, **kwargs):
            if self.plot_live and self.canvas.isVisible():
                func(self, *args, **kwargs)
                if self.rescale_plot:
                    self.ax.relim()
                    self.ax.autoscale()
                self.canvas.draw_idle()

        return wrapper

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.plot_live = True
        self.rescale_plot = True
        layout.addWidget(self.canvas)
        navigation_layout = QtWidgets.QHBoxLayout()
        navigation_layout.addWidget(
            NavigationToolbar(self.canvas, self, coordinates=False)
        )
        navigation_layout.addWidget(RescalePlotButton(self))
        navigation_layout.addWidget(SimplifyPlotSpinBox())
        navigation_layout.addStretch(1)
        navigation_layout.addWidget(FreezePlotButton(self))
        layout.addLayout(navigation_layout)

        self.ax: Axes = self.figure.subplots(squeeze=False)[0][0]  # type: ignore
        self.plot_once = False

    def plot(self):
        ...
