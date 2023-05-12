from PySide6 import QtWidgets, QtGui, QtCore
from lineplotwidget import LinePlotWidget
from histogramwidget import HistogramWidget
from timeofdayhistogramwidget import TimeOfDayWidget
from datatypes import Sensor, SensorType
from datamediator import DataMediator
from graphupdater import GraphUpdater


class PlotTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        sensor: Sensor,
        sensor_type: SensorType,
        datasource: DataMediator,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.sensor = sensor
        self.sensor_type = sensor_type
        self.datasource = datasource
        use_integer_y_axis = self.sensor == Sensor.DHT11
        self._tab_name = f"{self.sensor.value} {self.sensor_type.value.capitalize()}"
        self.linewidget = LinePlotWidget(
            self.sensor, self.sensor_type, use_integer=use_integer_y_axis
        )
        self.linewidget_manager = GraphUpdater(self.linewidget, self._tab_name)
        self.histogramwidget = HistogramWidget(
            self.sensor, self.sensor_type, use_integer=use_integer_y_axis
        )
        self.histogramwidget_manager = GraphUpdater(
            self.histogramwidget, self._tab_name
        )
        # self.time_of_day_widget = TimeOfDayWidget(self.sensor, self.sensor_type)
        # self.time_of_day_widget_manager = GraphUpdater(
        #     self.time_of_day_widget, self._tab_name
        # )
        self.addTab(self.linewidget, "Line")
        self.addTab(self.histogramwidget, "Histogram")
        # self.addTab(self.time_of_day_widget, "Time of Day")
        self.currentChanged.connect(self.update_plot)

    def update_plot(self):
        dataset = self.datasource.get_data(self.sensor, self.sensor_type)
        if dataset is not None:
            self.linewidget_manager.plot(dataset)
            self.histogramwidget_manager.plot(dataset)
            # self.time_of_day_widget_manager.plot(dataset)
