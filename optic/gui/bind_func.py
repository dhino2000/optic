from __future__ import annotations
from ..type_definitions import *
from ..io.file_dialog import openFileDialogAndSetLineEdit, saveFileDialog
from ..io.data_io import saveROICheck, loadROICheck, loadEventFilesNPY, generateSavePath, saveTiffStack, saveROITracking, loadROITracking, loadCellposeMaskNPY, saveMicrogliaTracking, loadMicrogliaTracking
from ..visualization.info_visual import updateROICountDisplay
from ..processing import *
from ..preprocessing import *
from ..utils import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit, QTableWidget, QButtonGroup, QCheckBox, QGraphicsView, QSlider, QMessageBox, QComboBox, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from copy import deepcopy
from itk.elxParameterObjectPython import elastixParameterObject
import numpy as np
import os
import shutil

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

# -> widget_manager.dict_button["help"]
def bindFuncHelp(
    q_button: 'QPushButton',
    url: str,
) -> None:
    q_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))


"""
View Functions -> ViewHandler
"""
def bindFuncViewEvents(q_view: QGraphicsView, view_control: ViewControl):
    def onKeyPress(event: QKeyEvent):
        view_control.view_handler.handleKeyPress(event)

    def onKeyRelease(event: QKeyEvent):
        view_control.view_handler.handleKeyRelease(event)

    def onMousePress(event: QMouseEvent):
        view_control.view_handler.handleMousePress(event)

    def onMouseMove(event: QMouseEvent):
        view_control.view_handler.handleMouseMove(event)

    def onMouseRelease(event: QMouseEvent):
        view_control.view_handler.handleMouseRelease(event)

    def onWheelEvent(event: QWheelEvent):
        view_control.view_handler.handleWheelEvent(event)

    q_view.keyPressEvent = onKeyPress
    q_view.keyReleaseEvent = onKeyRelease
    q_view.mousePressEvent = onMousePress
    q_view.mouseMoveEvent = onMouseMove
    q_view.mouseReleaseEvent = onMouseRelease
    q_view.wheelEvent = onWheelEvent

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
    q_combobox_eventfile: 'QComboBox',
    data_manager: 'DataManager', 
    control_manager: 'ControlManager', 
    canvas_control: 'CanvasControl', 
    app_key: str
) -> None:
    def _loadEventFilesNPY() -> None:
        success = loadEventFilesNPY(q_window, data_manager, app_key)
        # update combobox
        if success:
            q_combobox_eventfile.clear()
            q_combobox_eventfile.addItems(data_manager.getDictEventfile(app_key).keys())
    def _clearDictEventfile() -> None:
        data_manager.clearDictEventfile(app_key)
        q_combobox_eventfile.clear()
    def _updateEventfileName() -> None:
        eventfile_name = q_combobox_eventfile.currentText()
        control_manager.setSharedAttr(app_key, "eventfile_name", eventfile_name)
        canvas_control.updatePlotWithROISelect()

    q_button_load.clicked.connect(_loadEventFilesNPY)
    q_button_clear.clicked.connect(_clearDictEventfile)
    q_combobox_eventfile.currentIndexChanged.connect(_updateEventfileName)

# -> canvas_layouts.makeLayoutEventFilePlotProperty
def bindFuncCheckboxEventfilePlotProperty(
    q_checkbox_ffneu: 'QCheckBox',
    q_checkbox_dff0: 'QCheckBox',    
    canvas_control: 'CanvasControl'    
) -> None:
    def _onCheckboxChangedFFneu(state: int) -> None:
        is_checked_ffneu = (state == Qt.Checked)
        canvas_control.plot_ffneu = is_checked_ffneu
        canvas_control.updatePlotWithROISelect()
    def _onCheckboxChangedDff0(state: int) -> None:
        is_checked_dff0 = (state == Qt.Checked)
        canvas_control.plot_dff0 = is_checked_dff0
        canvas_control.updatePlotWithROISelect()
    q_checkbox_ffneu.stateChanged.connect(_onCheckboxChangedFFneu)
    q_checkbox_dff0.stateChanged.connect(_onCheckboxChangedDff0)

# -> canvas_layouts.makeLayoutCanvasTracePlot
def bindFuncButtonExportFigure(
    q_button: 'QPushButton', 
    q_window: 'QWidget',
    figure: Figure, 
    path_dst: str,
    dpi: int = 300
) -> None:
    def onButtonClicked(q_window, figure, path_dst, dpi) -> None:
        path_dst, is_overwrite = saveFileDialog(q_window, file_type=".png_pdf", initial_dir=path_dst)
        if path_dst:
            exportFigure(figure, path_dst, dpi)
    q_button.clicked.connect(lambda: onButtonClicked(q_window, figure, path_dst, dpi))

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
    widget_manager: 'WidgetManager',
    config_manager: 'ConfigManager',
    control_manager: 'ControlManager',
    app_key: str,
    local_var: bool = True
) -> None:
    gui_defaults = config_manager.gui_defaults
    table_columns = config_manager.table_columns[app_key]
    json_config = config_manager.json_config
    table_control = control_manager.table_controls[app_key]
    def _loadROICheck() -> None:
        loadROICheck(q_window, q_table, gui_defaults, table_columns, table_control)
        updateROICountDisplay(widget_manager, config_manager, app_key)
    q_button_save.clicked.connect(lambda: saveROICheck(q_window, q_lineedit, q_table, gui_defaults, table_columns, json_config, local_var))
    q_button_load.clicked.connect(lambda: _loadROICheck())

