import RLPy
import ui_components as UI
from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance
from plant_along_control import Position, ObjectsManageWidget, Arrangement, Path
import random

# Global value
ui = {}

# Callback
event_list = []
dialog_event_callback = None
event_callback = None


# ----------------- Event Call Back -----
class PlantAlongEventCallBack(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        global ui
        ui['object_container'].refresh()
        # ui['plant_along'].handle_selected_change_event()
        ui['path'].refresh()

    def OnObjectDataChanged(self):
        ui['object_container'].refresh()
        ui['path'].refresh()

    def OnAfterFileLoaded(self, nFileType):
        if nFileType == 0:
            ui['object_container'].clear()


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogHide(self):
        global event_list
        for event in event_list:
            RLPy.REventHandler.UnregisterCallback(event)
        event_list.clear()


def regist_event():
    global event_callback
    global event_list
    event_callback = PlantAlongEventCallBack()
    id = RLPy.REventHandler.RegisterCallback(event_callback)
    event_list.append(id)

    global ui
    global dialog_event_callback
    dialog_event_callback = DialogEventCallback()
    ui['dialog_window'].RegisterEventCallback(dialog_event_callback)


# ----- Set Plugin -------
def init_dialog():
    global ui
    global tab_widget
    ui['dialog_window'], ui['main_layout'] = set_dock("Prop Planter")

    try:
        ui["object_container"] = ObjectsManageWidget()
        ui['main_layout'].addWidget(ui['object_container'])

        ui["path"] = Path()
        ui['main_layout'].addWidget(ui['path'])

        ui['position'] = Position()
        ui['main_layout'].addWidget(ui['position'])

        ui['arrangement'] = Arrangement()
        ui['main_layout'].addWidget(ui['arrangement'])

        # apply button
        button = UI.Button("apply", parent=ui['main_layout'])
        button.clicked.connect(apply)
        ui['apply'] = button

    except Exception as e:
        print(e)


def set_dock(title="PlantAlong", width=300, height=400):
    dock = RLPy.RUi.CreateRDockWidget()
    dock.SetWindowTitle(title)

    qt_dock = wrapInstance(int(dock.GetWindow()), QtWidgets.QDockWidget)
    main_widget = QtWidgets.QWidget()
    qt_dock.setWidget(main_widget)
    qt_dock.setFixedWidth(width)
    # qt_dock.setMinimumHeight(height)

    main_layout = QtWidgets.QVBoxLayout()
    main_widget.setLayout(main_layout)

    return dock, main_layout


def show_dialog():
    global ui
    ui["dialog_window"].Show()
    regist_event()


def initialize_plugin():
    global event_list, event_callback

    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu(
            "Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName('pysample_menu')

    # dialog
    menu_action = plugin_menu.addAction("PlantAlong")
    init_dialog()
    menu_action.triggered.connect(show_dialog)


def run_script():
    try:
        initialize_plugin()
    except Exception as e:
        print(e)


def apply():
    global ui
    RLPy.RGlobal.BeginAction("PlantAlong")
    # for plant along
    start_pos = ui["position"].start_pos
    end_pos = ui["position"].end_pos

    # get the object list to plant
    items = ui['object_container'].items
    objs = [item['c_obj'] for item in items]

    # get arrrange method
    arrangement = ui['arrangement'].mode

    # get path
    path_name = ui["path"].current_text
    path = RLPy.RScene.FindObject(RLPy.EObjectType_Path, path_name)
    
    # check
    if not path:
        RLPy.RUi.ShowMessageBox("PlantAlong", "Can't find path object you selected", RLPy.EMsgButton_Ok)
        return
    if len(objs) == 0:
        RLPy.RUi.ShowMessageBox("PlantAlong", "Please add the object in list", RLPy.EMsgButton_Ok)
        return
    if start_pos > end_pos:
        RLPy.RUi.ShowMessageBox("PlantAlong", "Start Position can't greater than End Position", RLPy.EMsgButton_Ok)
        return

    try:
        idx = 0
        i = start_pos
        while i <= end_pos:
            single_step = ui["position"].step

            if arrangement == "Random":
                clone = objs[random.randint(0, len(objs)*2) % len(objs)].Clone()
            elif arrangement == "Sequence":
                clone = objs[idx % len(objs)].Clone()
            else:
                clone = objs[idx % len(objs)].Clone()

            current_time = RLPy.RGlobal.GetTime()
            clone.FollowPath(path, current_time)

            path_pos_control = clone.GetControl("PathPosition")
            current_time = RLPy.RGlobal.GetTime()
            path_pos_control.SetValue(current_time, i)

            # get clone
            i += single_step
            idx += 1

        RLPy.RGlobal.EndAction()
    except Exception as e:
        print(e)
