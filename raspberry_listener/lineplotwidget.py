from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet
from drawwidget import DrawWidget
from typing import Callable
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

    def __init__(self, parent: QtWidgets.QWidget | None = None):
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

    def medfilt(self, data: DataSet) -> DataSet:
        x, y = data
        return x, medfilt(y, self.spinbox.value())


class LinePlotWidget(DrawWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.line = None
        self._preprocessing_functions = []
        self.medfilt_spinbox = MedFilterButton()
        self.navigation_layout.insertWidget(-2, self.medfilt_spinbox)
        self.add_preprocessing_function(self.medfilt_spinbox.medfilt)

        @QtCore.Slot()
        def apply_preprocessing_and_plot():
            self.update_graph(self._dataset, self._title)
            self.plot()

        self.medfilt_spinbox.valueChanged.connect(
            lambda _: apply_preprocessing_and_plot()
        )

    def add_preprocessing_function(self, func: Callable[[DataSet], DataSet]):
        self._preprocessing_functions.append(func)

    def update_graph(self, dataset: DataSet, title: str):
        self._dataset = dataset
        self._title = title

    @DrawWidget.draw
    def plot(self, **kwargs):
        dataset = self._dataset
        for func in self._preprocessing_functions:
            dataset = func(dataset)
        time, data = dataset
        if self.line is not None:
            self.line.set_xdata(time)
            self.line.set_ydata(data)
        elif data.size > 0 or self._initial_kwargs != kwargs:
            (self.line,) = self.ax.plot(time, data, **kwargs)
            self._initial_kwargs = kwargs

        self.ax.set_title(self._title)