# -> io_layouts.makeLayoutROITrackingIO
def bindFuncROITrackingIO(
    q_button_save: 'QPushButton', 
    q_button_load: 'QPushButton', 
    q_window: 'QWidget', 
    q_lineedit_pri: 'QLineEdit', 
    q_lineedit_sec: 'QLineEdit',
    q_table_pri: 'QTableWidget',
    q_table_sec: 'QTableWidget', 
    widget_manager: 'WidgetManager',
    config_manager: 'ConfigManager',
    control_manager: 'ControlManager',
    app_key_pri: str,
    app_key_sec: str,
    local_var: bool = False
) -> None:
    gui_defaults = config_manager.gui_defaults
    json_config = config_manager.json_config
    def _loadROITracking() -> None:
        loadROITracking(
            q_window, 
            q_table_pri, 
            q_table_sec, 
            gui_defaults, 
            control_manager.table_controls[app_key_pri].table_columns, 
            control_manager.table_controls[app_key_sec].table_columns, 
            control_manager.table_controls[app_key_pri], 
            control_manager.table_controls[app_key_sec]
        )
        updateROICountDisplay(widget_manager, config_manager, app_key_pri)
        updateROICountDisplay(widget_manager, config_manager, app_key_sec)
    q_button_save.clicked.connect(lambda: saveROITracking(
        q_window, 
        q_lineedit_pri,
        q_lineedit_sec,
        q_table_pri, 
        q_table_sec,
        gui_defaults, 
        control_manager.table_controls[app_key_pri].table_columns, 
        control_manager.table_controls[app_key_sec].table_columns, 
        json_config, 
        local_var
        ))
    q_button_load.clicked.connect(lambda: _loadROITracking())

# -> io_layouts.makeLayoutROITrackingIO MicrogliaTracking
def bindFuncMicrogliaTrackingIO(
    q_button_save: 'QPushButton', 
    q_button_load: 'QPushButton', 
    q_window: 'QWidget', 
    q_lineedit: 'QLineEdit', 
    config_manager: 'ConfigManager',
    data_manager: 'DataManager',
    control_manager: 'ControlManager',
) -> None:
    gui_defaults = config_manager.gui_defaults
    json_config = config_manager.json_config
    def _saveMicrogliaTracking():
        dict_roi_coords_xyct = data_manager.getDictROICoordsXYCT()
        dict_roi_matching = data_manager.getDictROIMatching()
        saveMicrogliaTracking(
            q_window, 
            q_lineedit,
            gui_defaults, 
            json_config, 
            dict_roi_matching,
            dict_roi_coords_xyct
            )

    def _loadMicrogliaTracking() -> None:
        dict_roi_matching, dict_roi_coords_xyct = loadMicrogliaTracking(
            q_window, 
            gui_defaults, 
        )
        data_manager.dict_roi_matching = dict_roi_matching
        data_manager.dict_roi_coords_xyct = dict_roi_coords_xyct

        # hardcoded !!!
        # initialize ROI XYCT Colors
        for plane_t in data_manager.dict_roi_coords_xyct.keys():
            for roi_id in data_manager.dict_roi_coords_xyct[plane_t].keys():
                control_manager.view_controls["pri"].roi_colors_xyct[plane_t][roi_id] = generateRandomColor()
                control_manager.view_controls["sec"].roi_colors_xyct[plane_t][roi_id] = control_manager.view_controls["pri"].roi_colors_xyct[plane_t][roi_id]
                
        control_manager.view_controls["pri"].updateView()
        control_manager.view_controls["sec"].updateView()

        t_plane_pri = control_manager.view_controls["pri"].getPlaneT()
        t_plane_sec = control_manager.view_controls["sec"].getPlaneT()
        
        control_manager.table_controls["pri"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, True)
        control_manager.table_controls["sec"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, False)

    q_button_save.clicked.connect(lambda: _saveMicrogliaTracking())
    q_button_load.clicked.connect(lambda: _loadMicrogliaTracking())

