from PySide6 import QtWidgets
from datamediator import DataMediator
from datatypes import Sensor, SensorType
from plottabwidget import PlotTabWidget


class MainWindow(QtWidgets.QMainWindow):
    sensors = {
        SensorType.Temperature: [Sensor.DHT11, Sensor.DS18B20, Sensor.PITEMP],
        SensorType.Humidity: [Sensor.DHT11],
    }

    def __init__(
        self,
        data_mediator: DataMediator,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widgets: dict[str, PlotTabWidget] = {}
        tab = PlotTabWidget(data_mediator)
        self.tab_widgets["line"] = tab
        tab_name = f"Line Plot"
        self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.currentChanged.connect(self.update_visible_plot)

        self.setCentralWidget(self.tab_widget)

    def update_plots(self):
        for widget in self.tab_widgets.values():
            widget.update_plot()

    def update_visible_plot(self):
        for widget in self.tab_widgets.values():
            if widget.isVisible():
                widget.update_plot()
