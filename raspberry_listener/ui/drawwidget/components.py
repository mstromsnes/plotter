from matplotlib import rcParams
from PySide6 import QtCore, QtWidgets

from .drawwidget import DrawWidget


class FreezePlotButton(QtWidgets.QPushButton):
    def __init__(
        self, plot_widget: DrawWidget, parent: QtWidgets.QWidget | None = None
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
        self, plot_widget: DrawWidget, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.setText("Automatically rescale plot")
        self.stateChanged.connect(self.set_rescaling)
        self.setChecked(self.plot_widget.rescale_plot)

    def set_rescaling(self, checked):
        self.plot_widget.rescale_plot = checked


class SimplifyPlotSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(
        self, plot_widget: DrawWidget, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.setValue(rcParams["path.simplify_threshold"])
        self.valueChanged.connect(self.update_threshold)
        self.setSingleStep(0.1)
        self.setMinimum(0)
        self.setMaximum(1)

    @QtCore.Slot(float)
    def update_threshold(self, v):
        rcParams["path.simplify_threshold"] = v
