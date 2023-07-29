from datetime import datetime, timedelta

import matplotlib.dates
import numpy as np
from PySide6 import QtCharts, QtCore, QtGui, QtWidgets


class LineChart(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.chart = QtCharts.QChart()
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

    def update_graph(self, data: tuple[np.ndarray, np.ndarray], title: str):
        if hasattr(self, "_data"):
            old_cnt = self._data.size
        else:
            old_cnt = 0

        self._time, self._data = data
        self._title = title
        if self._data.size > 0:
            vec = np.vectorize(self.toEpoch)
            # for i in range(old_cnt, self._data.size):
            #     self.series.append(self.toEpoch(self._time[i]), self._data[i])
            self.series.appendNp(vec(self._time), self._data)
        self.chart.setTitle(self._title)

    def plot(self, **kwargs):
        if self._data.size > 0 and self.isVisible():
            ten_seconds = timedelta(seconds=10)

            self.xaxis.setRange(
                self.toQDateTime(self.toDatetime(self._time[0]) - ten_seconds),
                self.toQDateTime(self.toDatetime(self._time[-1]) + ten_seconds),
            )
            self.yaxis.setRange(np.min(self._data) - 1, np.max(self._data) + 1)
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
