from collections import defaultdict
from typing import Self

from numpy import datetime64, floating
from numpy.typing import NDArray

from .datatypes import DataSet_Fn, DataTypeModel, Unit

OneDimensionalTimeSeries = tuple[NDArray[datetime64], NDArray[floating]]


class OneDimensionalTimeSeriesModel(DataTypeModel):
    def __init__(self: Self):
        super().__init__()
        self._datalines: dict[tuple[str, str], DataSet_Fn] = {}
        self._source_name_to_data_name: dict[str, list[str]] = defaultdict(list)

    def _register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        key = (source_name, name)
        if key in self._datalines.keys():
            raise KeyError(f"{name} from {source_name} already registered")
        self._datalines[key] = dataset_fn
        self._source_name_to_data_name[source_name].append(name)
        self._has_data = True

    def get_data_name_from_source(self, source_name: str) -> list[str]:
        return self._source_name_to_data_name[source_name]

    def get_data(self, key: tuple[str, str]) -> OneDimensionalTimeSeries:
        return self._datalines[key]()

    def get_dataset_names(self) -> set[tuple[str, str]]:
        return set(self._datalines.keys())

    def get_source_names(self) -> set[str]:
        return set(self._source_name_to_data_name.keys())


class TemperatureModel(OneDimensionalTimeSeriesModel):
    _unit = Unit(short="C", long="Celcius", explanation="Temperature")

    def name(self):
        return "Temperature"


class HumidityModel(OneDimensionalTimeSeriesModel):
    _unit = Unit(short="%", long="Percent Humidity", explanation="Relative Humidity")

    def name(self):
        return "Humidity"