# -> io_layouts.makeLayoutMaskNpyIO
def bindFuncROIMaskNpyIO(
    q_button_save: 'QPushButton', 
    q_button_load: 'QPushButton', 
    q_window: 'QWidget', 
    data_manager: 'DataManager',
    control_manager: 'ControlManager',
    app_key: str
) -> None:
    def _loadMaskNpy() -> None:
        loadCellposeMaskNPY(
            q_window, 
            data_manager, 
            app_key, 
            ndim=3,
        )
        data_manager.dict_roi_coords_xyct = convertCellposeMaskToDictROICoordsXYCT(data_manager.getROIMask(app_key))
        data_manager.dict_roi_coords_xyct_reg = deepcopy(data_manager.dict_roi_coords_xyct)
        data_manager.dict_roi_matching = convertCellposeMaskToDictROIMatching(data_manager.getROIMask(app_key))
        data_manager.dict_im_roi_xyct = getDictROIImageXYCTFromDictROICoords(data_manager.dict_roi_coords_xyct, data_manager.getImageSize(app_key)) 

        # initialize ROI XYCT Colors
        for plane_t in data_manager.dict_roi_coords_xyct.keys():
            for roi_id in data_manager.dict_roi_coords_xyct[plane_t].keys():
                control_manager.view_controls["pri"].roi_colors_xyct[plane_t][roi_id] = generateRandomColor()
                control_manager.view_controls["sec"].roi_colors_xyct[plane_t][roi_id] = control_manager.view_controls["pri"].roi_colors_xyct[plane_t][roi_id]

        control_manager.view_controls["pri"].updateView()
        control_manager.view_controls["sec"].updateView()

        t_plane_pri = control_manager.view_controls["pri"].getPlaneT()
        t_plane_sec = control_manager.view_controls["sec"].getPlaneT()
        
        control_manager.table_controls["pri"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, True)
        control_manager.table_controls["sec"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, False)

    q_button_load.clicked.connect(lambda: _loadMaskNpy())

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
def bindFuncCheckboxShowROIPair(
    q_checkbox: 'QCheckBox',
    view_controls: Dict[AppKeys, ViewControl]
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        for view_control in view_controls.values():
            view_control.setShowROIPair(is_visible)
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
    view_controls: Dict[AppKeys, ViewControl]
) -> None:
    def onVisibilityChanged(state: int) -> None:
        is_visible = (state == Qt.Checked)
        for view_control in view_controls.values():
            view_control.setShowRegStack(is_visible)
            view_control.updateView()
    q_checkbox.stateChanged.connect(onVisibilityChanged)

# -> processing_image_layouts.makeLayoutExportFallLike
def bindFuncButtonLoadCellposeMask(
    q_window: 'QWidget',
    q_button: 'QPushButton',
    view_control: 'ViewControl',
    data_manager: 'DataManager',
    app_key: AppKeys,
) -> None:
    def _loadMaskNpy() -> None:
        loadCellposeMaskNPY(
            q_window, 
            data_manager, 
            app_key, 
            ndim=2
        )
        data_manager.dict_roi_coords[app_key] = convertCellposeMaskToDictROICoords(data_manager.getROIMask(app_key))
        view_control.updateView()
    q_button.clicked.connect(_loadMaskNpy)

# -> processing_image_layouts.makeLayoutExportFallLike
def bindFuncButtonExportFallLike(
    q_window: 'QWidget',
    q_button: 'QPushButton',
    q_lineedit: 'QLineEdit',
    data_manager: 'DataManager',
) -> None:
    def _exportFallLike() -> None:
        from ..preprocessing.preprocessing_fall import makeFallLikeFromBgImageAndDictROICoords
        from scipy.io import savemat
        Falllike = makeFallLikeFromBgImageAndDictROICoords(data_manager)
        path_dst = q_lineedit.text().replace(".tif", "_Fall_like.mat")
        path_dst, _ = saveFileDialog(q_window, file_type=".mat", initial_dir=path_dst)
        savemat(path_dst, Falllike)
        QMessageBox.information(q_window, "Export Finish", "Exported Fall-like.mat!")
    q_button.clicked.connect(_exportFallLike)

"""
Elastix
"""
# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncButtonRunElastixForFall(
        q_widget: 'QWidget',
        q_button: 'QPushButton',
        data_manager: 'DataManager',
        config_manager: 'ConfigManager',
        control_manager: 'ControlManager',
        app_key: str,
        app_key_sec: str,
        combobox_elastix_method: QComboBox,
        path_points_txt: str="points_tmp.txt",
        output_directory: str="./elastix"
) -> None:
    def _runElastix():
        os.makedirs(output_directory, exist_ok=True)

        elastix_method = combobox_elastix_method.currentText()
        print(f"{elastix_method} transform")
        dict_params = config_manager.json_config.get("elastix_params")[elastix_method]
        data_manager.dict_parameter_map[app_key] = convertDictToElastixFormat(dict_params)
        parameter_object = makeElastixParameterObject(data_manager.getParameterMap(app_key))
        
        print("Elastix Parameters", dict_params)

        # get fixed image and moving image, (meanImg, meanImgE, max_proj, Vcorr)
        img_type_pri = control_manager.view_controls[app_key].getBackgroundImageType()
        img_fix = data_manager.getDictBackgroundImage(app_key).get(img_type_pri)
        img_type_sec = control_manager.view_controls[app_key_sec].getBackgroundImageType()
        img_mov = data_manager.getDictBackgroundImage(app_key_sec).get(img_type_sec)
        # run elastix
        transform_parameters = calculateSingleTransform(img_fix, img_mov, parameter_object, output_directory)
        data_manager.dict_transform_parameters[app_key] = transform_parameters
        # apply transform parameters to image
        # background image
        dict_im_bg_reg_mov = {}
        for key_im in data_manager.getDictBackgroundImage(app_key_sec).keys():
            dict_im_bg_reg_mov[key_im] = applySingleTransform(data_manager.getDictBackgroundImage(app_key_sec).get(key_im), transform_parameters, output_directory)
        data_manager.dict_im_bg_reg[app_key_sec] = dict_im_bg_reg_mov
        # ROI image
        img_roi_mov = deepcopy(data_manager.getDictROIImage(app_key_sec).get("all"))
        val_max = np.max(img_roi_mov)
        img_roi_mov_reg = applySingleTransform(img_roi_mov, transform_parameters, output_directory)
        img_roi_mov_reg_clipped = np.minimum(img_roi_mov_reg, val_max) # avoid making contours of ROIs
        data_manager.dict_im_roi_reg[app_key_sec]["all"] = img_roi_mov_reg_clipped
        
        # ROI coordinates
        path_transform_parameters_file = os.path.join(output_directory,"TransformParameters.0.txt") # hardcoded !!!
        dict_roi_coords = data_manager.getDictROICoords(app_key_sec)
        dict_roi_coords_reg = applyDictROICoordsTransform(
            img_fix, img_mov, 
            dict_roi_coords, 
            data_manager.getParameterMap(app_key),
            path_transform_parameters_file, 
            path_points_txt, 
            output_directory
            )
        data_manager.dict_roi_coords_reg[app_key_sec] = dict_roi_coords_reg

        control_manager.view_controls[app_key].updateView()
        control_manager.view_controls[app_key_sec].updateView()

        shutil.rmtree(output_directory)
        os.remove(path_points_txt)
        QMessageBox.information(q_widget, "Image Registration Finish", "Image Registration Finished!")
    q_button.clicked.connect(lambda: _runElastix())

