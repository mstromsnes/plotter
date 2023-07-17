from ui.drawwidget import DrawWidget
from abc import abstractmethod


class PlotWidget(DrawWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    @abstractmethod
    def toggle_data(self, label, checked):
        pass

    @abstractmethod
    def plot(self):
        pass
