from PySide6 import QtWidgets, QtGui, QtCore
from lineplotwidget import LinePlotWidget
from histogramwidget import HistogramWidget
from timeofdayhistogramwidget import TimeOfDayWidget
from datatypes import DataHandler
from datamediator import DataMediator
from graphupdater import GraphUpdater


class PlotTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        datatype: DataHandler,
        datasource: DataMediator,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.datatype = datatype
        self.datasource = datasource
        use_integer_y_axis = self.datatype.datatype() == int
        self.linewidget = LinePlotWidget(self.datatype, use_integer=use_integer_y_axis)
        self.linewidget_manager = GraphUpdater(self.linewidget, self.datatype.tab_name)
        self.histogramwidget = HistogramWidget(
            self.datatype, use_integer=use_integer_y_axis
        )
        self.histogramwidget_manager = GraphUpdater(
            self.histogramwidget, self.datatype.tab_name
        )
        if self.datatype.ndims == 1:
            self.time_of_day_widget = TimeOfDayWidget(self.datatype)
            self.time_of_day_widget_manager = GraphUpdater(
                self.time_of_day_widget, self.datatype.tab_name
            )
        self.addTab(self.linewidget, "Line")
        self.addTab(self.histogramwidget, "Histogram")
        if self.datatype.ndims == 1:
            self.addTab(self.time_of_day_widget, "Time of Day")
        self.currentChanged.connect(self.update_plot)

    def update_plot(self):
        dataset = self.datasource.get_data(self.datatype)
        self.linewidget_manager.plot(dataset)
        self.histogramwidget_manager.plot(dataset)
        if self.datatype.ndims == 1:
            self.time_of_day_widget_manager.plot(dataset)