# -> processing_image_layouts.makeLayoutStackRegistration
def bindFuncButtonRunElastixForSingleStack(
        q_widget: 'QWidget',
        q_button: 'QPushButton',
        data_manager: 'DataManager',
        config_manager: 'ConfigManager',
        app_key: str,
        combobox_elastix_method: QComboBox,
        combobox_channel_ref: QComboBox,
        combobox_idx_ref: QComboBox,
        axis: Literal["t", "z"],
        output_directory: str="./elastix"
) -> None:
    def _runElastix():
        os.makedirs(output_directory, exist_ok=True)

        elastix_method = combobox_elastix_method.currentText() # rigid, affine, bspline
        channel_ref = int(combobox_channel_ref.currentText()) # 0, 1, 2
        idx_ref = int(combobox_idx_ref.currentText()) # 0, 1, 2, ...
        print(f"{elastix_method} transform")
        print("Reference channel:", channel_ref)
        print(f"Reference {axis} plane:", idx_ref)
        # get image stack and elastix parameters
        img_stack = data_manager.getTiffStack(app_key)
        dict_params = config_manager.json_config.get("elastix_params")[elastix_method]
        data_manager.dict_parameter_map[app_key] = convertDictToElastixFormat(dict_params)
        parameter_object = makeElastixParameterObject(data_manager.getParameterMap(app_key))
        print("Elastix Parameters", dict_params)

        # stack registration
        dict_transform_parameters, img_stack_reg = runStackRegistration(img_stack, parameter_object, channel_ref, idx_ref, axis, output_directory)
        data_manager.dict_transform_parameters[app_key] = dict_transform_parameters
        data_manager.dict_tiff_reg[app_key] = img_stack_reg
        shutil.rmtree(output_directory)

        QMessageBox.information(q_widget, "Image Registration Finish", "Image Registration Finished!")
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

# -> processing_image_layouts.makeLayoutSaveElastixTransform
def bindFuncButtonSaveElastixTransform(
    q_widget: QWidget,
    q_button: QPushButton,
    q_linnedit: QLineEdit,
    data_manager: DataManager,
    app_key: AppKeys,
    gui_defaults: GuiDefaults,
) -> None:
    def _saveElastixTransformParameters():
        transform_parameters = data_manager.dict_transform_parameters.get(app_key)
        if not transform_parameters:
            QMessageBox.warning(q_widget, "No Elastix Transform Parameters", "No Elastix Transform Parameters to save!")
            return
        initial_dir = f'{q_linnedit.text().split(".")[0]}_TransformParameters'

        saveElastixTransformParameters(q_widget, gui_defaults, initial_dir, transform_parameters)
        QMessageBox.information(q_widget, "Save Elastix Transform Parameters", "Elastix Transform Parameters saved successfully!")
    q_button.clicked.connect(_saveElastixTransformParameters)

def bindFuncButtonApplyElastixTransform_XYCTtoXYCZT(
    q_widget: QWidget,
    q_button: QPushButton,
    data_manager: DataManager,
    app_key: AppKeys,
    output_directory: str="./elastix"
) -> None:
    def _applyElastixTransform_XYCTtoXYCZT():
        os.makedirs(output_directory, exist_ok=True)

        img_stack = data_manager.getTiffStack(app_key)
        transform_parameters_XYCT = loadElastixTransformParameters(q_widget)
        num_z = data_manager.getSizeOfZ(app_key)
        transform_parameters_XYCZT = duplicateTransformParameters(transform_parameters_XYCT, axis="z", num_z=num_z)
        img_stack_reg = applyStackTransform(img_stack, transform_parameters_XYCZT, output_directory)
        data_manager.dict_transform_parameters[app_key] = transform_parameters_XYCZT
        data_manager.dict_tiff_reg[app_key] = img_stack_reg
        shutil.rmtree(output_directory)

        QMessageBox.information(q_widget, "Image Registration Finish", "Image Registration Finished!")
    q_button.clicked.connect(_applyElastixTransform_XYCTtoXYCZT)

