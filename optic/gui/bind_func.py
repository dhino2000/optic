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
def bindFuncROICheckIO(q_window, q_lineedit, q_table, q_button_save, q_button_load, table_columns, local_var=True):
    q_button_save.clicked.connect(lambda: saveROICheck(q_window, q_lineedit, q_table, table_columns, local_var))
    q_button_load.clicked.connect(lambda: loadROICheck(q_window, q_table, table_columns))

# -> table_layouts.makeLayoutTableROICountLabel
def bindFuncTableSelectionChanged(q_table, table_control, view_control):
    def _onSelectionChanged(selected, deselected):
        if selected.indexes():
            table_control.onSelectionChanged(selected, deselected)
            view_control.updateView()
    q_table.selectionModel().selectionChanged.connect(_onSelectionChanged)
def bindFuncRadiobuttonCelltypeChanged(table_control, view_control):
    def __onButtonClicked(row):
        def _onButtonClicked(button):
            table_control.updateSharedAttr_ROIDisplay_TableCelltypeChanged(row)
            view_control.updateView()
        return _onButtonClicked

    for row, button_group in table_control.groups_celltype.items():
        handler = __onButtonClicked(row)
        button_group.buttonClicked.connect(handler)

# -> table_layouts.makeLayoutAllROISetSameCelltype
def bindFuncButtonSetAllROISameCelltype(widget_manager, view_control, table_control):
    list_celltype = [key for key, value in table_control.table_columns.getColumns().items() if value['type'] == 'celltype']
    for celltype in list_celltype:
        widget_manager.dict_button[f"{table_control.key_app}_roi_set_{celltype}"].clicked.connect(
            lambda checked, ct=celltype: table_control.setAllROISameCelltype(ct)
        )
    view_control.updateView()

# -> table_layouts.makeLayoutAllROICheckboxToggle
def bindFuncButtonToggleAllROICheckbox(widget_manager, view_control, table_control):
    list_checkbox = [key for key, value in table_control.table_columns.getColumns().items() if value['type'] == 'checkbox']
    for checkbox in list_checkbox:
        for label, toggle in zip(["check", "uncheck"], [True, False]):
            widget_manager.dict_button[f"{table_control.key_app}_roi_{label}_{checkbox}"].clicked.connect(
                lambda checked, ck=checkbox, tg=toggle: table_control.toggleAllROICheckbox(ck, tg)
            )
    view_control.updateView()

# -> view_layouts.makeLayoutROIDisplayType
def bindFuncRadiobuttonROIDisplayTypeChanged(q_buttongroup, view_control, table_control):
    def _onROIDisplayTypeChanged(button_id):
        roi_display_type = q_buttongroup.button(button_id).text()
        table_control.updateSharedAttr_ROIDisplay_TypeChanged(roi_display_type)
        view_control.updateView()
    q_buttongroup.buttonClicked[int].connect(_onROIDisplayTypeChanged)
    checked_button = q_buttongroup.checkedButton()
    _onROIDisplayTypeChanged(q_buttongroup.id(checked_button))

# -> view_layouts.makeLayoutBGImageTypeDisplay
def bindFuncRadiobuttonBGImageTypeChanged(q_buttongroup, view_control):
    def _onBGImageTypeChanged(button_id):
        bg_image_type = q_buttongroup.button(button_id).text()
        view_control.setBackgroundImageType(bg_image_type)
        view_control.updateView()
    q_buttongroup.buttonClicked[int].connect(_onBGImageTypeChanged)
    checked_button = q_buttongroup.checkedButton()
    _onBGImageTypeChanged(q_buttongroup.id(checked_button))

# -> slider_layouts.makeLayoutOpacitySlider
def bindFuncOpacitySlider(q_slider, view_control):
    def onOpacityChanged(value):
        view_control.setROIOpacity(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

def bindFuncHighlightOpacitySlider(q_slider, view_control):
    def onOpacityChanged(value):
        view_control.setHighlightOpacity(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

# -> slider_layouts.makeLayoutContrastSlider
def bindFuncBackgroundContrastSlider(q_slider_min, q_slider_max, view_control, channel):
    def onContrastMinChanged(value):
        current_max = q_slider_max.value()
        if value > current_max:
            q_slider_max.setValue(value)
        view_control.setBackgroundContrastValue(channel, 'min', value)
        view_control.setBackgroundContrastValue(channel, 'max', max(value, current_max))
        view_control.updateView()
    def onContrastMaxChanged(value):
        current_min = q_slider_min.value()
        if value < current_min:
            q_slider_min.setValue(value)
        view_control.setBackgroundContrastValue(channel, 'max', value)
        view_control.setBackgroundContrastValue(channel, 'min', min(value, current_min))
        view_control.updateView()
    q_slider_min.valueChanged.connect(onContrastMinChanged)
    q_slider_max.valueChanged.connect(onContrastMaxChanged)

def bindFuncBackgroundVisibilityCheckbox(q_checkbox, view_control, channel):
    def onVisibilityChanged(state):
        is_visible = (state == Qt.Checked)
        view_control.setBackgroundVisibility(channel, is_visible)
        view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)
    