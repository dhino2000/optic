# 配置した後のwidgetに関数を紐づけ
# makeLayout <- -> bindFunc
from ..io.file_dialog import openFileDialogAndSetLineEdit
from ..io.data_io import saveROICheck, loadROICheck
from ..utils import *
from PyQt5.QtCore import Qt

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

# -> table_layouts.makeLayoutTableROICountLabel
def bindFuncTableSelectionChanged(q_table, table_controls, view_controls):
    q_table.selectionModel().selectionChanged.connect(table_controls.onSelectionChanged)
    view_controls.updateView()
    
# -> view_layouts.makeLayoutBGImageTypeDisplay
def bindFuncRadiobuttonBGImageTypeChanged(q_buttongroup, view_controls):
    def _onBGImageTypeChanged(button_id):
        bg_image_type = q_buttongroup.button(button_id).text()
        view_controls.setBackgroundImageType(bg_image_type)
        view_controls.updateView()
    q_buttongroup.buttonClicked[int].connect(_onBGImageTypeChanged)
    checked_button = q_buttongroup.checkedButton()
    _onBGImageTypeChanged(q_buttongroup.id(checked_button))

# -> slider_layouts.makeLayoutOpacitySlider
def bindFuncOpacitySlider(q_slider, view_controls):
    def onOpacityChanged(value):
        view_controls.setROIOpacity(value)
        view_controls.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

def bindFuncHighlightOpacitySlider(q_slider, view_controls):
    def onOpacityChanged(value):
        view_controls.setHighlightOpacity(value)
        view_controls.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

# -> slider_layouts.makeLayoutContrastSlider
def bindFuncBackgroundContrastSlider(q_slider_min, q_slider_max, view_controls, channel):
    def onContrastMinChanged(value):
        current_max = q_slider_max.value()
        if value > current_max:
            q_slider_max.setValue(value)
        view_controls.setBackgroundContrastValue(channel, 'min', value)
        view_controls.setBackgroundContrastValue(channel, 'max', max(value, current_max))
        view_controls.updateView()
    def onContrastMaxChanged(value):
        current_min = q_slider_min.value()
        if value < current_min:
            q_slider_min.setValue(value)
        view_controls.setBackgroundContrastValue(channel, 'max', value)
        view_controls.setBackgroundContrastValue(channel, 'min', min(value, current_min))
        view_controls.updateView()
    q_slider_min.valueChanged.connect(onContrastMinChanged)
    q_slider_max.valueChanged.connect(onContrastMaxChanged)

def bindFuncBackgroundVisibilityCheckbox(q_checkbox, view_controls, channel):
    def onVisibilityChanged(state):
        is_visible = (state == Qt.Checked)
        view_controls.setBackgroundVisibility(channel, is_visible)
        view_controls.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)
    