# -> processing_image_layouts.makeLayoutMicrogliaXYCTStackRegistration
def bindFuncButtonRunElastixForMicrogliaXYCTStackRegistration(
        q_widget: 'QWidget',
        q_button: 'QPushButton',
        data_manager: 'DataManager',
        config_manager: 'ConfigManager',
        app_keys: List[str],
        combobox_elastix_method: QComboBox,
        combobox_channel_ref: QComboBox,
        combobox_idx_ref: QComboBox,
        path_points_txt: str="./elastix/points_tmp.txt",
        output_directory: str="./elastix"
) -> None:
    def _runElastix():
        axis = "t"
        app_key_pri = app_keys[0]
        z_ref = 0
        c_ref = 0
        os.makedirs(output_directory, exist_ok=True)

        elastix_method = combobox_elastix_method.currentText()
        channel_ref = int(combobox_channel_ref.currentText())
        idx_ref = int(combobox_idx_ref.currentText())
        print(f"{elastix_method} transform")
        print("Reference channel:", channel_ref)
        print(f"Reference {axis} plane:", idx_ref)
        img_stack = data_manager.getTiffStack(app_key_pri)
        dict_params = config_manager.json_config.get("elastix_params")[elastix_method]
        data_manager.dict_parameter_map[app_key_pri] = convertDictToElastixFormat(dict_params)
        parameter_object = makeElastixParameterObject(data_manager.getParameterMap(app_key_pri))
        print("Elastix Parameters", dict_params)

        dict_transform_parameters, img_stack_reg = runStackRegistration(img_stack, parameter_object, channel_ref, idx_ref, axis, output_directory)

        for app_key in app_keys:
            data_manager.dict_transform_parameters[app_key] = dict_transform_parameters
            # background image
            data_manager.dict_tiff_reg[app_key] = img_stack_reg

            # # ROI image
            # img_roi_mov = deepcopy(data_manager.getDictROIImage(app_key_sec).get("all"))
            # val_max = np.max(img_roi_mov)
            # img_roi_mov_reg = applySingleTransform(img_roi_mov, transform_parameters, output_directory)
            # img_roi_mov_reg_clipped = np.minimum(img_roi_mov_reg, val_max) # avoid making contours of ROIs
            # data_manager.dict_im_roi_reg[app_key_sec]["all"] = img_roi_mov_reg_clipped
            
        # ROI coordinates
        # save transform parameters for applying ROI transform
        for zt_plane in dict_transform_parameters.keys(): # zt_plane: z0_t0, z0_t1, z0_t2, ...
            t_plane_pri = int(zt_plane.split("t")[1])
            param = dict_transform_parameters[zt_plane]
            path_dst = f"{output_directory}/TransformParameters_{zt_plane}.txt"
            param.WriteParameterFile(param, path_dst)

            img_fix = data_manager.getImageFromXYCZTTiffStack(app_keys[0], z_ref, t_plane_pri, c_ref)
            img_mov = img_fix.copy() # tmp
            dict_roi_coords_xyct_reg_singlet = applyDictROICoordsTransform(
                img_fix, img_mov, 
                data_manager.dict_roi_coords_xyct[t_plane_pri], 
                data_manager.getParameterMap(app_key_pri),
                path_dst, 
                path_points_txt, 
                output_directory
                )

            data_manager.dict_roi_coords_xyct_reg[t_plane_pri] = dict_roi_coords_xyct_reg_singlet
        # shutil.rmtree(output_directory)

        QMessageBox.information(q_widget, "Image Registration Finish", "Image Registration Finished!")
    q_button.clicked.connect(lambda: _runElastix())

"""
processing_roi_layouts
"""
def bindFuncButtonRunROIMatching(
    q_widget: 'QWidget',
    q_button: 'QPushButton',
    q_buttongroup_celltype_pri: 'QButtonGroup',
    q_buttongroup_celltype_sec: 'QButtonGroup',
    widget_manager: 'WidgetManager',
    data_manager: 'DataManager',
    control_manager: 'ControlManager',
    app_key_pri: str,
    app_key_sec: str,
):
    def _runROIMatching():
        view_control_pri = control_manager.view_controls[app_key_pri]
        roi_display_type_pri = q_buttongroup_celltype_pri.checkedButton().text()
        roi_display_type_sec = q_buttongroup_celltype_sec.checkedButton().text()
        result = showConfirmationDialog(
            q_widget,
            'Confirmation',
            f"Match only displayed ROIs? \nYes: Match {roi_display_type_pri} ROIs and {roi_display_type_sec} ROIs \nNo: Match all ROIs \nCancel: Cancel"
        )
        # use registered coordinates if show_reg_im_roi is True
        if view_control_pri.show_reg_im_roi:
            array_src = np.array([data_manager.getDictROICoordsRegistered(app_key_pri)[idx]["med"] for idx in range(data_manager.getNROIs(app_key_pri))])
            array_tgt = np.array([data_manager.getDictROICoordsRegistered(app_key_sec)[idx]["med"] for idx in range(data_manager.getNROIs(app_key_sec))])
        else:
            array_src = np.array([data_manager.getDictROICoords(app_key_pri)[idx]["med"] for idx in range(data_manager.getNROIs(app_key_pri))])
            array_tgt = np.array([data_manager.getDictROICoords(app_key_sec)[idx]["med"] for idx in range(data_manager.getNROIs(app_key_sec))])
        
        if result == QMessageBox.Yes:
            roi_display_pri = list(control_manager.getSharedAttr(app_key_pri, "roi_display").values())
            roi_display_sec = list(control_manager.getSharedAttr(app_key_sec, "roi_display").values())
            array_src = array_src[roi_display_pri]
            array_tgt = array_tgt[roi_display_sec]
        elif result == QMessageBox.Cancel:
            return 
        else:
            pass

        roi_matching = calculateROIMatching(
                    array_src=array_src,
                    array_tgt=array_tgt,
                    method=widget_manager.dict_combobox["ot_method"].currentText(),
                    loss_fun="square_loss",
                    metric="minkowski",
                    p=float(widget_manager.dict_lineedit["wd_exp"].text()),
                    alpha=float(widget_manager.dict_lineedit["fgwd_alpha"].text()),
                    threshold=float(widget_manager.dict_lineedit["ot_threshold_transport"].text()),
                    max_cost=float(widget_manager.dict_lineedit["ot_threshold_cost"].text()),
                )
        # convert roi_matching id to original id
        true_idxs_pri = np.nonzero(roi_display_pri)[0][list(roi_matching.keys())]
        true_idxs_sec = np.nonzero(roi_display_sec)[0][list(roi_matching.values())]
        roi_matching = dict(zip(true_idxs_pri, true_idxs_sec))

        control_manager.table_controls[app_key_pri].updateMatchedROIPairs(roi_matching)
        control_manager.view_controls[app_key_pri].updateView()
        QMessageBox.information(q_widget, "ROI Matching Finish", "ROI Matching Finished!")
    q_button.clicked.connect(_runROIMatching)

