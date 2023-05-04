from PySide6 import QtGui, QtCore, QtWidgets
import mainwindow
from datamediator import DataMediator, DataType, DataSource

HOST = "192.168.4.141"
PORT = 65431


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator(DataSource.Archive)
    window = mainwindow.MainWindow(data_source, (HOST, PORT))

    data_collection_timer = QtCore.QTimer()

    def plot_data():
        window.update_plots()

    def gather_and_plot():
        gather_data(data_source)
        plot_data()

    window.resize(800, 600)
    window.show()
    data_collection_timer.timeout.connect(gather_and_plot)
    data_collection_timer.timeout.emit()
    data_collection_timer.start(5000)
    app.exec()


def gather_data(data_source: DataMediator):
    for datatype in DataType.to_set():
        data_source.gather_data(datatype)
    # data_source.gather_data(DataType.MPU_TEMP)
    # data_source.gather_data(DataType.DHT_TEMP)


if __name__ == "__main__":
    main()
