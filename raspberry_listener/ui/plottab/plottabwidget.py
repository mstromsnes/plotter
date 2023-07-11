from datamodels.sources.framehandler import FrameHandler, ModelDataSetReturnType
from plotstrategies.line import LinePlot
from PySide6 import QtWidgets
from ui.plots import LinePlotWidget

from .sidebar import SideBar, TreeItem, TreeModel


class PlotTabWidget(QtWidgets.QTabWidget):
    def __init__(
        self,
        datasource: FrameHandler,
        data_sets: ModelDataSetReturnType,
        tab_name: str,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.datasource = datasource
        self.data_sets = data_sets
        self.linewidget = LinePlotWidget(self.datasource)
        line_sets = data_sets[LinePlot]
        children = [TreeItem([], keys[-1], keys) for keys in line_sets]
        self.tree_children = children
        self.tree = TreeItem(children, f"\t{tab_name}", None)
        self.model = TreeModel(self.tree)
        self.sidebar = SideBar(self.model)
        self.intermediate_widget = self.widget_with_sidebar(
            self.linewidget, self.sidebar
        )
        self.sidebar.button_toggled.connect(self.linewidget.toggle_line)
        self.addTab(self.intermediate_widget, "Line")
        self.currentChanged.connect(self.update_plot)

    def update_plot(self):
        self.linewidget.plot()

    @staticmethod
    def widget_with_sidebar(plot_widget, sidebar):
        widget = QtWidgets.QWidget(None)
        hbox = QtWidgets.QHBoxLayout(widget)
        hbox.addWidget(plot_widget, stretch=1)
        hbox.addWidget(sidebar)
        return widget