# -> processing_roi_layouts.makeLayoutROIManagerForTable
def bindFuncButtonsROIManagerForTable(
    q_button_add: 'QPushButton',
    q_button_remove: 'QPushButton',
    q_button_edit: 'QPushButton',
    q_table: 'QTableWidget',
    data_manager: 'DataManager',
    control_manager: 'ControlManager',
    table_control: 'TableControl',
    view_control: 'ViewControl',
    app_key_pri: AppKeys,
    app_key_sec: AppKeys,
) -> None:
    def _addROItoTable() -> None:
        if not view_control.roi_edit_mode:
            view_control.roi_edit_mode = True
            view_control.q_view.setFocus()
            print("roi_edit_mode:", view_control.roi_edit_mode)

            if not data_manager.dict_roi_matching["id"][view_control.getPlaneT()]:
                roi_id_edit = 0
            else:
                roi_id_edit = max(data_manager.dict_roi_matching["id"][view_control.getPlaneT()]) + 1 # new roi id, last ID+1
            view_control.view_handler.handler.roi_id_edit = roi_id_edit # for adding new roi

            plane_t_pri = control_manager.view_controls[app_key_pri].getPlaneT()
            plane_t_sec = control_manager.view_controls[app_key_sec].getPlaneT()
            plane_t = plane_t_pri if view_control.app_key == app_key_pri else plane_t_sec # pri or sec
            view_control.view_handler.handler.plane_t_pri = plane_t_pri
            view_control.view_handler.handler.plane_t_sec = plane_t_sec
            view_control.view_handler.handler.plane_t = plane_t

            view_control.view_handler.handler.roi_reg = view_control.show_reg_im_roi # registered roi or not
            view_control.view_handler.handler.roi_add_mode = True

    def _removeSelectedROIfromTable() -> None:
        row = q_table.currentRow()
        roi_selected_id = table_control.getCellIdFromRow(row)
        plane_t_pri = control_manager.view_controls[app_key_pri].getPlaneT()
        plane_t_sec = control_manager.view_controls[app_key_sec].getPlaneT()
        plane_t = plane_t_pri if view_control.app_key == app_key_pri else plane_t_sec # pri or sec
        # remove selected roi from dict_roi_matching, dict_roi_coords_xyct
        if roi_selected_id:
            data_manager.dict_roi_matching["id"][plane_t].remove(roi_selected_id)
            # remove all sec ROI of pri-sec pair
            for plane_t_pri_tmp in data_manager.dict_roi_matching["match"].keys(): # search all plane_t_pri
                for plane_t_sec_tmp in data_manager.dict_roi_matching["match"][plane_t_pri_tmp].keys(): # search all plane_t_sec
                    if plane_t == plane_t_sec_tmp: # choosed plane_t
                        for roi_pri, roi_sec in data_manager.dict_roi_matching["match"][plane_t_pri_tmp][plane_t].items():
                            if roi_sec == roi_selected_id:
                                data_manager.dict_roi_matching["match"][plane_t_pri_tmp][plane_t_sec_tmp][roi_pri] = None
            # remove all pri ROI of pri-sec pair
            for plane_t_sec_tmp in data_manager.dict_roi_matching["match"][plane_t].keys():
                del data_manager.dict_roi_matching["match"][plane_t][plane_t_sec_tmp][roi_selected_id]

            del data_manager.dict_roi_coords_xyct[plane_t][roi_selected_id]
            del data_manager.dict_roi_coords_xyct_reg[plane_t][roi_selected_id]
            print("ROI", roi_selected_id, "is removed.")
        table_control.setSharedAttr_ROISelected(None) # clear selected roi
        view_control.updateView()
        control_manager.table_controls[app_key_pri].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, plane_t_pri, plane_t_sec, True)
        control_manager.table_controls[app_key_sec].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, plane_t_pri, plane_t_sec, False)

    def _editSelectedROI() -> None:
        if not view_control.roi_edit_mode:
            roi_id_edit = control_manager.getSharedAttr(view_control.app_key, "roi_selected_id")
            if roi_id_edit is None:
                QMessageBox.warning(q_table, "No ROI Selected", "Please select a ROI to edit.")
                return
            view_control.view_handler.handler.roi_id_edit = roi_id_edit

            view_control.roi_edit_mode = True
            view_control.q_view.setFocus()
            print("roi_edit_mode:", view_control.roi_edit_mode)

            plane_t_pri = control_manager.view_controls[app_key_pri].getPlaneT()
            plane_t_sec = control_manager.view_controls[app_key_sec].getPlaneT()
            plane_t = plane_t_pri if view_control.app_key == app_key_pri else plane_t_sec # pri or sec
            view_control.view_handler.handler.plane_t_pri = plane_t_pri
            view_control.view_handler.handler.plane_t_sec = plane_t_sec
            view_control.view_handler.handler.plane_t = plane_t

            # registered roi or not
            dict_roi_coords_xyct_selected = data_manager.dict_roi_coords_xyct_reg[plane_t][roi_id_edit] if view_control.show_reg_im_roi else data_manager.dict_roi_coords_xyct[plane_t][roi_id_edit]
            view_control.view_handler.handler.roi_points_edit = set([(x, y) for x, y in zip(dict_roi_coords_xyct_selected["xpix"], dict_roi_coords_xyct_selected["ypix"])])
            view_control.view_handler.handler.roi_add_mode = False

    q_button_add.clicked.connect(_addROItoTable)
    q_button_remove.clicked.connect(_removeSelectedROIfromTable)
    q_button_edit.clicked.connect(_editSelectedROI)

