from plotstrategies import PlotStrategy, LinePlot
from collections import defaultdict
from datamodels import DataSet_Fn, DataTypeModel
from numpy.typing import NDArray
from numpy import datetime64, floating

OneDimensionalTimeSeries = tuple[NDArray[datetime64], NDArray[floating]]


class OneDimensionalTimeSeriesModel(DataTypeModel):
    SUPPORTED_PLOTS = {LinePlot}

    def __init__(self):
        super().__init__()
        self._datalines: dict[str, DataSet_Fn] = {}
        self._plottype_to_name: dict[type[PlotStrategy], list[str]] = defaultdict(list)
        self._name_to_plot: dict[str, list[PlotStrategy]] = defaultdict(list)
        self._name_to_source_name: dict[str, str] = defaultdict(str)

    def register_data(self, name: str, dataset_fn: DataSet_Fn, source_name: str):
        if name in self._datalines.keys():
            raise KeyError(f"{name} already registered")
        self._datalines[name] = dataset_fn
        self._name_to_source_name[name] = source_name
        self._make_plots(name, dataset_fn)
        self._has_data = True

    def get_source_name(self, name) -> str:
        return self._name_to_source_name[name]

    def get_data(self, name: str) -> OneDimensionalTimeSeries:
        return self._datalines[name]()

    def get_plots(self, name: str) -> list[PlotStrategy]:
        return self._name_to_plot[name]

    def get_plot(self, name: str, plot_type: type[PlotStrategy]) -> PlotStrategy:
        plots = self._name_to_plot[name]
        for plot in plots:
            if isinstance(plot, plot_type):
                return plot
        raise KeyError

    def get_dataset_names(self) -> set[str]:
        return set(self._datalines.keys())

    def supported_plots(self) -> set[type[PlotStrategy]]:
        return self.SUPPORTED_PLOTS

    def _make_plots(self, name: str, dataset_fn: DataSet_Fn):
        for plot_type in self.SUPPORTED_PLOTS:
            plot = plot_type(dataset_fn, model=self, label=name)
            self._plottype_to_name[plot_type].append(name)
            self._name_to_plot[name].append(plot)


class TemperatureModel(OneDimensionalTimeSeriesModel):
    def name(self):
        return "Temperature"


class HumidityModel(OneDimensionalTimeSeriesModel):
    def name(self):
        return "Humidity"
