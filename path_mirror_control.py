import RLPy
from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance
from PySide2 import QtCore
import ui_components as UI



class PathMirrorTabWidget(QtWidgets.QTabWidget):
    def __init__(self):
        super(PathMirrorTabWidget, self).__init__()

        self.prop_widget = PropConfigControl()
        self.place_widget = PlaceConfigControl()

        self.addTab(self.prop_widget, "Property")
        self.addTab(self.place_widget, "Place")


    def handle_selected_change_event(self):
        self.currentWidget().handle_selected_change_event()


class PlaceConfigControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PlaceConfigControl, self).__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        ui = {}
        ui["selection"] = UI.SelectionControl(0, "Place", parent=self.layout)
        self.ui = ui.copy()
        self.selected_objects = []
        self.refresh()

        if parent:
            parent.addWidget(self)

    @property
    def selection(self):
        return self.selected_objects[0]

    def handle_selected_change_event(self):
        self.refresh()
        try:
            name = self.selected_objects[0].GetName()
            self.ui['selection'].set_item_label(1, name)
        except:
            return

    def refresh(self):
        self.selected_objects = self.__get_selected_objects()

    def __get_selected_objects(self):
        return RLPy.RScene.GetSelectedObjects()


class PropConfigControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # ui

        ui = {}
        ui['selection'] = UI.SelectionControl(0, "Property", parent=self.layout)
        # ui['vectors'] = UI.Vector3Control(parent=self.layout)
        # ui['clones'] = UI.SliderControl("Clone", parent=self.layout)

        # data
        self.ui = ui.copy()
        self.selected_objects = []
        self.refresh()

        if parent:
            parent.addWidget(self)

    @property
    def selection(self):
        return self.selected_objects[0]


    def handle_selected_change_event(self):
        self.refresh()
        try:
            name = self.selected_objects[0].GetName()
            self.ui['selection'].set_item_label(1, name)
        except:
            return

    def refresh(self):
        self.selected_objects = self.__get_selected_objects()

    def __get_selected_objects(self):
        return RLPy.RScene.GetSelectedObjects()


class MirrorAxis(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()

        self._x_box = QtWidgets.QCheckBox(text="X")
        self._y_box = QtWidgets.QCheckBox(text="Y")
        self._z_box = QtWidgets.QCheckBox(text="Z")

        layout.addWidget(self._x_box)
        layout.addWidget(self._y_box)
        layout.addWidget(self._z_box)

        self.setLayout(layout)
        self.setTitle("Mirror Axis")
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        self.__mirror_axis = "X"
        if parent:
            parent.addWidget(self)


class PlantAlong(UI.SliderControl):
    def __init__(self, parent=None):
        super().__init__(label='PlantAlong', span=(0, 1), single_step=0.1)

        if parent:
            parent.addWidget(self)