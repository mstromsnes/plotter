from enum import Enum, auto

from attrs import define, field
from datamodels import DataIdentifier
from matplotlib.axes import Axes
from sources import DataNotReadyException

from ..axes import AxesStrategy
from ..plotstrategy import PlotStrategy


class PlotStatus(Enum):
    Enabled = auto()
    Disabled = auto()
    Hidden = auto()


@define
class PlotItem:
    identifier: DataIdentifier
    plot_strategy: PlotStrategy
    _status: PlotStatus
    _axes_strategy: AxesStrategy

    @property
    def ax(self) -> Axes:
        return self._axes_strategy.from_dataidentifier(self.identifier)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status: PlotStatus):
        if new_status == self.status:
            return

        def transition_from_hidden(new_status: PlotStatus):
            if new_status == PlotStatus.Disabled:
                self._axes_strategy.remove_plot(self.identifier)

        def transition_from_enabled(new_status: PlotStatus):
            if new_status == PlotStatus.Disabled:
                self.plot_strategy.remove_artist()
                self._axes_strategy.remove_plot(self.identifier)
            elif new_status == PlotStatus.Hidden:
                self.plot_strategy.remove_artist()

        def transition_from_disabled(new_status: PlotStatus):
            if new_status == PlotStatus.Enabled:
                self._axes_strategy.add_plot(self.identifier)
            elif new_status == PlotStatus.Hidden:
                self._axes_strategy.add_plot(self.identifier)

        match self.status:
            case PlotStatus.Enabled:
                transition_from_enabled(new_status)
            case PlotStatus.Disabled:
                transition_from_disabled(new_status)
            case PlotStatus.Hidden:
                transition_from_hidden(new_status)
        self._status = new_status

    @property
    def visible(self) -> bool:
        return self.status == PlotStatus.Enabled

    @property
    def figure(self):
        return self.ax.figure

    @property
    def root_figure(self):
        fig = self.figure
        while fig != fig.get_figure():
            fig = fig.get_figure()
        return fig

    def draw_plot(self):
        try:
            self.plot_strategy(self.ax)
        except DataNotReadyException:
            pass
