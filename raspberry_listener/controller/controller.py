from datamodels import DataTypeModel, OneDimensionalTimeSeriesModel
from plotstrategies import (
    HistogramPlot,
    LinePlot,
    PlotStrategy,
    TimeOfDayPlot,
    FlatTimeOfDay,
)

SUPPORTED_PLOTS = {
    OneDimensionalTimeSeriesModel: {
        LinePlot,
        HistogramPlot,
        TimeOfDayPlot,
        FlatTimeOfDay,
    }
}


def supported_plots(model: DataTypeModel) -> set[type[PlotStrategy]]:
    plots = set()
    for model_type, supported_plot_types in SUPPORTED_PLOTS.items():
        if isinstance(model, model_type):
            plots.update(supported_plot_types)
    return plots
