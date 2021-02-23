import RLPy
import ui_components as UI
from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance
from random import randrange
from path_mirror_control import PathMirrorTabWidget, MirrorAxis, PlantAlong
from manipulation import local_move
# Global value
ui = {}

# Callback
event_list = []
dialog_event_callback = None
event_callback = None


# ----------------- Event Call Back -----
class PropPlanterEventCallBack(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        print('selected change')
        global ui
        ui['tab_widget'].handle_selected_change_event()


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
    event_callback = PropPlanterEventCallBack()
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
        # tab ui
        ui['tab_widget'] = PathMirrorTabWidget()
        ui['main_layout'].addWidget(ui['tab_widget'])

        ui['mirror_axis'] = MirrorAxis()
        ui['main_layout'].addWidget(ui['mirror_axis'])

        ui['plant_along'] = PlantAlong()
        ui['main_layout'].addWidget(ui['plant_along'])

        # apply button
        button = UI.Button("apply", parent=ui['main_layout'])
        button.clicked.connect(apply)
        ui['apply'] = button

    except Exception as e:
        print(e)


def set_dock(title="Path Mirror", width=300, height=400):
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
    menu_action = plugin_menu.addAction("PathMirror")
    init_dialog()
    menu_action.triggered.connect(show_dialog)


def run_script():
    try:
        initialize_plugin()
    except Exception as e:
        print(e)


def apply():
    global ui
    # objs = RLPy.RScene.GetSelectedObjects()
    #
    # for idx, obj in enumerate(objs):
    #     print("obj: %s" % obj.GetName())

    objs = RLPy.RScene.GetSelectedObjects()
    obj = objs[0]
    path_pos_control = obj.GetControl("PathPosition")
    path_pos_control.SetValue(RLPy.RTime(50), 0.25)
    path_pos_control.SetValue(RLPy.RTime(100), 0.5)
    path_pos_control.SetValue(RLPy.RTime(150), 0.75)
    path_pos_control.SetValue(RLPy.RTime(200), 1)
    obj.Update()

    #
    # # for plant along
    # objs = RLPy.RScene.GetSelectedObjects()
    # single_step = ui['plant_along'].value
    # print("ui['plant_along'].value: %.2f" % single_step)
    #
    # objs = RLPy.RScene.GetSelectedObjects()
    # try:
    #     obj = objs[0]
    #     path_pos_control = obj.GetControl("PathPosition")
    #     current_time = RLPy.RGlobal.GetTime()
    #
    #     # get transform control and origin transform
    #     transform_control = obj.GetControl("Transform")
    #     transform_key = RLPy.RTransformKey()
    #     transform_control.GetTransformKey(current_time, transform_key)
    #     origin_transform = transform_key.GetTransform()
    #
    #     i = 0
    #     while i <= 1:
    #         print("i: %.2f" % i)
    #         # set path position key
    #         path_pos_control.SetValue(current_time, i)
    #         obj.Update()
    #
    #         # get x, y, z
    #         transform = transform_key.GetTransform()
    #
    #         # let clone transform equal to origin
    #         clone = obj.Clone()
    #         clone_transform_control = clone.GetControl("Transform")
    #         clone_transform_key = RLPy.RTransformKey()
    #         clone_transform_control.GetTransformKey(current_time, clone_transform_key)
    #         clone_transform_key.SetTransform(transform)
    #
    #         i += single_step
    #
    #     print("Finish path control value apply")
    #     # clean origin obj path position key
    #     transform_key.SetTransform(origin_transform)
    # except Exception as e:
    #     print(e)
