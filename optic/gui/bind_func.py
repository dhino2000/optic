from __future__ import annotations
from ..type_definitions import *
from ..io.file_dialog import openFileDialogAndSetLineEdit
from ..io.data_io import saveROICheck, loadROICheck, loadEventFileNPY
from ..utils import *
from PyQt5.QtCore import Qt
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit, QTableWidget, QButtonGroup, QCheckBox, QGraphicsView, QSlider
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

"""
This module uses the following type annotations:

- q_button, q_button_save, q_button_load: QPushButton
- q_widget, q_window: QWidget, QMainWindow
- q_lineedit: QLineEdit
- q_table: QTableWidget
- q_buttongroup: QButtonGroup
- q_checkbox: QCheckBox
- q_view: QGraphicsView
- q_canvas: FigureCanvasQTAgg
- view_control: ViewControl
- table_control: TableControl
- canvas_control: CanvasControl
- data_manager: DataManager
- control_manager: ControlManager
- widget_manager: WidgetManager
"""

"""
others
"""
# -> widget_manager.dict_button["exit"]
def bindFuncExit(
    q_button: 'QPushButton', 
    q_window: 'QWidget'
) -> None:
    q_button.clicked.connect(lambda: exitApp(q_window))

# -> makeWidgetView, mousePressEvent
def bindFuncViewMouseEvent(
    q_view: 'QGraphicsView', 
    view_control: 'ViewControl', 
    table_control: 'TableControl'
) -> None:
    def onViewClicked(event) -> None:
        view_pos = event.pos()
        scene_pos = q_view.mapToScene(view_pos)
        view_control.mousePressEvent(int(scene_pos.x()), int(scene_pos.y()))
        table_control.updateSelectedROI(
            view_control.control_manager.getSharedAttr(view_control.key_app, 'roi_selected_id')
        )
    
    q_view.mousePressEvent = onViewClicked

"""
canvas_layouts
"""
# -> canvas_layouts.makeLayoutCanvasTracePlot, mouseEvent
def bindFuncCanvasMouseEvent(
    q_canvas: 'FigureCanvasQTAgg',
    canvas_control: 'CanvasControl',
    ax: Axes,
    list_event: List[str],
    list_func: List[Callable[[Event, Axes], Any]]
) -> None:
    if len(list_event) != len(list_func):
        raise ValueError("The number of events and functions must match.")

    for event, func in zip(list_event, list_func):
        q_canvas.mpl_connect(event, lambda event, func=func, ax=ax: func(event, ax))

# -> canvas_layouts.makeLayoutEventFilePlot
def bindFuncButtonEventfileIO(
    q_button_load: 'QPushButton', 
    q_button_clear: 'QPushButton', 
    q_window: 'QWidget', 
    data_manager: 'DataManager', 
    control_manager: 'ControlManager', 
    canvas_control: 'CanvasControl', 
    key_app: str
) -> None:
    def _loadEventFileNPY() -> None:
        loadEventFileNPY(q_window, data_manager, control_manager, key_app)
        canvas_control.updatePlotWithROISelect()
    q_button_load.clicked.connect(_loadEventFileNPY)
    q_button_clear.clicked.connect(lambda: data_manager.clearEventfile(key_app))

"""
io_layouts
"""
# -> io_layouts.makeLayoutLoadFileWidget
def bindFuncLoadFileWidget(
    q_button: 'QPushButton', 
    q_widget: 'QWidget', 
    q_lineedit: 'QLineEdit', 
    filetype: str = None
) -> None:
    q_button.clicked.connect(lambda: openFileDialogAndSetLineEdit(q_widget, filetype, q_lineedit))


# -> io_layouts.makeLayoutROICheckIO
def bindFuncROICheckIO(
    q_button_save: 'QPushButton', 
    q_button_load: 'QPushButton', 
    q_window: 'QWidget', 
    q_lineedit: 'QLineEdit', 
    q_table: 'QTableWidget', 
    table_columns: List[str], 
    table_control: 'TableControl',
    local_var: bool = True
) -> None:
    q_button_save.clicked.connect(lambda: saveROICheck(q_window, q_lineedit, q_table, table_columns, local_var))
    q_button_load.clicked.connect(lambda: loadROICheck(q_window, q_table, table_columns, table_control))

