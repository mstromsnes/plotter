from controller import supported_plots
from datamodels import DataTypeModel
from plotstrategies import PlotStrategy
from PySide6 import QtWidgets
from ui.plots import PlotWidgetFactory

from .sidebar import SideBar


class DataTypeTabWidget(QtWidgets.QTabWidget):
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
                widget = PlotTabWidget(model, supported_plot)
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
        plot_type: type[PlotStrategy],
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.plot_widget = PlotWidgetFactory.build(plot_type, model)
        self.sidebar = SideBar(model)
        self.sidebar.button_toggled.connect(self.plot_widget.toggle_data)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.plot_widget, stretch=1)
        hbox.addWidget(self.sidebar)
        self.setLayout(hbox)

    def update_plot(self):
        self.plot_widget.plot()
