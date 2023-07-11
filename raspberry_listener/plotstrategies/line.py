import pandas as pd
from matplotlib.axes import Axes
from datamodels.sources.framehandler import (
    FrameHandler,
    DataNotReadyException,
)
from matplotlib.lines import Line2D
from .plotstrategy import PlotStrategy


class LinePlot(PlotStrategy):
    def __init__(
        self,
        datasource: FrameHandler,
        keys: tuple,
        label: str | None = None,
    ):
        self.datasource = datasource
        self.keys = keys
        self.label = label

    def __str__(self):
        return "Line"

    def __call__(self, ax: Axes, **kwargs):
        try:
            series = self.get_timeindexed_series()
        except DataNotReadyException:
            return
        try:
            self.artist.set_xdata(series.index.to_numpy())
            self.artist.set_ydata(series.to_numpy())
            self.artist.recache()
        except AttributeError:
            self._artists = ax.plot(
                series.index.to_numpy(),
                series.to_numpy(),
                label=self.label,
                **kwargs,
            )

    def get_timeindexed_series(self) -> pd.Series:
        df = self.datasource.dataframe
        df = df.loc[*self.keys]
        assert isinstance(df, pd.DataFrame)
        series = df.get("reading")
        assert isinstance(series, pd.Series)
        return series

    @property
    def artist(self) -> Line2D:
        return self._artists[0]