"""
slider_layouts
"""
# -> slider_layouts.makeLayoutOpacitySlider
def bindFuncOpacitySlider(
    q_slider: 'QSlider', 
    view_control: 'ViewControl'
) -> None:
    def onOpacityChanged(value: int) -> None:
        view_control.setROIOpacity(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

def bindFuncHighlightOpacitySlider(
    q_slider: 'QSlider', 
    view_control: 'ViewControl'
) -> None:
    def onOpacityChanged(value: int) -> None:
        view_control.setHighlightOpacity(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

# -> slider_layouts.makeLayoutContrastSlider
def bindFuncBackgroundContrastSlider(
    q_slider_min: 'QSlider', 
    q_slider_max: 'QSlider', 
    view_control: 'ViewControl', 
    channel: str
) -> None:
    def onContrastMinChanged(value: int) -> None:
        current_max = q_slider_max.value()
        if value > current_max:
            q_slider_max.setValue(value)
        view_control.setBackgroundContrastValue(channel, 'min', value)
        view_control.setBackgroundContrastValue(channel, 'max', max(value, current_max))
        view_control.updateView()
    def onContrastMaxChanged(value: int) -> None:
        current_min = q_slider_min.value()
        if value < current_min:
            q_slider_min.setValue(value)
        view_control.setBackgroundContrastValue(channel, 'max', value)
        view_control.setBackgroundContrastValue(channel, 'min', min(value, current_min))
        view_control.updateView()
    q_slider_min.valueChanged.connect(onContrastMinChanged)
    q_slider_max.valueChanged.connect(onContrastMaxChanged)

# -> view_layouts.makeLayoutViewWithZTSlider
def bindFuncPlaneZSlider(
    q_slider: 'QSlider',
    view_control: 'ViewControl'
) -> None:
    def onZChanged(value: int) -> None:
        view_control.setPlaneZ(value)
        
        view_control.updateView()
    q_slider.valueChanged.connect(onZChanged)
def bindFuncPlaneTSlider(
    q_slider: 'QSlider',
    view_control: 'ViewControl'
) -> None:
    def onTChanged(value: int) -> None:
        view_control.setPlaneT(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onTChanged)

# -> slider_layouts.makeLayoutContrastSlider
def bindFuncBackgroundVisibilityCheckbox(
    q_checkbox: 'QCheckBox', 
    view_control: 'ViewControl', 
    channel: str
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        view_control.setBackgroundVisibility(channel, is_visible)
        view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

"""
table_layouts
"""
# -> table_layouts.makeLayoutTableROICountLabel
def bindFuncTableSelectionChanged(
    q_table: 'QTableWidget', 
    table_control: 'TableControl', 
    view_control: 'ViewControl', 
    canvas_control: 'CanvasControl'
) -> None:
    def _onSelectionChanged(selected, deselected) -> None:
        if selected.indexes():
            table_control.onSelectionChanged(selected, deselected)
            view_control.updateView()
            canvas_control.updatePlotWithROISelect()
    q_table.selectionModel().selectionChanged.connect(_onSelectionChanged)

# -> table_layouts.makeLayoutTableROICountLabel
def bindFuncRadiobuttonOfTableChanged(
    table_control: 'TableControl', 
    view_control: 'ViewControl'
) -> None:
    def __onButtonClicked(row: int) -> Callable[[QPushButton], None]:
        def _onButtonClicked(button: 'QPushButton') -> None:
            table_control.changeRadiobuttonOfTable(row)
            view_control.updateView()
        return _onButtonClicked

    for row, button_group in table_control.groups_celltype.items():
        handler = __onButtonClicked(row)
        button_group.buttonClicked.connect(handler)

# -> table_layouts.makeLayoutAllROISetSameCelltype
def bindFuncButtonSetAllROISameCelltype(
    widget_manager: 'WidgetManager', 
    view_control: 'ViewControl', 
    table_control: 'TableControl'
) -> None:
    list_celltype = [key for key, value in table_control.table_columns.getColumns().items() if value['type'] == 'celltype']
    for celltype in list_celltype:
        widget_manager.dict_button[f"{table_control.key_app}_roi_set_{celltype}"].clicked.connect(
            lambda checked, ct=celltype: table_control.setAllROISameCelltype(ct)
        )
    view_control.updateView()

# -> table_layouts.makeLayoutAllROICheckboxToggle
def bindFuncCheckboxToggleAllROI(
    widget_manager: 'WidgetManager', 
    view_control: 'ViewControl', 
    table_control: 'TableControl'
) -> None:
    list_checkbox = [key for key, value in table_control.table_columns.getColumns().items() if value['type'] == 'checkbox']
    for checkbox in list_checkbox:
        for label, toggle in zip(["check", "uncheck"], [True, False]):
            widget_manager.dict_button[f"{table_control.key_app}_roi_{label}_{checkbox}"].clicked.connect(
                lambda checked, ck=checkbox, tg=toggle: table_control.toggleAllROICheckbox(ck, tg)
            )
    view_control.updateView()

# -> table_layouts.makeLayoutROIFilterButton
def bindFuncButtonFilterROI(
    q_button: 'QPushButton',
    table_control: 'TableControl', 
    view_control: 'ViewControl'
) -> None:
    thresholds = table_control.getThresholdsOfROIFilter()
    q_button.clicked.connect(
        lambda: table_control.filterROI(thresholds)
    )
    view_control.updateView()

"""
view_layouts
"""
# -> view_layouts.makeLayoutDislplayCelltype, All ROI, None, Neuron ,Not Cell, ...
def bindFuncRadiobuttonDisplayCelltypeChanged(
    q_buttongroup: 'QButtonGroup', 
    view_control: 'ViewControl', 
    table_control: 'TableControl'
) -> None:
    def _onROIDisplayTypeChanged(button_id: int) -> None:
        roi_display_type = q_buttongroup.button(button_id).text()
        table_control.updateROIDisplayWithCelltype(roi_display_type)
        view_control.updateView()
    q_buttongroup.buttonClicked[int].connect(_onROIDisplayTypeChanged)
    checked_button = q_buttongroup.checkedButton()
    _onROIDisplayTypeChanged(q_buttongroup.id(checked_button))

# -> view_layouts.makeLayoutBGImageTypeDisplay, meanImg, meanImgE, ... 
def bindFuncRadiobuttonBGImageTypeChanged(
    q_buttongroup: 'QButtonGroup', 
    view_control: 'ViewControl'
) -> None:
    def _onBGImageTypeChanged(button_id: int) -> None:
        bg_image_type = q_buttongroup.button(button_id).text()
        view_control.setBackgroundImageType(bg_image_type)
        view_control.updateView()
    q_buttongroup.buttonClicked[int].connect(_onBGImageTypeChanged)
    checked_button = q_buttongroup.checkedButton()
    _onBGImageTypeChanged(q_buttongroup.id(checked_button))




