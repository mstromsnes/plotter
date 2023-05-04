from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, DataHandler
from drawwidget import DrawWidget, UnpackedDataSet
from matplotlib import rcParams, axes
from scipy.signal import medfilt

from matplotlib.ticker import MaxNLocator


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

    def __init__(self, datatype: DataHandler, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.datatype = datatype
        self.spinbox = self.OddSpinBox()
        self.label = QtWidgets.QLabel("Median Filter")
        self.spinbox.setValue(1)
        self.spinbox.setMinimum(1)
        self.spinbox.setSingleStep(2)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.label)
        self.spinbox.valueChanged.connect(self.valueChanged)

    def medfilt(self, data: UnpackedDataSet) -> UnpackedDataSet:
        x, y = data
        return x, medfilt(y, self.spinbox.value())


class SimplifyPlotSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setValue(rcParams["path.simplify_threshold"])
        self.valueChanged.connect(self.update_threshold)
        self.setSingleStep(0.1)
        self.setMinimum(0)
        self.setMaximum(1)

    @QtCore.Slot(float)
    def update_threshold(self, v):
        rcParams["path.simplify_threshold"] = v


class LinePlotWidget(DrawWidget):
    def __init__(
        self,
        datatype: DataHandler,
        use_integer=False,
        parent: QtWidgets.QWidget | None = None,
        **kwargs
    ):
        super().__init__(parent=parent)
        self.datatype = datatype
        self.line = None
        self.medfilt_spinbox = MedFilterButton(self.datatype)
        self.navigation_layout.addWidget(SimplifyPlotSpinBox())
        self.navigation_layout.addWidget(self.medfilt_spinbox)
        self.add_postprocessing_function(self.medfilt_spinbox.medfilt)

        self.medfilt_spinbox.valueChanged.connect(self.plot)
        self.ax: axes.Axes = self.figure.add_subplot(**kwargs)
        if use_integer:
            self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    def update_graph(self, dataset: DataSet, title: str):
        self._dataset = dataset
        self._title = title

    @DrawWidget.draw
    def plot(self, *args, **kwargs):
        dataset = self._dataset
        for func in self._postprocessing_functions:
            dataset = func(dataset)
        time, data = dataset
        if self.line is not None:
            self.line.set_xdata(time)
            self.line.set_ydata(data)
        elif data.size > 0 or self._initial_kwargs != kwargs:
            (self.line,) = self.ax.plot(time, data, **kwargs)
            self._initial_kwargs = kwargs

        self.ax.set_title(self._title)

    def _rescale(self):
        self.ax.relim()
        self.ax.autoscale()
