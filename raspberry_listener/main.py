from time import perf_counter
from PySide6 import QtGui, QtCore, QtWidgets
import numpy as np
import mainwindow
from datamediator import DataMediator, DataType, DataSource
from remotereader import LogDownloader

HOST = "192.168.4.141"
PORT = 65431


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator(DataSource.Archive)
    archive = LogDownloader()
    data_source.set_archive(DataType.CPU_TEMP, *archive.get_latest_archive())
    window = mainwindow.MainWindow(data_source)
    data_collection_timer = QtCore.QTimer()
    data_collection_timer.timeout.connect(lambda: gather_data(archive, data_source))
    gather_data(archive, data_source)
    data_collection_timer.start(5000)
    data_display_timer = QtCore.QTimer()
    # data_display_timer.timeout.connect(
    #     lambda: print(data_source.get_data(DataType.CPU_TEMP))
    # )
    data_display_timer.timeout.connect(
        lambda: plot(data_source.get_data(DataType.CPU_TEMP), window)
    )
    window.tab_widget.currentChanged.connect(
        lambda: plot(data_source.get_data(DataType.CPU_TEMP), window)
    )
    data_display_timer.start(500)
    window.resize(800, 600)
    window.show()
    app.exec()


def gather_data(archive, data_source):
    archive.get_latest_archive()
    data_source.gather_data(DataType.CPU_TEMP)


def plot(raw_data: tuple[np.ndarray, np.ndarray, int], window):
    window.plotwidget.update_graph(raw_data, "CPU TEMP")
    window.plotwidget.plot()

    window.qt_line_chart.update_graph(raw_data, "CPU TEMP")
    window.qt_line_chart.plot()


if __name__ == "__main__":
    main()
