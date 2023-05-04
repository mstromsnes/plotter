from datatypes import DataSet
from drawwidget import DrawWidget
import numpy as np


class GraphUpdater:
    def __init__(self, graph: DrawWidget, title: str):
        self._last_timestamp: np.datetime64 | None = None
        self.graph = graph
        self.title = title

    def plot(self, data_tuple: DataSet):
        if data_tuple[0].size > 0:
            last_timestamp = data_tuple[0][-1]
            if self._last_timestamp != last_timestamp:
                self.graph.update_graph(data_tuple, self.title)
            self.graph.plot()
            self._last_timestamp = last_timestamp

    def set_title(self, title: str):
        self.title = title
