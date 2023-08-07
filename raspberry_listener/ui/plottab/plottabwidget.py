from controller import supported_plots
from datamodels import DataTypeModel
from PySide6 import QtWidgets
from ui.plots import PlotWidget, PlotWidgetFactory


class DataTypeTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        model: DataTypeModel,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.widgets: list[PlotWidget] = []
        for supported_plot in supported_plots(model):
            try:
                plot_widget = PlotWidgetFactory.build(model, supported_plot)
                self.widgets.append(plot_widget)
                self.addTab(plot_widget, supported_plot.name())
            except KeyError:
                pass

    def update_plot(self):
        for widget in self.widgets:
            if widget.isVisible():
                widget.plot()
