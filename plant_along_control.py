import RLPy
from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance
from PySide2 import QtCore
import ui_components as UI
import manipulation as mp


class ObjectsManageWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        contain_btn_layout = QtWidgets.QHBoxLayout()
        contain_list_layout = QtWidgets.QHBoxLayout()
        # self._contain_widget = QtWidgets.QTreeWidget()
        # self._tree_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        # self._tree_widget.setDragEnabled(True)
        # self._tree_widget.setDropIndicatorShown(True)

        self._contain_widget = QtWidgets.QListWidget()
        self._contain_widget.setAcceptDrops(True)
        self._contain_widget.setDragEnabled(True)
        self._contain_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self._add_btn = QtWidgets.QPushButton(text='add')
        # self._add_btn.setFixedHeight(15)
        self._add_btn.clicked.connect(self.__add_click)

        self._remove_btn = QtWidgets.QPushButton(text='remove')
        # self._remove_btn.setFixedHeight(15)
        self._remove_btn.clicked.connect(self.__remove_click)

        contain_btn_layout.addWidget(self._add_btn)
        contain_btn_layout.addWidget(self._remove_btn)
        contain_list_layout.addWidget(self._contain_widget, 1)

        layout.addLayout(contain_list_layout)
        layout.addLayout(contain_btn_layout)
        self.setLayout(layout)

        self.__items = []

    def __add_item(self, c_obj):

        # name = c_obj.GetName()
        # item = QtWidgets.QTreeWidgetItem()
        # item.setText(0, name)
        # item.setFlags(item.flags() | QtCore.Qt.NoItemFlags)
        # item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        # self._contain_widget.addTopLevelItem(item)

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
        for item_dict in self.__items:
            if item_dict[key] is value:
                self.__items.remove(item_dict)
                idx = self._contain_widget.row(item_dict['item'])
                self._contain_widget.takeItem(idx)
            else:
                print(item_dict[key], value)

    def __remove_click(self):
        selected_items = self._contain_widget.selectedItems()
        print("selected quantity: %d" % len(selected_items))
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
            if obj not in w_objs:
                self.__remove_item(obj, key='c_obj')


    @property
    def items(self):
        return self.__items


class Position(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.per_step = UI.PositionControl(label='Set Plant Step(%d)', value=0.1)
        self.start_pos = UI.PositionControl(label='Set Start Position(%d)')
        self.end_pos = UI.PositionControl(label='Set End Position(%d)', value=1)
        self.note_label = QtWidgets.QLabel(text="Step have to greater than %.2f" % 0.1)

        layout.addWidget(self.per_step)
        layout.addWidget(self.start_pos)
        layout.addWidget(self.end_pos)
        layout.addWidget(self.note_label)
        self.setLayout(layout)

        self.setTitle("PlantAlong")
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        self.__mini_step = 0.1

        if parent:
            parent.addWidget(self)

    def apply(self,):
        # for plant along
        single_step = self.per_step.value
        start_pos = self.start_pos.value
        end_pos = self.end_pos.value
        print("ui['plant_along'].value: %.2f" % single_step)
        
        # get the object list to plant
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

    # def handle_selected_change_event(self):
    #     objs = RLPy.RScene_GetSelectedObjects()
    #     if objs:
    #         bounding = mp.get_bounding_box(objs[0])
    #         self.__mini_step = bounding[1]
    #         self.note_label.setText("Step have to greater than %.2f" % self.__mini_step)
    #         # set control paras
    #         self.per_step.minimum = self.__mini_step
    #         self.per_step.value = self.__mini_step


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

        self._path_label = QtWidgets.QLabel("Path")

        path_layout.addWidget(self._path_label)
        path_layout.addWidget(self._path_list)
        layout.addLayout(path_layout)

        self.setLayout(layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

    def refresh(self):
        self.__update_list()

    def __update_list(self):
        self._path_list.clear()
        objs = RLPy.RScene.FindObjects(RLPy.EObjectType_Prop)
        for idx, obj in enumerate(objs):
            self._path_list.insertItem(idx, obj.GetName())