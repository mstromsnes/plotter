import numpy as np

from drawwidget import DrawWidget


class LinePlotWidget(DrawWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line = None
        # self.ax.format_coord = self.format_coord

    def update_graph(self, data: np.ndarray, title: str):
        self._time, self._data, self._cnt = data
        self._title = title

    @DrawWidget.draw
    def plot(self, **kwargs):
        if self.line is None and self._cnt > 0:
            (self.line,) = self.ax.plot(
                self._time[: self._cnt], self._data[: self._cnt], **kwargs
            )
        elif self.line is not None:
            self.line.set_xdata(self._time[: self._cnt])
            self.line.set_ydata(self._data[: self._cnt])

        self.ax.set_title(self._title)

    # @staticmethod
    # def format_coord(x: float, y: float):
    #     """Instead of labeling coordinates as floats, label them as discrete points using integer values"""
    #     x = int(x + 0.5)
    #     y = int(y + 0.5)
    #     return f"{x=}, {y=}"
