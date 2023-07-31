from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import Self

from datamodels import DataTypeModel
from PySide6 import QtCore, QtGui, QtWidgets


@dataclass
class TreeItem:
    children: list[Self]
    text: str


class SideBar(QtWidgets.QTreeView):
    button_toggled = QtCore.Signal(str, bool)

    def __init__(
        self, datatype_model: DataTypeModel, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent=parent)
        self.datatype_model = datatype_model
        self.tree_root = self.make_tree()
        treeViewModel = TreeModel(self.tree_root)
        self.setModel(treeViewModel)
        self._button_widgets = []
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
        self.button_toggled.emit(label, state)

    def add_buttons(self, item: QtGui.QStandardItem):
        if item.hasChildren():
            for row in range(item.rowCount()):
                self.add_buttons(item.child(row, 0))
        else:
            label = item.data(QtGui.Qt.ItemDataRole.DisplayRole)
            button = QtWidgets.QCheckBox()
            self._button_widgets.append(button)
            callback = partial(self.button_toggled_fn, label)
            button.toggled.connect(callback)
            item.setData(f"    {label.upper()}", QtGui.Qt.ItemDataRole.DisplayRole)
            self.setIndexWidget(item.index(), button)

    @QtCore.Slot()
    def rowsInserted(
        self,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        start: int,
        end: int,
    ) -> None:
        return super().rowsInserted(parent, start, end)


class TreeModel(QtGui.QStandardItemModel):
    def __init__(self, tree: TreeItem):
        super().__init__(None)
        self.setHorizontalHeaderLabels([tree.text])
        self.items = []
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
