from collections import defaultdict
from typing import Self

from numpy import datetime64, floating
from numpy.typing import NDArray

from .datatypes import DataIdentifier, DataSet_Fn, DataTypeModel, Unit

OneDimensionalTimeSeries = tuple[NDArray[datetime64], NDArray[floating]]


class OneDimensionalTimeSeriesModel(DataTypeModel):
    def __init__(self: Self):
        super().__init__()
        self._datalines: dict[DataIdentifier, DataSet_Fn] = dict()
        self._source_name_to_data_name: dict[str, list[str]] = defaultdict(list)

    def _register_data(self, dataset: DataIdentifier, dataset_fn: DataSet_Fn):
        if dataset in self._datalines:
            raise KeyError(f"{dataset.data} from {dataset.source} already registered")
        self._datalines[dataset] = dataset_fn
        self._source_name_to_data_name[dataset.source].append(dataset.data)
        self._has_data = True

    def get_data_name_from_source(self, source_name: str) -> list[str]:
        return self._source_name_to_data_name[source_name]

    def get_data(self, dataset: DataIdentifier) -> OneDimensionalTimeSeries:
        return self._datalines[dataset]()

    def get_data_identifiers(self) -> set[DataIdentifier]:
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
