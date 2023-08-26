import logging
from collections.abc import Sequence
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


def create_populated_manager() -> DataTypeManager:
    datatype_manager = DataTypeManager()
    temperature_model = TemperatureModel()
    humidity_model = HumidityModel()
    datatype_manager.register_datatype(temperature_model)
    datatype_manager.register_datatype(humidity_model)
    return datatype_manager


def load_dataset(
    source_name: str, datatype_manager: DataTypeManager
) -> DataThreadController:
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
        models: Sequence[DataTypeModel],
        thread: DataThreadController,
        source_name: str,
    ):
        for model in models:
            connect_model(model, thread, source_name)

    match source_name:
        case "Pi-sensors":
            handler = SensorDataFrameHandler()
            models = register_raspberry_sensor_data(
                handler, datatype_manager, source_name
            )
            init_load_fn = handler.initial_load
            update_fn = handler.update_data
        case "Yr Forecast":
            handler = YrForecast()
            models = register_yr_forecast_data(handler, datatype_manager, source_name)
            init_load_fn = handler.initial_load
            update_fn = None
        case "Yr Historic":
            handler = YrHistoric()
            models = register_yr_historic_data(handler, datatype_manager, source_name)
            init_load_fn = handler.initial_load
            update_fn = None
        case _:
            raise KeyError(f"Dataset {source_name} not available")
    thread = make_thread(init_load_fn, update_fn)
    connect_models(models, thread, source_name)
    return thread


def main():
    available_datasets = ["Pi-sensors", "Yr Forecast", "Yr Historic"]
    datatype_manager = create_populated_manager()

    app = QtWidgets.QApplication()
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
