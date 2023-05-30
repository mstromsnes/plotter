from PySide6 import QtWidgets, QtCore
from lineplotwidget import LinePlotWidget
from datatypes import Sensor, SensorType
from datamediator import DataMediator
from functools import partial


class SideBar(QtWidgets.QTreeWidget):
    button_toggled = QtCore.Signal(SensorType, Sensor, bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        for sensor_type in SensorType:
            top_level_item = QtWidgets.QTreeWidgetItem(self)
            top_level_item.setText(0, sensor_type.value)
            for sensor in Sensor:
                clickable_item = QtWidgets.QTreeWidgetItem(top_level_item)
                button = QtWidgets.QCheckBox()
                button.setText(sensor.value)
                callback = partial(self.button_toggled_fn, sensor_type, sensor)
                button.toggled.connect(callback)
                self.setItemWidget(clickable_item, 0, button)

    def button_toggled_fn(self, sensor_type, sensor, state):
        self.button_toggled.emit(sensor_type, sensor, state)


class PlotTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        datasource: DataMediator,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.datasource = datasource
        self.linewidget = LinePlotWidget(self.datasource)
        sidebar = SideBar()
        self.intermediate_widget = self.widget_with_sidebar(self.linewidget, sidebar)
        sidebar.button_toggled.connect(self.linewidget.toggle_line)
        self.addTab(self.intermediate_widget, "Line")
        self.currentChanged.connect(self.update_plot)

    def update_plot(self):
        self.linewidget.plot()

    @staticmethod
    def widget_with_sidebar(plot_widget, sidebar):
        widget = QtWidgets.QWidget(None)
        hbox = QtWidgets.QHBoxLayout(widget)
        hbox.addWidget(plot_widget, stretch=1)
        hbox.addWidget(sidebar)
        return widget