# -> processing_roi_layouts.makeLayoutROIEditConfig
def bindFuncSliderSpinBoxROIEditConfig(
    q_slider_opacity: QSlider,
    q_spinbox_radius: QSpinBox, 
    view_control: ViewControl,      
) -> None:
    def onOpacityChanged(value: int) -> None:
        view_control.roi_edit_opacity = value
        view_control.view_handler.handler.updateROIEditLayer()
    def onRadiusChanged(value: int) -> None:
        view_control.roi_edit_radius = value
        view_control.view_handler.handler.updateROIEditLayer()

    q_slider_opacity.valueChanged.connect(onOpacityChanged)
    q_spinbox_radius.valueChanged.connect(onRadiusChanged)

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
    view_control: 'ViewControl',
) -> None:
    def onTChanged(value: int) -> None:
        view_control.setPlaneT(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onTChanged)

# -> view_layouts.makeLayoutViewWithZTSlider for Microglia Tracking
def bindFuncPlaneTSliderWithXYCTTracking(
    q_slider_pri: 'QSlider',
    q_slider_sec: 'QSlider',
    data_manager: 'DataManager',
    control_manager: 'ControlManager',
    table_control_pri: 'TableControl',
    table_control_sec: 'TableControl',
) -> None:
    def onTChanged(value: int, app_key: AppKeys) -> None:
        # "pri" value should be less than "sec" value
        if app_key == "pri": # pri slider changed
            if value >= q_slider_pri.maximum():
                return
            elif value >= q_slider_sec.value():
                q_slider_sec.setValue(value + 1)
        else: # sec slider changed
            if value <= q_slider_sec.minimum():
                return
            elif value <= q_slider_pri.value():
                q_slider_pri.setValue(value - 1)

        control_manager.view_controls[app_key].setPlaneT(value)
        control_manager.table_controls[app_key].setPlaneT(value)

        """
        Critical Bug
        To avoid app crash, clear selected_roi of both tables
        """
        table_control_pri.setSharedAttr_ROISelected(None)
        table_control_sec.setSharedAttr_ROISelected(None)

        try:
            # hardcoded !!!
            t_plane_pri = control_manager.view_controls["pri"].getPlaneT()
            t_plane_sec = control_manager.view_controls["sec"].getPlaneT()
            
            control_manager.table_controls["pri"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, True)
            control_manager.table_controls["sec"].updateWidgetDynamicTableWithT(data_manager.dict_roi_matching, t_plane_pri, t_plane_sec, False)

            # hardcoded !!!
            control_manager.view_controls["pri"].updateView()
            control_manager.view_controls["sec"].updateView()
        except Exception as e:
            # raise e
            pass
        
    q_slider_pri.valueChanged.connect(lambda value: onTChanged(value, "pri")) # hardcoded !!!
    q_slider_sec.valueChanged.connect(lambda value: onTChanged(value, "sec")) # hardcoded !!!

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

# -> processing_image_layouts.makeLayoutFallRegistration
def bindFuncROIPairOpacitySlider(
    q_slider: 'QSlider', 
    view_control: 'ViewControl'
) -> None:
    def onOpacityChanged(value: int) -> None:
        view_control.setROIPairOpacity(value)
        view_control.updateView()
    q_slider.valueChanged.connect(onOpacityChanged)

