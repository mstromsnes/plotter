from PySide6 import QtWidgets, QtCore, QtGui
from sources import FrameHandler
from datathread import DataThreadController
from typing import Callable


class DataSetList(QtWidgets.QDialog):
    load_dataset = QtCore.Signal(str)

    def __init__(self, datasets: list[str], parent=None):
        super().__init__(parent)
        self.listwidget = QtWidgets.QListWidget()
        self.listwidget.addItems(datasets)

        self.load_button = QtWidgets.QPushButton("&Load Dataset")

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.addWidget(self.listwidget)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.load_button)
        self.v_layout.addLayout(self.button_layout)

        self.load_button.clicked.connect(self.choose_dataset_and_close)
        self.listwidget.doubleClicked.connect(self.choose_dataset_and_close)

    def choose_dataset_and_close(self):
        chosen_item = self.listwidget.currentItem().text()
        self.load_dataset.emit(chosen_item)
        self.close()


class DataPlotterWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        available_datasets: list[str],
        dataset_loader: Callable[[str], tuple[FrameHandler, DataThreadController]],
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.tab_widget = QtWidgets.QTabWidget()
        self.available_datasets = available_datasets
        self.dataset_loader = dataset_loader
        self.tab_widgets: dict[str, PlotTabWidget] = {}
        self.set_menubar()
        self.tab_widget.currentChanged.connect(self.update_visible_plot)
        self.setCentralWidget(self.tab_widget)
        self._loaded_datasets = {}
        self._data_loading_threads = {}

    def create_plots(self, handler: FrameHandler):
        model = handler.model()
        for tab_name in model.groups():
            tab = PlotTabWidget(handler, model.datasets(tab_name), tab_name)
            self.tab_widgets[tab_name] = tab
            self.tab_widget.addTab(tab, tab_name)

    def update_plots(self):
        for widget in self.tab_widgets.values():
            widget.update_plot()

    def update_visible_plot(self):
        for widget in self.tab_widgets.values():
            if widget.isVisible():
                widget.update_plot()

    def set_menubar(self):
        menubar = self.menuBar()

        dataset_action = QtGui.QAction("Open &Dataset", self)
        dataset_action.triggered.connect(self.pick_dataset_to_load)

        menubar.addAction(dataset_action)
        add_plot_action = QtGui.QAction("Create &Plot", self)
        add_plot_action.setDisabled(True)
        menubar.addAction(add_plot_action)

    def pick_dataset_to_load(self):
        def load_dataset(name: str):
            if name not in self._loaded_datasets.keys():
                handler, thread = self.dataset_loader(name)
                self._loaded_datasets[name] = handler
                self._data_loading_threads[name] = thread
                if name in self.available_datasets:
                    self.available_datasets.remove(name)
                self.create_plots(handler)

        self.dataset_picker = DataSetList(list(self.available_datasets))
        self.dataset_picker.load_dataset.connect(load_dataset)
        self.dataset_picker.show()
