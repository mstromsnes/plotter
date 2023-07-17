import logging

from ui.dataplotterwindow import DataPlotterWindow
from sources import SensorDataFrameHandler
from datathread import DataThreadController
from PySide6 import QtCore, QtWidgets


def main():
    app = QtWidgets.QApplication()
    available_datasets = ["Pi-sensors"]

    def load_dataset(name: str) -> tuple[FrameHandler, DataThreadController]:
        match name:
            case "Pi-sensors":
                handler = SensorDataFrameHandler()
                thread = DataThreadController(handler)
                data_collection_timer.timeout.connect(thread.update_data)
                thread.finished.connect(window.update_visible_plot)
                return handler, thread
            case _:
                raise KeyError(f"Dataset {name} not available")

    window = DataPlotterWindow(available_datasets, load_dataset)
    data_collection_timer = QtCore.QTimer()

    window.resize(1200, 600)
    window.show()
    window.update_plots()
    data_collection_timer.timeout.emit()
    data_collection_timer.start(5000)
    app.exec()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
