from collections import defaultdict

from numpy import datetime64, floating
from numpy.typing import NDArray

from .datatypes import DataSet_Fn, DataTypeModel, Unit

OneDimensionalTimeSeries = tuple[NDArray[datetime64], NDArray[floating]]


class OneDimensionalTimeSeriesModel(DataTypeModel):
    def __init__(self):
        super().__init__()
        self._datalines: dict[tuple[str, str], DataSet_Fn] = {}
        self._name_to_source_name: dict[str, str] = defaultdict(str)

        key = (source_name, name)
        if key in self._datalines.keys():
            raise KeyError(f"{name} from {source_name} already registered")
        self._datalines[key] = dataset_fn
        self._has_data = True

    def get_source_name(self, name) -> str:
        return self._name_to_source_name[name]

    def get_data(self, key: tuple[str, str]) -> OneDimensionalTimeSeries:
        return self._datalines[key]()

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
