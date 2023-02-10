from PySide6 import QtGui, QtCore, QtWidgets
import numpy as np
import mainwindow
from datamediator import DataMediator, DataType, DataSource
from remotereader import LogDownloader
from datatypes import DataSet

HOST = "192.168.4.141"
PORT = 65431


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator(DataSource.Archive)
    archive = LogDownloader()
    data_source.set_archive(DataType.CPU_TEMP, *archive.get_latest_archive())
    window = mainwindow.MainWindow(data_source, (HOST, PORT))
    gather_data(archive, data_source)
    plot_updater = PlotUpdater(window)

    def gather_and_plot():
        gather_data(archive, data_source)
        plot_updater.plot(data_source.get_data(DataType.CPU_TEMP))

    data_collection_timer = QtCore.QTimer()
    data_collection_timer.timeout.connect(gather_and_plot)
    data_collection_timer.start(5000)
    window.resize(800, 600)
    window.show()
    plot_updater.plot(data_source.get_data(DataType.CPU_TEMP))
    window.tab_widget.currentChanged.connect(
        lambda: plot_updater.plot(data_source.get_data(DataType.CPU_TEMP))
    )
    app.exec()


def gather_data(archive: LogDownloader, data_source: DataMediator):
    archive.get_latest_archive()
    data_source.gather_data(DataType.CPU_TEMP)


class PlotUpdater:
    def __init__(self, window: mainwindow.MainWindow):
        self._last_timestamp: np.datetime64 | None = None
        self.window = window

    def plot(self, data_tuple: DataSet):
        last_timestamp = data_tuple[0][-1]
        if self._last_timestamp != last_timestamp:
            self.window.plotwidget.update_graph(data_tuple, "CPU TEMP")
            self.window.plotwidget.plot()
        self._last_timestamp = last_timestamp


if __name__ == "__main__":
    main()
