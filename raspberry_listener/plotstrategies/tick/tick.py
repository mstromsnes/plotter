from typing import Callable

from datamodels import DataTypeModel
from matplotlib.axes import Axes
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.projections.polar import PolarAxes
from matplotlib.ticker import (
    Formatter,
    FuncFormatter,
    LinearLocator,
    Locator,
    NullFormatter,
    NullLocator,
)
from numpy import pi

TickStrategy = Callable[[Axes], None]


def concise_date_formatter(ax: Axes, model: DataTypeModel):
    ax.yaxis.set_major_formatter("{x}" + f"{model.unit.short}")
    locator = AutoDateLocator()
    formatter = ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


def flat_time_of_day_formatter(ax: Axes):
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: pos))
    ax.xaxis.set_major_locator(LinearLocator(numticks=25))
    ax.yaxis.set_inverted(True)
    ax.set_xlim(0, 2 * pi)


def clock_time_of_day_formatter(ax: PolarAxes):
    angle_step = 360 // 24
    angles = (float(i * angle_step) for i in range(24))
    labels = (str(i) for i in range(24))
    ax.set_thetagrids(tuple(angles), tuple(labels))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetalim(0, 2 * pi)
    ax.yaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_locator(NullLocator())


def major_tickformatter(
    x_formatter: Formatter | None = None,
    y_formatter: Formatter | None = None,
    *,
    x_locator: Locator | None = None,
    y_locator: Locator | None = None,
):
    def formatter_fn(ax: Axes):
        if x_locator is not None:
            ax.xaxis.set_major_locator(x_locator)
        if y_locator is not None:
            ax.yaxis.set_major_locator(y_locator)
        if x_formatter is not None:
            ax.xaxis.set_major_formatter(x_formatter)
        if y_formatter is not None:
            ax.yaxis.set_major_formatter(y_formatter)

    return formatter_fn


def minor_tickformatter(
    x_formatter: Formatter | None = None,
    y_formatter: Formatter | None = None,
    *,
    x_locator: Locator | None = None,
    y_locator: Locator | None = None,
):
    def formatter_fn(ax: Axes):
        if x_locator is not None:
            ax.xaxis.set_major_locator(x_locator)
        if y_locator is not None:
            ax.yaxis.set_major_locator(y_locator)
        if x_formatter is not None:
            ax.xaxis.set_major_formatter(x_formatter)
        if y_formatter is not None:
            ax.yaxis.set_major_formatter(y_formatter)

    return formatter_fn
