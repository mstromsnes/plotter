import pandas as pd
from matplotlib.axes import Axes
from typing import Optional
from datatypes import SensorType, Sensor
from datamediator import DataMediator, DataNotReadyException
from matplotlib.lines import Line2D
from .plotstrategy import PlotStrategy


class LinePlot(PlotStrategy):
    def __init__(
        self,
        datasource: DataMediator,
        sensor_type: SensorType,
        sensor: Sensor,
        label: Optional[str] = None,
    ):
        self.datasource = datasource
        self.sensor_type = sensor_type
        self.sensor = sensor
        self.label = (
            label if label is not None else f"{sensor_type.value} - {sensor.value}"
        )

    def __call__(self, ax: Axes):
        try:
            series = self.get_timeindexed_single_sensor_series()
            try:
                self.artist.set_xdata(series.index.to_numpy())
                self.artist.set_ydata(series.to_numpy())
            except AttributeError:
                self._artists = ax.plot(
                    series.index.to_numpy(), series.to_numpy(), label=self.label
                )
        except DataNotReadyException:
            pass

    def get_timeindexed_single_sensor_series(self) -> pd.Series:
        df = self.datasource.dataframe
        single_sensor_df = df.loc[self.sensor_type.value, self.sensor.value]
        assert isinstance(single_sensor_df, pd.DataFrame)
        series = single_sensor_df.get("reading")
        assert isinstance(series, pd.Series)
        return series

    @property
    def artist(self) -> Line2D:
        return self._artists[0]
