from PySide6 import QtGui, QtCore, QtWidgets
import numpy as np
import mainwindow
from datamediator import DataMediator, DataType, DataSource
from datatypes import DataSet

HOST = "192.168.4.141"
PORT = 65431


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator(DataSource.Archive)
    window = mainwindow.MainWindow(data_source, (HOST, PORT))
    plot_updater = PlotUpdater(window)

    data_collection_timer = QtCore.QTimer()
    data_collection_timer.timeout.connect(lambda: gather_data(data_source))
    data_collection_timer.timeout.emit()
    data_collection_timer.start(5000)
    window.resize(800, 600)
    window.show()
    plot_updater.plot(data_source.get_data(DataType.CPU_TEMP))
    window.tab_widget.currentChanged.connect(
        lambda: plot_updater.plot(data_source.get_data(DataType.CPU_TEMP))
    )
    app.exec()


def gather_data(data_source: DataMediator):
    data_source.gather_data(DataType.CPU_TEMP)


class PlotUpdater:
    def __init__(self, window: mainwindow.MainWindow):
        self._last_timestamp: np.datetime64 | None = None
        self.window = window

    def plot(self, data_tuple: DataSet):
        if data_tuple[0].size > 0:
            last_timestamp = data_tuple[0][-1]
            if self._last_timestamp != last_timestamp:
                self.window.plotwidget.update_graph(data_tuple, "CPU TEMP")
                self.window.plotwidget.plot()
            self._last_timestamp = last_timestamp


if __name__ == "__main__":
    main()
