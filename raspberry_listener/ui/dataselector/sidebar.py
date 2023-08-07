from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import Callable, Self

from datamodels import DataTypeModel
from PySide6 import QtCore, QtGui, QtWidgets


@dataclass
class TreeItem:
    children: list[Self]
    text: str


SideBarButtonType = type[QtWidgets.QRadioButton] | type[QtWidgets.QCheckBox]


class SideBar(QtWidgets.QTreeView):
    data_toggled = QtCore.Signal(str, bool)

    def __init__(
        self,
        datatype_model: DataTypeModel,
        button_type: SideBarButtonType,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.datatype_model = datatype_model
        self.tree_root = self.make_tree()
        treeViewModel = TreeModel(self.tree_root)
        self.setModel(treeViewModel)
        self.button_type = button_type
        self._button_widgets: list[QtWidgets.QWidget] = []
        self._callbacks: list[partial[None]] = []
        self.add_buttons(treeViewModel.invisibleRootItem())

    def make_tree(self):
        data_set_names = self.datatype_model.get_dataset_names()
        sources = defaultdict(list)
        for name in data_set_names:
            sources[self.datatype_model.get_source_name(name)].append(name)
        source_nodes = []
        for source_name, datasets in sources.items():
            leaf_nodes = [TreeItem([], dataset_name) for dataset_name in datasets]
            source_node = TreeItem(leaf_nodes, source_name)
            source_nodes.append(source_node)
        tree_root = TreeItem(source_nodes, "")
        return tree_root

    def button_toggled_fn(self, label: str, state: bool):
        self.data_toggled.emit(label, state)

    def add_buttons(self, item: QtGui.QStandardItem):
        if item.hasChildren():
            for row in range(item.rowCount()):
                self.add_buttons(item.child(row, 0))
        else:
            label = item.data(QtGui.Qt.ItemDataRole.DisplayRole)
            assert isinstance(label, str)
            button = self.button_type(label.upper())
            self._button_widgets.append(button)
            callback = partial(self.button_toggled_fn, label)
            button.toggled.connect(callback)
            self._callbacks.append(callback)
            item.setData("", QtGui.Qt.ItemDataRole.DisplayRole)
            self.setIndexWidget(item.index(), button)

    def widget(self):
        return self


class TreeModel(QtGui.QStandardItemModel):
    def __init__(self, tree: TreeItem):
        super().__init__(None)
        self.setHorizontalHeaderLabels([tree.text])
        self.items: list[QtGui.QStandardItem] = []
        for child in tree.children:
            self.appendRow(self.build_tree(child))

    def build_tree(self, tree: TreeItem):
        tree_item = self.fill_item(tree)
        for child in tree.children:
            tree_item.appendRow(self.build_tree(child))
        self.items.append(tree_item)
        return tree_item

    def fill_item(self, item: TreeItem) -> QtGui.QStandardItem:
        text = f"{item.text}" if item.text is not None else "N/A"
        tree_item = QtGui.QStandardItem()
        tree_item.setText(text)
        return tree_item
