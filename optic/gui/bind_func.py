# 配置した後のwidgetに関数を紐づけ
# makeLayout <- -> bindFunc
from ..io.file_dialog import openFileDialogAndSetLineEdit
from ..io.data_io import saveROICheck, loadROICheck
from ..controls.table_controls import onTableSelectionChanged
from ..controls.view_controls import onBGImageTypeChanged
from ..utils import *

# -> io_layouts.makeLayoutLoadFileWidget
def bindFuncLoadFileWidget(q_widget, q_button, q_lineedit, filetype=None):
    q_button.clicked.connect(lambda: openFileDialogAndSetLineEdit(q_widget, filetype, q_lineedit))

# -> widget_manager.dict_button["exit"]
def bindFuncExit(q_window, q_button):
    q_button.clicked.connect(lambda: exitApp(q_window))

# -> io_layouts.makeLayoutROICheckIO
def bindFuncROICheckIO(q_window, q_lineedit, q_table, q_button_save, q_button_load, dict_tablecol, local_var=True):
    q_button_save.clicked.connect(lambda: saveROICheck(q_window, q_lineedit, q_table, dict_tablecol, local_var))
    q_button_load.clicked.connect(lambda: loadROICheck(q_window, q_table, dict_tablecol))

# -> slider_layouts.makeLayoutContrastSlider
def bindFuncContrastSlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))

# -> slider_layouts.makeLayoutOpacitySlider
def bindFuncOpacitySlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))

# -> table_layouts.makeLayoutTableROICountLabel
def bindFuncTableSelectionChanged(q_table, data_manager, view_controls, key):
    q_table.selectionModel().selectionChanged.connect(
        lambda selected, deselected: onTableSelectionChanged(data_manager, key, selected, deselected)
    )
    view_controls.updateView()

# -> view_layouts.makeLayoutBGImageTypeDisplay
def bindFuncRadiobuttonBGImageTypeChanged(q_buttongroup, data_manager, view_controls, key):
    def _onBGImageTypeChanged(button_id):
        bg_image_type = q_buttongroup.button(button_id).text()
        onBGImageTypeChanged(data_manager, key, bg_image_type)
        view_controls.updateView()
    q_buttongroup.buttonClicked[int].connect(_onBGImageTypeChanged)
    # 初期状態を設定し、即座に_onBGImageTypeChangedを呼び出す
    checked_button = q_buttongroup.checkedButton()
    _onBGImageTypeChanged(q_buttongroup.id(checked_button))
