from __future__ import annotations
from ..type_definitions import *
from ..io.file_dialog import openFileDialogAndSetLineEdit, saveFileDialog
from ..io.data_io import saveROICheck, loadROICheck, loadEventFileNPY, generateSavePath, saveTiffStack
from ..visualization.view_visual_rectangle import clipRectangleRange
from ..processing import *
from ..utils import *
from PyQt5.QtCore import Qt
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit, QTableWidget, QButtonGroup, QCheckBox, QGraphicsView, QSlider, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

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
    def onViewPressed(event) -> None:
        view_control.mousePressEvent(event)
        roi_selected_id = view_control.control_manager.getSharedAttr(view_control.app_key, 'roi_selected_id')
        table_control.updateSelectedROI(roi_selected_id)
        table_control.q_table.setFocus()
    
    q_view.mousePressEvent = onViewPressed

# -> makeWidgetView, mousePressEvent
def bindFuncViewMouseEventWithTracking(
    q_view: 'QGraphicsView', 
    view_control: 'ViewControl', 
    table_control: 'TableControl',
    app_key: AppKeys,
    app_key_sec: AppKeys,
) -> None:
    def onViewPressed(event) -> None:
        view_control.mousePressEvent(event)
        roi_selected_id = view_control.control_manager.getSharedAttr(view_control.app_key, 'roi_selected_id')
        table_control.updateSelectedROI(roi_selected_id)
        table_control.q_table.setFocus()
    
    q_view.mousePressEvent = onViewPressed

# -> makeWidgetView, mouseMoveEvent
def bindFuncViewMouseEventForTIFF(
    q_view: 'QGraphicsView',
    q_lineedit: 'QLineEdit',
    view_control: 'ViewControl',
    table_control: 'TableControl'
) -> None:
    def onViewPressed(event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if view_control.dict_key_pushed[Qt.Key_Control]:
                view_control.startDraggingWithCtrlKey(event)
            elif table_control:
                scene_pos = q_view.mapToScene(event.pos())
                view_control.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()))
                roi_selected_id = view_control.control_manager.getSharedAttr(view_control.app_key, 'roi_selected_id')
                table_control.updateSelectedROI(roi_selected_id)

    def onViewMoved(event: QMouseEvent) -> None:
        if view_control.is_dragging and view_control.dict_key_pushed[Qt.Key_Control]:
            view_control.updateDraggingWithCtrlKey(event)

    def onViewReleased(event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and view_control.is_dragging:
            if view_control.dict_key_pushed[Qt.Key_Control]:
                view_control.finishDraggingWithCtrlKey(event)
                rect = view_control.rect.rect()
                rect_range = view_control.getRectRangeFromQRectF(rect)
                q_lineedit.setText(','.join(map(str, rect_range)))
            else:
                view_control.cancelDraggingWithCtrlKey()

    q_view.mousePressEvent = onViewPressed
    q_view.mouseMoveEvent = onViewMoved
    q_view.mouseReleaseEvent = onViewReleased

    def onKeyPressed(event: QKeyEvent) -> None:
        view_control.keyPressEvent(event)

    def onKeyReleased(event: QKeyEvent) -> None:
        view_control.keyReleaseEvent(event)

    q_view.keyPressEvent = onKeyPressed
    q_view.keyReleaseEvent = onKeyReleased

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
    app_key: str
) -> None:
    def _loadEventFileNPY() -> None:
        loadEventFileNPY(q_window, data_manager, control_manager, app_key)
        canvas_control.updatePlotWithROISelect()
    q_button_load.clicked.connect(_loadEventFileNPY)
    q_button_clear.clicked.connect(lambda: data_manager.clearEventfile(app_key))

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
    gui_defaults: GuiDefaults,
    table_columns: List[str], 
    json_config: JsonConfig,
    table_control: 'TableControl',
    local_var: bool = True
) -> None:
    q_button_save.clicked.connect(lambda: saveROICheck(q_window, q_lineedit, q_table, gui_defaults, table_columns, json_config, local_var))
    q_button_load.clicked.connect(lambda: loadROICheck(q_window, q_table, gui_defaults, table_columns, table_control))

"""
processing_image_layouts
"""
# -> processing_image_layouts.makeLayoutStackNormalization
def bindFuncButtonSetRectangeRange(
    q_widget: 'QWidget',
    q_button: 'QPushButton', 
    q_lineedit: 'QLineEdit',
    view_control: 'ViewControl'
) -> None:
    def onButtonClicked() -> None:
        try:
            rect_range = [int(x) for x in q_lineedit.text().replace(" ", "").split(",")]
            # if values are out of range
            rect_range = clipRectangleRange(view_control.tiff_shape, rect_range)
            q_lineedit.setText(','.join(map(str, rect_range)))
            if len(rect_range) != 8:
                raise ValueError("Expected 8 values")
            view_control.setRectRange(rect_range)
            view_control.updateView()
        except ValueError:
            QMessageBox.warning(q_widget, "Invalid Input", "Please enter 8 integer values separated by commas.\nEx) 100, 200, 100, 200, 1, 2, 0, 0")
    q_button.clicked.connect(onButtonClicked)

