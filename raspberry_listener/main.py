import logging

from controller import (
    register_raspberry_sensor_data,
    register_yr_forecast_data,
    register_yr_historic_data,
)
from datamodels import DataTypeManager, HumidityModel, TemperatureModel
from datathread import DataThreadController
from PySide6 import QtCore, QtWidgets
from sources import DataLoader, SensorDataFrameHandler, YrForecast, YrHistoric
from ui.dataplotterwindow import DataPlotterWindow


def main():
    app = QtWidgets.QApplication()
    available_datasets = ["Pi-sensors", "Yr Forecast", "Yr Historic"]

    datatype_manager = DataTypeManager()
    temperature_model = TemperatureModel()
    humidity_model = HumidityModel()
    datatype_manager.register_datatype(temperature_model)
    datatype_manager.register_datatype(humidity_model)

    def load_dataset(name: str) -> DataThreadController:
        def make_thread(handler: DataLoader):
            thread = DataThreadController(handler)
            data_collection_timer.timeout.connect(thread.update_data)
            thread.finished.connect(window.update_visible_plot)
            return thread

        match name:
            case "Pi-sensors":
                handler = SensorDataFrameHandler()
                register_raspberry_sensor_data(
                    handler, temperature_model, humidity_model, name
                )
            case "Yr Forecast":
                handler = YrForecast()
                register_yr_forecast_data(
                    handler, temperature_model, humidity_model, name
                )
            case "Yr Historic":
                handler = YrHistoric()
                register_yr_historic_data(
                    handler, temperature_model, humidity_model, name
                )
            case _:
                raise KeyError(f"Dataset {name} not available")
        return make_thread(handler)

    window = DataPlotterWindow(available_datasets, load_dataset, datatype_manager)
    data_collection_timer = QtCore.QTimer()

    window.resize(1200, 600)
    window.show()
    data_collection_timer.timeout.emit()
    data_collection_timer.start(5000)
    app.exec()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("debuglog.log")],
    )
    main()
