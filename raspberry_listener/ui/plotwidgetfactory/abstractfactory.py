from datamodels import DataTypeModel, OneDimensionalTimeSeriesModel
from ui.plots import PlotWidget

from .timeseriesfactory import build_timeseries_widgets


def build_widgets(model: DataTypeModel) -> dict[str, PlotWidget]:
    match model:
        case OneDimensionalTimeSeriesModel():
            return build_timeseries_widgets(model)
        case _:
            raise NotImplementedError(
                "This type of model does not have a factory function defined"
            )
