import plotmanager
from sources import FrameHandler
from plotstrategies.line import LinePlot
from PySide6 import QtCore, QtWidgets
from ui.drawwidget import DrawWidget
from .simplifyplotbutton import SimplifyPlotSpinBox


class LinePlotWidget(DrawWidget):
    def __init__(
        self,
        datasource: FrameHandler,
        parent: QtWidgets.QWidget | None = None,
        **kwargs,
    ):
        super().__init__(parent=parent)

        self.datasource = datasource
        self.navigation_layout.addWidget(SimplifyPlotSpinBox())
        self.manager = plotmanager.OneAxesPrSensorTypeManager(self, "Timeseries")

    @QtCore.Slot(tuple, bool)
    def toggle_line(self, dataset_key: tuple, label: str | None, checked: bool):
        if not checked:
            self.manager.remove_plotting_strategy(*dataset_key)
        else:
            strategy = LinePlot(self.datasource, dataset_key, label)
            self.manager.add_plotting_strategy(strategy, *dataset_key)

    def plot(self):
        self.manager.plot()
