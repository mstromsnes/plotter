from PySide6 import QtGui, QtCore, QtWidgets
import mainwindow
from datathread import DataThread
from datamediator import DataMediator
import logging


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator()
    window = mainwindow.MainWindow(data_source)
    datathread = DataThread(data_source, window)

    data_collection_timer = QtCore.QTimer()

    data_collection_timer.timeout.connect(datathread.gather_data)
    datathread.finished.connect(window.update_visible_plot)
    window.resize(800, 600)
    window.show()
    window.update_plots()
    data_collection_timer.timeout.emit()
    data_collection_timer.start(5000)
    app.exec()


def gather_data(data_source: DataMediator):
    data_source.merge_new_data_into_dataframe()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
