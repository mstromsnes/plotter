from typing import Callable

from datamodels import DataTypeManager
from datathread import DataThreadController
from PySide6 import QtCore, QtGui, QtWidgets

from .plottab import DataTypeTabWidget


class DataSetList(QtWidgets.QDialog):
    # Dialog widget for choosing a dataset to load
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

    def update_datasets(self, datasets: list[str]):
        self.listwidget.clear()
        self.listwidget.addItems(datasets)

    def choose_dataset_and_close(self):
        # After choosing a dataset, close the widget
        chosen_item = self.listwidget.currentItem()
        if chosen_item is not None:
            self.load_dataset.emit(chosen_item.text())
        self.close()


class DataPlotterWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        available_datasets: list[str],
        dataset_loader: Callable[[str], DataThreadController],
        datatype_manager: DataTypeManager,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.tab_widget = QtWidgets.QTabWidget()
        self.available_datasets = available_datasets
        self.dataset_loader = dataset_loader
        self.dataset_manager = datatype_manager
        self.tab_widgets: dict[str, DataTypeTabWidget] = {}
        self.setCentralWidget(self.tab_widget)
        self._loaded_datasets: set[str] = set()
        self._data_loading_threads = {}

        self.dataset_picker = DataSetList(self.available_datasets)
        self.dataset_picker.load_dataset.connect(self._load_dataset)

        self.set_menubar()

    def _load_dataset(self, name: str):
        if name not in self._loaded_datasets:
            thread = self.dataset_loader(name)
            self._loaded_datasets.add(name)
            self._data_loading_threads[name] = thread
            if name in self.available_datasets:
                self.available_datasets.remove(name)
            self.create_missing_datatype_tabs(self.dataset_manager)
            self.dataset_picker.update_datasets(self.available_datasets)

    def create_missing_datatype_tabs(self, datatype_manager: DataTypeManager):
        types = datatype_manager.get_types()
        for type in types:
            data_model = datatype_manager.get_model(type)
            if data_model.has_data():
                if not data_model.name() in self.tab_widgets:
                    tab = DataTypeTabWidget(data_model)
                    self.tab_widgets[data_model.name()] = tab
                    self.tab_widget.addTab(tab, data_model.name())

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
        dataset_action.triggered.connect(self.dataset_picker.show)

        menubar.addAction(dataset_action)
        add_plot_action = QtGui.QAction("Create &Plot", self)
        add_plot_action.setDisabled(True)
        menubar.addAction(add_plot_action)
