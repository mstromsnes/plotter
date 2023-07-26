from datamodels import DataTypeModel
from plotmanager import OneAxesPlotManager
from plotstrategies import HistogramPlot
from PySide6 import QtCore, QtWidgets

from .plotwidget import PlotWidget


class HistogramWidget(PlotWidget):
    def __init__(
        self,
        model: DataTypeModel,
        parent: QtWidgets.QWidget | None = None,
        **kwargs,
    ):
        super().__init__(parent=parent)

        self.model = model
        self.manager = OneAxesPlotManager(self, model, "Timeseries")

    @QtCore.Slot(str, bool)
    def toggle_data(self, label: str, checked: bool):
        if not checked:
            self.manager.remove_plotting_strategy(label)
        else:
            self.manager.add_plotting_strategy(label, HistogramPlot)

    def plot(self):
        self.manager.plot()
