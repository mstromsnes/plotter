from PySide6 import QtWidgets, QtGui, QtCore
from functools import partial
from dataclasses import dataclass


@dataclass
class TreeItem:
    children: list["TreeItem"]
    text: str | None
    callback_args: tuple[str, ...] | None


class SidebarDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        if index.data(QtCore.Qt.ItemDataRole.UserRole) is not None:
            option.text = ""
        return super().paint(painter, option, index)


class SideBar(QtWidgets.QTreeView):
    button_toggled = QtCore.Signal(tuple, str, bool)

    def __init__(self, model: QtGui.QStandardItemModel, parent=None):
        super().__init__(parent=parent)
        self.setModel(model)
        self.setItemDelegate(SidebarDelegate())
        self._button_widgets = []
        for row in range(model.rowCount()):
            self.add_buttons(row)

    def button_toggled_fn(self, dataset_key: tuple, label: str | None, state: bool):
        self.button_toggled.emit(dataset_key, label, state)

    def add_buttons(self, row):
        index = self.model().index(row, 0)
        if (dataset_key := index.data(QtGui.Qt.ItemDataRole.UserRole)) is not None:
            button = QtWidgets.QCheckBox()
            self._button_widgets.append(button)
            label = index.data(QtGui.Qt.ItemDataRole.DisplayRole)
            if type(label) is str:
                label = label.strip()
            else:
                label = None
            callback = partial(self.button_toggled_fn, dataset_key, label)
            button.toggled.connect(callback)
            self.setIndexWidget(index, button)
        else:
            model = index.model()
            for row in range(model.rowCount()):
                self.add_buttons(row)

    @QtCore.Slot()
    def rowsInserted(
        self,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        start: int,
        end: int,
    ) -> None:
        print(parent.data)
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
        text = f"    {item.text}" if item.text is not None else "N/A"
        print(text)
        tree_item = QtGui.QStandardItem()
        tree_item.setText(text)
        tree_item.setData(item.callback_args, QtGui.Qt.ItemDataRole.UserRole)
        return tree_item