# -> processing_image_layouts.makeLayoutStackNormalization
def bindFuncButtonManageRectangleRangeForListWidget(
    q_widget: 'QWidget',
    q_button_add: 'QPushButton', 
    q_button_remove: 'QPushButton', 
    q_button_clear: 'QPushButton', 
    q_listwidget: 'QListWidget', 
    q_lineedit: 'QLineEdit',
    view_control: 'ViewControl'
) -> None:
    def _addItemToListWidgetFromLineEdit(q_listwidget, q_lineedit) -> None:
        try:
            q_lineedit.setText(q_lineedit.text().replace(" ", ""))
            rect_range = [int(x) for x in q_lineedit.text().split(",")]
            if len(rect_range) != 8:
                raise ValueError("Expected 8 values")
            addItemToListWidgetFromLineEdit(q_listwidget, q_lineedit)
        except ValueError:
            QMessageBox.warning(q_widget, "Invalid Input", "Please enter 8 integer values separated by commas.\nEx) 100, 200, 100, 200, 1, 2, 0, 0")
    def _removeSelectedItemsFromListWidget(q_listwidget, view_control) -> None:
        view_control.setRectHighlightRange(None)
        removeSelectedItemsFromListWidget(q_listwidget)
    def _clearListWidget(q_listwidget, view_control) -> None:
        view_control.setRectHighlightRange(None)
        clearListWidget(q_listwidget)
    q_button_add.clicked.connect(lambda: _addItemToListWidgetFromLineEdit(q_listwidget, q_lineedit))
    q_button_remove.clicked.connect(lambda: _removeSelectedItemsFromListWidget(q_listwidget, view_control))
    q_button_clear.clicked.connect(lambda: _clearListWidget(q_listwidget, view_control))

def bindFuncListWidgetSelectionChanged(
    q_listwidget: 'QListWidget', 
    view_control: 'ViewControl'
) -> None:
    def onSelectionChanged() -> None:
        item = q_listwidget.currentItem()
        if item:
            rect_range = [int(x) for x in item.text().replace(" ", "").split(",")]
            view_control.setRectHighlightRange(rect_range)
            view_control.updateView()
    q_listwidget.itemSelectionChanged.connect(onSelectionChanged)

def bindFuncButtonRunImageNormalization(
    q_widget: 'QWidget',
    q_button: 'QPushButton',
    q_lineedit: 'QLineEdit',
    q_listwidget: 'QListWidget',
    tiff_stack: np.ndarray[Tuple[int, int, int, int, int]],
    metadata: Dict[str, Any],
):
    def _bindFuncButtonRunImageNormalization():
        try:
            list_reference_areas = [tuple(int(x.strip()) for x in q_listwidget.item(i).text().split(",")) for i in range(q_listwidget.count())]
            print(list_reference_areas)
            if len(list_reference_areas) == 0:
                raise ValueError("Add reference areas to the list !")

            # progress dialog
            progress_dialog = showProgressDialog(q_widget, "Normalizing image stack...")
            try:
                path_tif_src = q_lineedit.text()
                path_tif_dst = generateSavePath(path_tif_src, suffix="_normalized", new_extension=".tif")
                tiff_stack_norm = normalizeImageStackWithReferenceAreas(tiff_stack, list_reference_areas)
                saveTiffStack(q_widget, path_tif_dst, tiff_stack_norm, imagej=True, metadata=metadata)
            finally:
                progress_dialog.close()

        except ValueError as e:
            QMessageBox.warning(q_widget, "Invalid Input", str(e))
        except Exception as e:
            QMessageBox.warning(q_widget, "Error", f"An error occurred: {str(e)}")

    q_button.clicked.connect(_bindFuncButtonRunImageNormalization)

# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncCheckboxShowMatchedROI(
    q_checkbox: 'QCheckBox',
    view_controls: Dict[AppKeys, ViewControl]
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        for view_control in view_controls.values():
            view_control.setShowROIMatch(is_visible)
            view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncCheckboxShowRegisteredBGImage(
    q_checkbox: 'QCheckBox',
    view_controls: Dict[AppKeys, ViewControl]
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        for view_control in view_controls.values():
            view_control.setShowRegImBG(is_visible)
            view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncCheckboxShowRegisteredROIImage(
    q_checkbox: 'QCheckBox',
    view_controls: Dict[AppKeys, ViewControl]
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        for view_control in view_controls.values():
            view_control.setShowRegImROI(is_visible)
            view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

# -> processing_image_layouts.makeLayoutStackRegistration
def bindFuncCheckboxShowRegisteredStack(
    q_checkbox: 'QCheckBox',
    view_control: 'ViewControl'
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        view_control.setShowRegStack(is_visible)
        view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncButtonRunElastixForFall(
        q_button: 'QPushButton',
        data_manager: 'DataManager',
        config_manager: 'ConfigManager',
        control_manager: 'ControlManager',
        app_key: str,
        app_key_sec: str,
        combobox_elastix_method: QComboBox,
) -> None:
    def _runElastix():
        elastix_method = combobox_elastix_method.currentText()
        print(f"{elastix_method} transform")
        dict_params = config_manager.json_config.get("elastix_params")[elastix_method]
        print("Elastix Parameters", dict_params)

        # get fixed image and moving image, (meanImg, meanImgE, max_proj, Vcorr)
        img_type_pri = control_manager.view_controls[app_key].getBackgroundImageType()
        img_fix= data_manager.getDictBackgroundImage(app_key).get(img_type_pri)
        img_type_sec = control_manager.view_controls[app_key_sec].getBackgroundImageType()
        img_mov = data_manager.getDictBackgroundImage(app_key_sec).get(img_type_sec)
        # run elastix
        transform_parameters = calculateSingleTransform(img_fix, img_mov, dict_params)
        data_manager.dict_transform_parameters[app_key] = transform_parameters
        # apply transform parameters to image
        # background image
        dict_im_bg_reg_mov = {}
        for key_im in data_manager.getDictBackgroundImage(app_key_sec).keys():
            dict_im_bg_reg_mov[key_im] = applySingleTransform(data_manager.getDictBackgroundImage(app_key_sec).get(key_im), transform_parameters)
        data_manager.dict_im_bg_reg[app_key_sec] = dict_im_bg_reg_mov
        # ROI image
        img_roi_mov = data_manager.getDictROIImage(app_key_sec).get("raw").copy()
        img_roi_mov_reg = applySingleTransform(img_roi_mov, transform_parameters)
        data_manager.dict_im_roi[app_key_sec]["reg"] = img_roi_mov_reg
        # ROI coordinates
        dict_roi_coords = data_manager.getDictROICoords(app_key_sec)
        dict_roi_coords_reg = applyDictROICoordsTransform(img_mov, transform_parameters, dict_roi_coords)
        data_manager.dict_roi_coords_reg[app_key_sec] = dict_roi_coords_reg

        control_manager.view_controls[app_key].updateView()
        control_manager.view_controls[app_key_sec].updateView()

        print("Registration Finished !")

    q_button.clicked.connect(lambda: _runElastix())

# -> processing_image_layouts.makeLayoutStackRegistration
def bindFuncButtonRunElastixForSingleStack(
        q_button: 'QPushButton',
        data_manager: 'DataManager',
        config_manager: 'ConfigManager',
        app_key: str,
        combobox_elastix_method: QComboBox,
        combobox_channel_ref: QComboBox,
        combobox_idx_ref: QComboBox,
        axis: Literal["t", "z"],
) -> None:
    def _runElastix():
        elastix_method = combobox_elastix_method.currentText()
        channel_ref = int(combobox_channel_ref.currentText())
        idx_ref = int(combobox_idx_ref.currentText())
        print(f"{elastix_method} transform")
        print("Reference channel:", channel_ref)
        print(f"Reference {axis} plane:", idx_ref)
        img_stack = data_manager.getTiffStack(app_key)
        dict_params = config_manager.json_config.get("elastix_params")[elastix_method]
        print("Elastix Parameters", dict_params)
        img_stack_reg = runStackRegistration(img_stack, dict_params, channel_ref, idx_ref, axis, display_iters=10)
        data_manager.dict_tiff_reg[app_key] = img_stack_reg
        print("Registration Fnisihed !")
    q_button.clicked.connect(lambda: _runElastix())

# -> processing_image_layouts.makeLayoutStackRegistration
def bindFuncButtonSaveRegisterdImage(
    q_widget: 'QWidget',
    q_button: 'QPushButton',
    data_manager: 'DataManager',
    app_key: str,
    path_tif_src: str
) -> None:
    def _saveRegisteredImage():
        path_tif_dst = generateSavePath(path_tif_src, suffix="_reg", new_extension=".tif")
        metadata = data_manager.getTiffMetadata(app_key)
        saveTiffStack(q_widget, path_tif_dst, data_manager.getTiffStackRegistered(app_key), imagej=True, metadata=metadata)
    q_button.clicked.connect(_saveRegisteredImage)

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
            if canvas_control: # for canvas_control
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
        widget_manager.dict_button[f"{table_control.app_key}_roi_set_{celltype}"].clicked.connect(
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
            widget_manager.dict_button[f"{table_control.app_key}_roi_{label}_{checkbox}"].clicked.connect(
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


