from plotmanager import OneAxesPlotManager
from plotstrategies.line import LinePlot
from PySide6 import QtCore, QtWidgets
from .plotwidget import PlotWidget
from .simplifyplotbutton import SimplifyPlotSpinBox
from datamodels import DataTypeModel


class LinePlotWidget(PlotWidget):
    def __init__(
        self,
        model: DataTypeModel,
        parent: QtWidgets.QWidget | None = None,
        **kwargs,
    ):
        super().__init__(parent=parent)

        self.model = model
        self.navigation_layout.addWidget(SimplifyPlotSpinBox())
        self.manager = OneAxesPlotManager(self, model, "Timeseries")

    @QtCore.Slot(str, bool)
    def toggle_data(self, label: str, checked: bool):
        if checked:
            self.manager.add_plotting_strategy(label, LinePlot)
        else:
            self.manager.remove_plotting_strategy(label)

    def plot(self):
        self.manager.plot()
