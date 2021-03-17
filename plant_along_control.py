import RLPy
from PySide2 import QtWidgets
import ui_components as UI
from random import randint


class ObjectsManageWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        contain_btn_layout = QtWidgets.QHBoxLayout()
        contain_list_layout = QtWidgets.QHBoxLayout()

        self._contain_widget = QtWidgets.QListWidget()
        self._contain_widget.setAcceptDrops(True)
        self._contain_widget.setDragEnabled(True)
        self._contain_widget.model().rowsMoved.connect(self.refresh_switch_items)
        self._contain_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self._add_btn = QtWidgets.QPushButton(text='add')
        self._add_btn.clicked.connect(self.__add_click)

        self._remove_btn = QtWidgets.QPushButton(text='remove')
        self._remove_btn.clicked.connect(self.__remove_click)

        contain_btn_layout.addWidget(self._add_btn)
        contain_btn_layout.addWidget(self._remove_btn)
        contain_list_layout.addWidget(self._contain_widget, 1)

        layout.addLayout(contain_list_layout)
        layout.addLayout(contain_btn_layout)
        self.setLayout(layout)

        self.__items = []

    def __add_item(self, c_obj):

        name = c_obj.GetName()
        item = QtWidgets.QListWidgetItem()
        item.setText(name)
        self._contain_widget.addItem(item)

        self.__items.append({
            "item": item,
            "c_obj": c_obj
        })

    def __add_click(self):
        c_objects = RLPy.RScene.GetSelectedObjects()
        for c_obj in c_objects:
            self.__add_item(c_obj)

    def __remove_item(self, value, key):
        for idx, item_dict in enumerate(self.__items):
            if item_dict[key] is value:
                self.__items.pop(idx)
                idx = self._contain_widget.row(item_dict['item'])
                self._contain_widget.takeItem(idx)

    def __remove_click(self):
        selected_items = self._contain_widget.selectedItems()
        for item in selected_items:
            self.__remove_item(item, 'item')

    def __update_name(self, obj):
        for item_dict in self.__items:
            if item_dict['c_obj'] == obj:
                name = obj.GetName()
                # item_dict['item'].setText(0, name)
                item_dict['item'].setText(name)

    def refresh(self):
        c_objs = RLPy.RScene.FindObjects(RLPy.EObjectType_Object |
            RLPy.EObjectType_Avatar |
            RLPy.EObjectType_Prop |
            RLPy.EObjectType_Camera |
            RLPy.EObjectType_Particle)

        w_objs = [item_dict['c_obj'] for item_dict in self.__items]

        # update the item's name in widget
        for obj in c_objs:
            if obj in w_objs:
                self.__update_name(obj)

        for obj in w_objs:
            if obj not in c_objs:
                self.__remove_item(obj, key='c_obj')

    def refresh_switch_items(self):
        new_items = []
        for row in range(self._contain_widget.count()):
            item = self._contain_widget.item(row)
            item_dict = self.__find_item_by_name(item.text())
            if item_dict:
                new_items.append(item_dict)
        self.__items = new_items

    def clear(self):
        self._contain_widget.clear()
        self.__items.clear()

    def __find_item_by_name(self, name):
        for item in self.__items:
            if item['c_obj'].GetName() == name:
                return item
        return None

    @property
    def items(self):
        return self.__items


class StepControl(UI.PositionControl):
    def __init__(self):
        super().__init__(label='Set Plant Constant Step(%d)', value=0.1)

    @property
    def value(self):
        if self.checkbox.checkState():
            return self.slider.value
        else:
            return randint(0, 10) / 100


class Position(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        
        self.step_control = StepControl()
        
        self.start_pos_control = UI.PositionControl(label='Set Start Position(%d)')

        self.end_pos_control = UI.PositionControl(label='Set End Position(%d)', value=1)

        layout.addWidget(self.step_control)
        layout.addWidget(self.start_pos_control)
        layout.addWidget(self.end_pos_control)
        self.setLayout(layout)

        self.setTitle("PlantAlong")
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        if parent:
            parent.addWidget(self)

    @property
    def step(self):
        return self.step_control.value

    @property
    def start_pos(self):
        return self.start_pos_control.value

    @property
    def end_pos(self):
        return self.end_pos_control.value


class Arrangement(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        arrangement_layout = QtWidgets.QHBoxLayout()
        self.setTitle("Arrangement")

        self._arrange_box = QtWidgets.QComboBox()
        self._arrange_box.insertItem(0, 'Sequence')
        self._arrange_box.insertItem(1, 'Random')
        self._arrange_label = QtWidgets.QLabel("Arrange")

        arrangement_layout.addWidget(self._arrange_label)
        arrangement_layout.addWidget(self._arrange_box)
        layout.addLayout(arrangement_layout)

        self.setLayout(layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

    @property
    def mode(self):
        return self._arrange_box.currentText()


class Path(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        path_layout = QtWidgets.QHBoxLayout()
        self.setTitle("Path")

        self._path_list = QtWidgets.QComboBox()
        self.__update_list()

        path_layout.addWidget(self._path_list)
        layout.addLayout(path_layout)

        self.setLayout(layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

    def refresh(self):
        self.__update_list()

    def __update_list(self):
        self._path_list.clear()
        objs = RLPy.RScene.FindObjects(RLPy.EObjectType_Path)
        for idx, obj in enumerate(objs):
            self._path_list.insertItem(idx, obj.GetName())

    @property
    def current_text(self):
        return self._path_list.currentText()