from controller import supported_plots
from datamodels import DataTypeModel
from plotstrategies import HistogramPlot, LinePlot, PlotStrategy
from PySide6 import QtWidgets
from ui.plots import HistogramWidget, LinePlotWidget, PlotWidget

from .sidebar import SideBar


class DataTypeTabWidget(QtWidgets.QTabWidget):
    WIDGET_STRATEGY: dict[type[PlotStrategy], type[PlotWidget]] = {
        LinePlot: LinePlotWidget,
        HistogramPlot: HistogramWidget,
    }

    def __init__(
        self,
        model: DataTypeModel,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.widgets: list[PlotTabWidget] = []
        for supported_plot in supported_plots(model):
            try:
                widget_type = self.WIDGET_STRATEGY[supported_plot]
                widget = PlotTabWidget(model, widget_type)
                self.widgets.append(widget)
                self.addTab(widget, supported_plot.name())
            except KeyError:
                pass
        self.currentChanged.connect(self.update_plot)

    def update_plot(self):
        for widget in self.widgets:
            if widget.isVisible():
                widget.update_plot()


class PlotTabWidget(QtWidgets.QWidget):
    def __init__(
        self,
        model: DataTypeModel,
        widget_type: type[PlotWidget],
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.plot_widget = widget_type(self.model)
        self.sidebar = SideBar(model)
        self.sidebar.button_toggled.connect(self.plot_widget.toggle_data)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.plot_widget, stretch=1)
        hbox.addWidget(self.sidebar)
        self.setLayout(hbox)

    def update_plot(self):
        self.plot_widget.plot()
