from PySide6 import QtWidgets, QtGui, QtCore
from datamediator import DataMediator


class IntEdit(QtWidgets.QLineEdit):
    def __init__(self, value: int, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        validator = QtGui.QIntValidator(0, 255, self)
        self.setValidator(validator)
        if 0 <= value <= 255:
            self.setText(str(value))
        sizepolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        self.setSizePolicy(sizepolicy)

    def get_num(self):
        return int(self.text())

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, 0)


class IPString:
    IpType = list[int | str] | list[int] | list[str]

    def __init__(self, filled_in_parts: IpType):
        self._string = self._make_string_from_list(filled_in_parts)

    def change_part(self, part: int, new_value: str):
        parts = self._string.split(".")
        parts[part] = new_value
        self._string = self._make_string_from_list(parts)

    @staticmethod
    def _make_string_from_list(
        filled_in_parts: IpType,
    ):
        return "".join([str(v) + "." for v in filled_in_parts])

    def get_ip(self) -> str:
        return self._string


class IPField(QtWidgets.QWidget):
    def __init__(
        self, filled_in_value: list[int], parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        sizepolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        layout = QtWidgets.QHBoxLayout()
        for i in range(4):
            field = IntEdit(filled_in_value[i])
            field.textChanged.connect(lambda new_value: self._update_ip(i, new_value))
            layout.addWidget(field)
            if i < 3:
                separator = QtWidgets.QLabel(".")
                layout.addWidget(separator)
        self.setLayout(layout)
        self.setSizePolicy(sizepolicy)

        self.ip = IPString(filled_in_value)

    def _update_ip(self, part: int, new_value: str):
        self.ip.change_part(part, new_value)

    def get_ip(self) -> str:
        return self.ip.get_ip()


class PortField(QtWidgets.QSpinBox):
    def __init__(self, value: int, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setMaximum(65536)
        self.setValue(value)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Maximum,
            )
        )

    def get_port(self) -> int:
        return self.value()


class ConnectWidget(QtWidgets.QWidget):
    def __init__(
        self,
        data_mediator: DataMediator,
        host: list[int],
        port: int,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.data_mediator = data_mediator
        layout = QtWidgets.QHBoxLayout()
        self.ipfield = IPField(host)
        self.portfield = PortField(port)
        self.connect_button = QtWidgets.QPushButton()
        button_text = "Disconnect" if self.data_mediator.is_connected() else "Connect"
        self.connect_button.setText(button_text)
        self._wire_up_connect_button()
        layout.addStretch(1)
        layout.addWidget(self.ipfield)
        layout.addWidget(QtWidgets.QLabel(":"))
        layout.addWidget(self.portfield)
        layout.addWidget(self.connect_button)
        self.setLayout(layout)

    def _wire_up_connect_button(self):
        def connect():
            self.data_mediator.connect(self.ipfield.get_ip(), self.portfield.get_port())
            self.connect_button.setText("Disconnect")

        def disconnect():
            self.data_mediator.disconnect()
            self.connect_button.setText("Connect")

        def on_click():
            if self.data_mediator.is_connected():
                disconnect()
            else:
                connect()

        self.connect_button.clicked.connect(on_click)


class Toolbar(QtWidgets.QToolBar):
    def __init__(
        self,
        data_mediator: DataMediator,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.connect_widget = ConnectWidget(data_mediator, [192, 168, 4, 141], 65431)
        self.addWidget(self.connect_widget)
