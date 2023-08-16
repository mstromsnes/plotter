import logging
from functools import partial

from controller import (
    register_raspberry_sensor_data,
    register_yr_forecast_data,
    register_yr_historic_data,
)
from datamodels import DataTypeManager, DataTypeModel, HumidityModel, TemperatureModel
from datathread import DataThreadController, LoadFn
from PySide6 import QtCore, QtWidgets
from sources import SensorDataFrameHandler, YrForecast, YrHistoric
from ui.dataplotterwindow import DataPlotterWindow


def main():
    app = QtWidgets.QApplication()
    available_datasets = ["Pi-sensors", "Yr Forecast", "Yr Historic"]

    datatype_manager = DataTypeManager()
    temperature_model = TemperatureModel()
    humidity_model = HumidityModel()
    datatype_manager.register_datatype(temperature_model)
    datatype_manager.register_datatype(humidity_model)

    def load_dataset(source_name: str) -> DataThreadController:
        def make_thread(init_load_fn: LoadFn, update_data_fn: LoadFn | None = None):
            thread = DataThreadController(init_load_fn, update_data_fn)
            if update_data_fn is not None:
                data_collection_timer = QtCore.QTimer()
                data_collection_timer.setSingleShot(True)
                data_collection_timer.timeout.connect(thread.update_data)
                thread.finished.connect(partial(data_collection_timer.start, 5000))
            return thread

        def connect_model(
            model: DataTypeModel, thread: DataThreadController, source_name: str
        ):
            thread.finished.connect(partial(model.forward_source_updated, source_name))

        def connect_models(
            models: list[DataTypeModel], thread: DataThreadController, source_name: str
        ):
            for model in models:
                connect_model(model, thread, source_name)

        match source_name:
            case "Pi-sensors":
                handler = SensorDataFrameHandler()
                register_raspberry_sensor_data(
                    handler, temperature_model, humidity_model, source_name
                )
                thread = make_thread(handler.initial_load, handler.update_data)
                connect_models([temperature_model, humidity_model], thread, source_name)
            case "Yr Forecast":
                handler = YrForecast()
                register_yr_forecast_data(
                    handler, temperature_model, humidity_model, source_name
                )
                thread = make_thread(handler.initial_load)
                connect_models([temperature_model, humidity_model], thread, source_name)
            case "Yr Historic":
                handler = YrHistoric()
                register_yr_historic_data(
                    handler, temperature_model, humidity_model, source_name
                )
                thread = make_thread(handler.initial_load)
                connect_models([temperature_model, humidity_model], thread, source_name)
            case _:
                raise KeyError(f"Dataset {source_name} not available")
        return thread

    window = DataPlotterWindow(available_datasets, load_dataset, datatype_manager)

    window.resize(1200, 600)
    window.show()
    app.exec()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("debuglog.log")],
    )
    main()
