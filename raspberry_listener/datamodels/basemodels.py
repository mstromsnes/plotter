from collections import defaultdict

from numpy import datetime64, floating
from numpy.typing import NDArray

from .datatypes import DataSet_Fn, DataTypeModel, Unit

OneDimensionalTimeSeries = tuple[NDArray[datetime64], NDArray[floating]]


class OneDimensionalTimeSeriesModel(DataTypeModel):
    def __init__(self):
        super().__init__()
        self._datalines: dict[str, DataSet_Fn] = {}
        self._name_to_source_name: dict[str, str] = defaultdict(str)

    def register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        if name in self._datalines.keys():
            raise KeyError(f"{name} already registered")
        self._datalines[name] = dataset_fn
        self._name_to_source_name[name] = source_name
        self._has_data = True

    def get_source_name(self, name) -> str:
        return self._name_to_source_name[name]

    def get_data(self, name: str) -> OneDimensionalTimeSeries:
        return self._datalines[name]()

    def get_dataset_names(self) -> set[str]:
        return set(self._datalines.keys())


class TemperatureModel(OneDimensionalTimeSeriesModel):
    _unit = Unit(short="C", long="Celcius", explanation="Temperature")

    def name(self):
        return "Temperature"


class HumidityModel(OneDimensionalTimeSeriesModel):
    _unit = Unit(short="%", long="Percent Humidity", explanation="Relative Humidity")

    def name(self):
        return "Humidity"
