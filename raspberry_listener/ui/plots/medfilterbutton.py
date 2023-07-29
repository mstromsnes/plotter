from PySide6 import QtCore, QtGui, QtWidgets
from scipy.signal import medfilt


class MedFilterButton(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)

    class OddSpinBox(QtWidgets.QSpinBox):
        def validate(self, text: str, pos: int):
            validator = QtGui.QIntValidator()
            validator.setBottom(self.minimum())
            validator.setTop(self.maximum())
            state = validator.validate(text, pos)
            if state is QtGui.QValidator.State.Invalid:
                return state
            number = int(text)
            if number % 2 == 1:
                return QtGui.QValidator.State.Acceptable
            return QtGui.QValidator.State.Invalid

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.spinbox = self.OddSpinBox()
        self.label = QtWidgets.QLabel("Median Filter")
        self.spinbox.setValue(1)
        self.spinbox.setMinimum(1)
        self.spinbox.setSingleStep(2)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.label)
        self.spinbox.valueChanged.connect(self.valueChanged)

    def medfilt(self, data):
        x, y = data
        return x, medfilt(y, self.spinbox.value())
