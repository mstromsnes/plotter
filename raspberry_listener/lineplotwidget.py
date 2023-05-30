from PySide6 import QtWidgets, QtGui, QtCore
from datatypes import DataSet, Sensor, SensorType
from datamediator import DataMediator
from drawwidget import DrawWidget
from matplotlib import rcParams
from scipy.signal import medfilt
import plotmanager
from plotstrategies import LinePlot


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
        datasource: DataMediator,
        parent: QtWidgets.QWidget | None = None,
        **kwargs,
    ):
        super().__init__(parent=parent)

        self.datasource = datasource
        self.navigation_layout.addWidget(SimplifyPlotSpinBox())
        self.manager = plotmanager.OneAxesPrSensorTypeManager(self, "Timeseries")

    @QtCore.Slot(SensorType, Sensor, bool)
    def toggle_line(self, sensor_type: SensorType, sensor: Sensor, checked: bool):
        if not checked:
            self.manager.remove_plotting_strategy(sensor_type, sensor)
        else:
            strategy = LinePlot(self.datasource, sensor_type, sensor)
            self.manager.add_plotting_strategy(strategy, sensor_type, sensor)

    def plot(self):
        self.manager.plot()
