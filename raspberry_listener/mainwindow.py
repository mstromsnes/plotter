from PySide6 import QtWidgets, QtGui, QtCore
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
        self.tab_widgets = {}
        for sensor_type, sensors in self.sensors.items():
            for sensor in sensors:
                tab = PlotTabWidget(sensor, sensor_type, data_mediator)
                self.tab_widgets[sensor, sensor_type] = tab
                tab_name = f"{sensor.value} {sensor_type.value.capitalize()}"
                self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.currentChanged.connect(self.update_plots)

        self.setCentralWidget(self.tab_widget)

    def update_plots(self):
        for widget in self.tab_widgets.values():
            widget.update_plot()
