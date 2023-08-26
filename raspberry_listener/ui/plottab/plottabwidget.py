from controller import supported_plots
from datamodels import DataTypeModel
from PySide6 import QtWidgets
from ui.plots import PlotWidget
from ui.plotwidgetfactory import build_widgets


class DataTypeTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        model: DataTypeModel,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.widgets: dict[str, PlotWidget] = build_widgets(model)
        for name, widget in self.widgets.items():
            self.addTab(widget, name)
        self.currentChanged.connect(self.update_plots)

    def update_plots(self):
        for widget in self.widgets.values():
            if widget.isVisible():
                widget.plot()
