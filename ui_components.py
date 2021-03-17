import RLPy
from PySide2 import QtWidgets
from functools import partial
from PySide2 import QtCore
from PySide2.QtCore import *


class SelectionControl(QtWidgets.QWidget):
    def __init__(self, id, label, height=80, parent=None):
        super().__init__()

        self.id = id
        self.list_view = QtWidgets.QListView()

        # self.setStyleSheet("QListView {border:1px solid rgb(72, 72, 72);}")
        self.list_view.setFixedHeight(height)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QtWidgets.QLabel(label))
        self.layout().addWidget(QtWidgets.QLineEdit(""))
        # self.layout().addWidget(self.list_view)

        if parent:
            parent.addWidget(self)

    def set_item_label(self, item_idx, text):
        self.layout().itemAt(item_idx).widget().setText(text)


class Vector3Control(QtWidgets.QWidget):
    def __init__(self, label='Vector', span=(-100, 0, 100), checked=[True, True, True], parent=None):
        super().__init__()
        self.__enabled = checked
        self.__value = [span[2], span[2], span[2]]
        self.__vector = {"x": span[2], "y": span[2], "z": span[2]}

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(0, 0, 0, 0)

        def enable_disable(spinbox, axis, cond):
            spinbox.setEnabled(cond)
            index = {"X": 0, "Y": 1, "Z": 2}[axis]
            self.__enabled[index] = cond > 0

        def change_value(axis, value):
            self.__vector[axis.lower()] = value
            index = {"X": 0, "Y": 1, "Z": 2}[axis]
            self.__value[index] = value

        for axis, checked in {"X": checked[0], "Y": checked[1], "Z": checked[2]}.items():
            layout = QtWidgets.QVBoxLayout()
            top_layout = QtWidgets.QHBoxLayout()

            checkbox = QtWidgets.QCheckBox()
            spinbox = QtWidgets.QDoubleSpinBox(
                minimum=span[0], maximum=span[2], value=span[1])

            top_layout.addWidget(checkbox)
            top_layout.addWidget(QtWidgets.QLabel("%s %s" % (label, axis)))
            top_layout.addStretch() #### I don't understand

            layout.addLayout(top_layout)
            layout.addWidget(spinbox)

            checkbox.setEnabled(checked)
            spinbox.setEnabled(checked)

            checkbox.stateChanged.connect(partial(enable_disable, spinbox, axis))
            spinbox.valueChanged.connect(partial(change_value, axis))

            self.layout().addLayout(layout)

        if parent:
            parent.addWidget(self)


class SliderControlWidget(QtWidgets.QWidget):
    value_change = Signal(float)

    def __init__(self,  span=(0, 1), value=0, single_step=0.01, parent=None, factor=100):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal,
                                         maximum=span[1]*factor, minimum=span[0]*factor, value=value)
        self._slider.setSingleStep(1)
        self._slider.valueChanged.connect(lambda x: self.__change_value(x, 'spinbox'))

        self._spinbox = QtWidgets.QDoubleSpinBox(maximum=span[1], minimum=span[0], value=value, singleStep=single_step)
        self._spinbox.valueChanged.connect(lambda x: self.__change_value(x, 'slider'))

        layout.addWidget(self._slider)
        layout.addWidget(self._spinbox)

        self.setLayout(layout)

        self.__value = value
        self.__span = span
        self.__factor = factor

        if parent:
            parent.addWidget(self)

    def __block_signals(self, cond=True):
        self._spinbox.blockSignals(cond)
        self._slider.blockSignals(cond)

    def __change_value(self, value, item: str):
        self.__block_signals()
        if item == 'spinbox':
            self.__value = value / self.__factor
            self._spinbox.setValue(self.__value)
        elif item == 'slider':
            self.__value = value
            self._slider.setValue(value * self.__factor)
        self.__block_signals(False)
        self.value_change.emit(self.__value)

    @property
    def value(self):
        return self.__value

    @property
    def minimum(self):
        return self._spinbox.minimum()

    @minimum.setter
    def minimum(self, value):
        self._spinbox.setMinimum(value)
        self._slider.setMinimum(value * self.__factor)

    @value.setter
    def value(self, val):
        self.__value = clamp(val, self.__span[0], self.__span[1])
        self.__block_signals()
        self._spinbox.setValue(self.__value)
        self._slider.setValue(self.__value * self.__factor)
        self.__block_signals(False)


class PositionControl(QtWidgets.QWidget):
    def __init__(self, label, span=(0, 1), single_step=0.01, value=0, state=True):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.checkbox = QtWidgets.QCheckBox(text=label)
        self.checkbox.setChecked(state)
        self.checkbox.stateChanged.connect(self.on_check_changed)

        self._slider = SliderControlWidget(span=span, value=value, single_step=single_step)
        self._slider.setEnabled(state)

        layout.addWidget(self.checkbox)
        layout.addWidget(self._slider)
        self.setLayout(layout)

        self.__default_value = value

    @property
    def value(self):
        if self.checkbox.isChecked():
            return self._slider.value
        else:
            return self.__default_value
    @property
    def minimum(self):
        return self._slider.minimum

    @value.setter
    def value(self, value):
        self._slider.value = value

    @minimum.setter
    def minimum(self, value):
        self._slider.minimum = value

    def on_check_changed(self):
        enable = self.checkbox.isChecked()
        self._slider.setEnabled(enable)
        if ~enable:
            self._slider.value = self.__default_value


class Button(QtWidgets.QPushButton):
    def __init__(self, label="Button", enabled=True, parent=None):
        super(Button, self).__init__(label)

        self.setFixedHeight(25)
        self.setEnabled(enabled)

        if parent:
            parent.addWidget(self)


def clamp(amount, value1, value2):
    __min = value1
    __max = value2
    if (value1 > value2):
        __max = value1
        __min = value2
    if (amount < __min):
        return __min
    if (amount > __max):
        return __max
    return amount