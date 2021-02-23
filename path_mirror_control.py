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


class PlantAlong(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.per_step = UI.PositionControl(label='Set Plant Step(%d)')
        self.start_pos = UI.PositionControl(label='Set Start Position(%d)')
        self.end_pos = UI.PositionControl(label='Set End Position(%d)')

        layout.addWidget(self.per_step)
        layout.addWidget(self.start_pos)
        layout.addWidget(self.end_pos)
        self.setLayout(layout)

        self.setTitle("PlantAlong")
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")


        if parent:
            parent.addWidget(self)

    def apply(self):
        # for plant along
        single_step = self.per_step.value
        start_pos = self.start_pos.value
        end_pos = self.end_pos.value
        print("ui['plant_along'].value: %.2f" % single_step)

        objs = RLPy.RScene.GetSelectedObjects()
        origin_path_pos = 0

        try:
            obj = objs[0]
            path_pos_control = obj.GetControl("PathPosition")
            current_time = RLPy.RGlobal.GetTime()
            path_pos_control.GetValue(current_time, origin_path_pos)

            # get transform control and origin transform
            transform_control = obj.GetControl("Transform")
            transform_key = RLPy.RTransformKey()
            transform_control.GetTransformKey(current_time, transform_key)
            origin_transform = transform_key.GetTransform()


            i = start_pos
            while i <= end_pos:
                print("i: %.2f" % i)
                # set path position key
                path_pos_control.SetValue(current_time, i)
                obj.Update()

                # get x, y, z
                transform = transform_key.GetTransform()

                # let clone transform equal to origin
                clone = obj.Clone()
                clone_transform_control = clone.GetControl("Transform")
                clone_transform_key = RLPy.RTransformKey()
                clone_transform_control.GetTransformKey(current_time, clone_transform_key)
                clone_transform_key.SetTransform(transform)

                i += single_step

            print("Finish path control value apply")
            # reset origin obj path position key
            path_pos_control.SetValue(current_time, origin_path_pos)
            transform_key.SetTransform(origin_transform)
        except Exception as e:
            print(e)