import logging

from ui.dataplotterwindow import DataPlotterWindow
from sources import SensorDataFrameHandler
from controller import register_raspberry_sensor_data
from datathread import DataThreadController
from PySide6 import QtCore, QtWidgets
from datamodels import TemperatureModel, HumidityModel, DataTypeManager


def main():
    app = QtWidgets.QApplication()
    available_datasets = ["Pi-sensors"]

    datatype_manager = DataTypeManager()
    temperature_model = TemperatureModel()
    humidity_model = HumidityModel()
    datatype_manager.register_datatype(temperature_model)
    datatype_manager.register_datatype(humidity_model)

    def load_dataset(name: str) -> DataThreadController:
        match name:
            case "Pi-sensors":
                handler = SensorDataFrameHandler()
                register_raspberry_sensor_data(
                    handler, temperature_model, humidity_model, name
                )
                thread = DataThreadController(handler)
                data_collection_timer.timeout.connect(thread.update_data)
                thread.finished.connect(window.update_visible_plot)
                return thread
            case _:
                raise KeyError(f"Dataset {name} not available")

    window = DataPlotterWindow(available_datasets, load_dataset, datatype_manager)
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
