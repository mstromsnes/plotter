from functools import partial
from weakref import finalize

from datamodels import DataIdentifier, DataTypeModel
from PySide6 import QtCore, QtGui, QtWidgets

SideBarButtonType = type[QtWidgets.QRadioButton] | type[QtWidgets.QCheckBox]


class SideBar(QtWidgets.QTreeView):
    data_toggled = QtCore.Signal(tuple, bool)

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
        self.tree_model.source_added.connect(self.add_source)
        self.tree_model.build_complete_tree()
        self.header().hide()

    def button_toggled_fn(self, dataset: DataIdentifier, state: bool):
        self.data_toggled.emit(dataset, state)

    def add_source(self, source_item: QtGui.QStandardItem):
        source_name = source_item.text()
        if source_item.hasChildren():
            for row in range(source_item.rowCount()):
                self.add_button(source_item.child(row, 0), source_name)

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
    source_added = QtCore.Signal(QtGui.QStandardItem)

    def __init__(self, datatype_model: DataTypeModel):
        super().__init__(None)
        self.datatype_model = datatype_model
        self.datatype_model.register_observer(self.add_source)
        self._finalizer = finalize(
            self, self.datatype_model.remove_observer, self.add_source
        )
        self.setHorizontalHeaderLabels([""])

    def build_complete_tree(self):
        for source in self.datatype_model.get_source_names():
            self.add_source(source)

    def add_source(self, source_name: str) -> None:
        dataset_names = self.datatype_model.get_data_name_from_source(source_name)
        source_item = QtGui.QStandardItem(source_name)
        for name in dataset_names:
            data_item = QtGui.QStandardItem(name)
            source_item.appendRow(data_item)
        root_item = self.invisibleRootItem()
        root_item.appendRow(source_item)
        self.source_added.emit(source_item)
