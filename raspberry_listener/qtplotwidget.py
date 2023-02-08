from PySide6 import QtWidgets, QtCharts, QtCore, QtGui
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates


class LineChart(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        # self.series = QtCharts.QLineSeries()
        self.chart = QtCharts.QChart()
        # self.chart.addSeries(self.series)
        # self.chart.createDefaultAxes()
        self._chart_view = QtCharts.QChartView(self.chart)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._chart_view)
        self.series = QtCharts.QLineSeries()
        self._cnt = 0
        self.chart.addSeries(self.series)
        self.xaxis = QtCharts.QDateTimeAxis()
        self.xaxis.setFormat("dd.MM.yyyy h.mm")
        self.yaxis = QtCharts.QValueAxis()
        self.chart.setAxisX(self.xaxis)
        self.chart.setAxisY(self.yaxis)
        self.series.attachAxis(self.xaxis)
        self.series.attachAxis(self.yaxis)
        self.vecToEpoch = np.vectorize(self.toTimestamp)
        self._chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    @classmethod
    def toTimestamp(cls, timestamp: np.datetime64):
        return int(cls.toDatetime(timestamp).timestamp() * 1000)

    @classmethod
    def toDatetime(cls, timestamp: np.datetime64) -> datetime:
        if isinstance(timestamp, datetime):
            return timestamp
        return matplotlib.dates.num2date(matplotlib.dates.date2num(timestamp))

    @classmethod
    def toEpoch(cls, timestamp: np.datetime64):
        return QtCore.QDateTime(cls.toDatetime(timestamp)).toMSecsSinceEpoch()

    @classmethod
    def toQDateTime(cls, timestamp: np.datetime64):
        return QtCore.QDateTime(cls.toDatetime(timestamp))

    def update_graph(self, data: np.ndarray, title: str):
        old_cnt = self._cnt
        self._time, self._data, self._cnt = data
        self._title = title
        if self._cnt > 0:
            # self.series.replaceNp(
            #     self.vecToEpoch(self._time[: self._cnt]), self._data[: self._cnt]
            # )
            for i in range(old_cnt, self._cnt):
                self.series.append(self.toEpoch(self._time[i]), self._data[i])
        self.chart.setTitle(self._title)

    def plot(self, **kwargs):
        if self._cnt > 0 and self.isVisible():
            ten_seconds = timedelta(seconds=10)

            self.xaxis.setRange(
                self.toQDateTime(self.toDatetime(self._time[0]) - ten_seconds),
                self.toQDateTime(
                    self.toDatetime(self._time[self._cnt - 1]) + ten_seconds
                ),
            )
            self.yaxis.setRange(
                np.min(self._data[: self._cnt]) - 1, np.max(self._data[: self._cnt] + 1)
            )
            self._chart_view.repaint()
        # # self.series.appendNp(self._time[: self._cnt], self._data[: self._cnt])
        # # self.series.append(0, 1)
        # # self.series.append(1, 2)
        # # self.series.append(2, 3)
        # # self.series.append(3, 4)

    # def old(self):
    #     if self.line is not None:
    #         self.line.set_xdata(self._time[: self._cnt])
    #         self.line.set_ydata(self._data[: self._cnt])
    #         # self.ax.set_xlim(self._time[0], self._time[self._cnt - 1])
    #         # self.ax.set_ylim(
    #         #     np.amin(self._data[: self._cnt]), np.amax(self._data[: self._cnt])
    #         # )
    #         self.ax.draw_artist(self.line)
    #     elif self._cnt > 0:
    #         (self.line,) = self.ax.plot(
    #             self._time[: self._cnt], self._data[: self._cnt], **kwargs
    #         )

    #     self.ax.set_title(self._title)
