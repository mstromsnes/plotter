from functools import partial

from datamodels import DataIdentifier, DataTypeModel
from PySide6 import QtCore, QtGui, QtWidgets

SideBarButtonType = type[QtWidgets.QRadioButton] | type[QtWidgets.QCheckBox]


class SideBar(QtWidgets.QTreeView):
    data_toggled = QtCore.Signal(DataIdentifier, bool)

    def __init__(
        self,
        datatype_model: DataTypeModel,
        button_type: SideBarButtonType,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.datatype_model = datatype_model
        self.button_type = button_type
        self.tree_model = TreeModel(self.datatype_model)
        self.setModel(self.tree_model)
        self.tree_model.item_added.connect(self.add_widget_item)
        self.tree_model.build_complete_tree()
        self.header().hide()

    def button_toggled_fn(self, dataset: DataIdentifier, state: bool):
        self.data_toggled.emit(dataset, state)

    def add_widget_item(self, item: QtGui.QStandardItem, source_name: str):
        if not item.hasChildren():
            self.add_button(item, source_name)

    def add_button(self, item: QtGui.QStandardItem, source_label: str):
        label = item.text()
        button = self.button_type(label.upper())
        callback = partial(self.button_toggled_fn, DataIdentifier(source_label, label))
        button.toggled.connect(callback)
        item.setText("")
        self.setIndexWidget(item.index(), button)

    def widget(self):
        return self


class TreeModel(QtGui.QStandardItemModel):
    item_added = QtCore.Signal(QtGui.QStandardItem, str)

    def __init__(self, datatype_model: DataTypeModel):
        super().__init__(None)
        self.datatype_model = datatype_model
        self.datatype_model.dataline_registered.connect(self.add_item)
        self.sources: dict[str, QtGui.QStandardItem] = dict()
        self.setHorizontalHeaderLabels([""])

    def build_complete_tree(self):
        for source in self.datatype_model.get_source_names():
            dataset_names = self.datatype_model.get_data_name_from_source(source)
            self.add_source(source)
            for name in dataset_names:
                self.add_item(DataIdentifier(source, name))

    def add_source(self, source_name: str) -> None:
        source_item = QtGui.QStandardItem(source_name)
        self.sources[source_name] = source_item
        root_item = self.invisibleRootItem()
        root_item.appendRow(source_item)

    def add_item(self, dataset: DataIdentifier):
        # Get or make the source item
        source_name = dataset.source
        if source_name not in self.sources:
            self.add_source(source_name)
        source_item = self.sources[source_name]

        # Make the dataset item
        item_name = dataset.data
        item = QtGui.QStandardItem(item_name)
        source_item.appendRow(item)
        self.item_added.emit(item, source_name)