"""
table_layouts
"""
# -> table_layouts
def bindFuncButtonClearColumnCells(
    q_button: 'QPushButton', 
    q_table: 'QTableWidget', 
    idx_col: int
) -> None:
    q_button.clicked.connect(lambda: clearColumnCells(q_table, idx_col))

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
def bindFuncTableSelectionChangedWithTracking(
    q_table_pri: 'QTableWidget', 
    q_table_sec: 'QTableWidget',
    table_control_pri: 'TableControl', 
    table_control_sec: 'TableControl',
    view_control_pri: 'ViewControl', 
    view_control_sec: 'ViewControl',
    canvas_control_pri: 'CanvasControl',
    canvas_control_sec: 'CanvasControl'
) -> None:
    def _onSelectionChangedWithTracking(selected, deselected) -> None: # for "pri" table
        if selected.indexes():
            table_control_pri.onSelectionChangedWithTracking(selected, deselected)
            row = table_control_pri.getSharedAttr_ROIMatch()
            table_control_sec.updateSelectedROI(row)
            view_control_pri.updateView()
            view_control_sec.updateView()
            if canvas_control_pri: # for canvas_control
                canvas_control_pri.updatePlotWithROISelect()
    def _onSelectionChanged(selected, deselected) -> None: # for "sec" table
        if selected.indexes():
            table_control_sec.onSelectionChanged(selected, deselected)
            view_control_sec.updateView()
            if canvas_control_sec: # for canvas_control
                canvas_control_sec.updatePlotWithROISelect()
    q_table_pri.selectionModel().selectionChanged.connect(_onSelectionChangedWithTracking)
    q_table_sec.selectionModel().selectionChanged.connect(_onSelectionChanged)

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

# -> table_layouts.makeLayoutROIFilterButton
def bindFuncButtonFilterROI(
    q_button: 'QPushButton',
    dict_q_lineedit: Dict[str, 'QLineEdit'],
    table_control: 'TableControl', 
    view_control: 'ViewControl',
) -> None:
    q_button.clicked.connect(
        lambda: table_control.filterROI(getThresholdsOfROIFilter(dict_q_lineedit))
    )
    view_control.updateView()

# -> MicrogliaTracking, ROI Table
def bindFuncTableCellChangedWithMicrogliaTracking(
    q_table_pri: 'QTableWidget',
    control_manager: 'ControlManager',
    data_manager: 'DataManager',
) -> None:
    def _onEditingFinished() -> None:
        try:
            current_row = q_table_pri.currentRow()

            # get the maximum roi id of the secondary plane
            t_plane_pri = control_manager.view_controls["pri"].getPlaneT()
            t_plane_sec = control_manager.view_controls["sec"].getPlaneT()
            max_roi_id_sec = data_manager.dict_roi_matching["id"][t_plane_sec][-1]

            # get the new value
            item_pri_id = q_table_pri.item(current_row, 0)
            item_pri_id_match = q_table_pri.item(current_row, 1)

            if item_pri_id is None: # skip
                return
            else:
                if item_pri_id_match is None: # set blank
                    data_manager.dict_roi_matching["match"][t_plane_pri][t_plane_sec][roi_id_pri] = None
                    return
            roi_id_pri = item_pri_id.text()
            roi_id_sec = item_pri_id_match.text()
            if roi_id_sec == "": # set blank
                roi_id_pri = int(roi_id_pri)
                data_manager.dict_roi_matching["match"][t_plane_pri][t_plane_sec][roi_id_pri] = None
                return

            roi_id_pri = int(roi_id_pri)
            roi_id_sec = int(roi_id_sec)

            # check the validity of the roi id
            if 0 <= roi_id_sec <= max_roi_id_sec:
                data_manager.dict_roi_matching["match"][t_plane_pri][t_plane_sec][roi_id_pri] = roi_id_sec
        except ValueError:
            print("Invalid input: not an integer")
        except KeyError as e:
            print(f"KeyError: {e}")
        except AttributeError as e: # set blank
            data_manager.dict_roi_matching["match"][t_plane_pri][t_plane_sec][roi_id_pri] = None
        except IndexError as e:
            print(f"IndexError: {e}")

    q_table_pri.itemChanged.connect(_onEditingFinished)

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

# -> view_layouts.makeLayoutROIChooseSkip, Neuron, Not Cell, Check, ...
def bindFuncCheckBoxROIChooseSkip(
    list_q_checkbox: List['QCheckBox'],
    control_manager: 'ControlManager',
    app_key: AppKeys,
) -> None:
    def _onCheckBoxChanged(state: int, q_checkbox_text: str) -> None:
        is_checked = (state == Qt.Checked)
        celltype = q_checkbox_text.split(" ")[1]
        control_manager.setSharedAttrDictValue(app_key, "skip_roi_types", celltype, is_checked)
    for q_checkbox in list_q_checkbox:
        q_checkbox.stateChanged.connect(lambda state, q_checkbox_text=q_checkbox.text(): _onCheckBoxChanged(state, q_checkbox_text))

# -> view_layouts.makeLayoutDisplayROIContourNext
def bindFuncCheckBoxDisplayROIContourNext(
    q_checkbox_contour: 'QCheckBox', 
    q_checkbox_next: 'QCheckBox',
    view_control: 'ViewControl'
) -> None:
    def _onCheckBoxChanged(state: int, prop: str) -> None:
        is_checked = (state == Qt.Checked)
        view_control.setROIDisplayProp(prop, is_checked)
        view_control.updateView()
    q_checkbox_contour.stateChanged.connect(lambda state: _onCheckBoxChanged(state, "contour"))
    q_checkbox_next.stateChanged.connect(lambda state: _onCheckBoxChanged(state, "next"))


