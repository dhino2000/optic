from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from ..preprocessing.preprocessing_roi import getROIContour
from ..config.constants import PenColors, PenWidth
import numpy as np

"""
update layer_roi
"""
# update layer_roi for Suite2pROICheck
def updateLayerROI_Suite2pROICheck(
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        draw_selected_roi: bool = True
        ) -> None:
    width, height = view_control.getImageSize()
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent) 

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(app_key, "roi_display")
    ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    
    # draw all ROIs except selected ROI
    dict_roi_coords = data_manager.getDictROICoords(app_key)
    for roiId, dict_roi_coords_single in dict_roi_coords.items():
        if roi_display[roiId] and roiId != ROISelectedId:
            color = view_control.getROIColor(roiId)
            opacity = view_control.getROIOpacity()
            drawROI(painter, dict_roi_coords_single, color, opacity)

    # draw selected ROI
    if draw_selected_roi:
        dict_roi_coords_selected = dict_roi_coords[ROISelectedId]
        color_selected = view_control.getROIColor(ROISelectedId)
        opacity_selected = view_control.getHighlightOpacity()
        # draw contour of selected ROI
        if view_control.getROIDisplayProp("contour"):
            drawROIContour(painter, dict_roi_coords_selected, color_selected, opacity_selected)
        else:
            drawROI(painter, dict_roi_coords_selected, color_selected, opacity_selected)

    # draw next ROI of selected ROI, with White color
    if view_control.getROIDisplayProp("next"):
        dict_roi_coords_selected_next = dict_roi_coords.get(ROISelectedId+1)
        if dict_roi_coords_selected_next:
            drawROIContour(painter, dict_roi_coords_selected_next, (255, 255, 255), opacity_selected)

    painter.end()
    view_control.layer_roi.setPixmap(pixmap)

# update layer_roi for Suite2pROITracking
def updateLayerROI_Suite2pROITracking(
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key_pri: AppKeys,
        app_key_sec: AppKeys,
        draw_selected_roi: bool = True
        ) -> None:
    width, height = view_control.getImageSize()
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent) 

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(app_key_pri, "roi_display")
    ROISelectedId = control_manager.getSharedAttr(app_key_pri, "roi_selected_id")

    if view_control.show_reg_im_roi:
        dict_roi_coords = data_manager.getDictROICoordsRegistered(app_key_pri)
    else:
        dict_roi_coords = data_manager.getDictROICoords(app_key_pri)
    
    for roiId, dict_roi_coords_single in dict_roi_coords.items():
        if roi_display[roiId] and roiId != ROISelectedId:
            color = view_control.getROIColor(roiId)
            opacity = view_control.getROIOpacity()
            drawROI(painter, dict_roi_coords_single, color, opacity)

    # draw selected ROI, on "pri" view, draw also "sec" selected ROI
    highlightROISelectedWithTracking(view_control, painter, data_manager, control_manager, app_key_pri, app_key_sec)

    # draw ROI pairs
    drawROIPairsOnlyDisplay(view_control, painter, data_manager, control_manager, ROISelectedId, app_key_pri, app_key_sec)

    painter.end()
    from ..visualization.view_visual import resetZoomView
    resetZoomView(view_control.q_view, view_control.q_scene.sceneRect())
    view_control.layer_roi.setPixmap(pixmap)

# update layer_roi for MicrogliaTracking
def updateLayerROI_MicrogliaTracking(
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        app_key_sec: AppKeys = None,
        draw_selected_roi: bool = True
        ) -> None:
    width, height = view_control.getImageSize()
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent) 

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    plane_t = view_control.getPlaneT()
    
    # WARNING: this code often causes crash, be careful when data_manager.dict_roi_coords_xyct is None
    if view_control.getShowRegImROI(): # show registered ROIs
        dict_roi_coords_xyct = data_manager.getDictROICoordsXYCTRegistered()
    else:
        dict_roi_coords_xyct = data_manager.getDictROICoordsXYCT()
    dict_roi_coords_xyct_tplane = dict_roi_coords_xyct.get(plane_t)
    if not len(dict_roi_coords_xyct_tplane) == 0:
        for roiId, dict_roi_coords_single in dict_roi_coords_xyct_tplane.items():
            if roiId != ROISelectedId:
                color = view_control.getROIColorXYCT(plane_t, roiId)
                opacity = view_control.getROIOpacity()
                drawROI(painter, dict_roi_coords_single, color, opacity)

        # draw selected ROI
        if draw_selected_roi and ROISelectedId is not None:
            dict_roi_coords_selected = dict_roi_coords_xyct_tplane[ROISelectedId]
            color_selected = view_control.getROIColorXYCT(plane_t, ROISelectedId)
            opacity_selected = view_control.getHighlightOpacity()
            drawROI(painter, dict_roi_coords_selected, color_selected, opacity_selected)

    # "pri" view, draw also "sec" ROI
    if app_key_sec:
        view_control_sec = control_manager.view_controls[app_key_sec]
        plane_t_sec = view_control_sec.getPlaneT()
        if view_control.getShowRegImROI(): # show registered ROIs
            dict_roi_coords_xyct = data_manager.getDictROICoordsXYCTRegistered()
        else:
            dict_roi_coords_xyct = data_manager.getDictROICoordsXYCT()
        dict_roi_coords_xyct_tplane = dict_roi_coords_xyct.get(plane_t_sec)
        if not len(dict_roi_coords_xyct_tplane) == 0:
            for roiId, dict_roi_coords_single in dict_roi_coords_xyct_tplane.items():
                if roiId != ROISelectedId:
                    color = (0, 0, 255) # blue
                    opacity = view_control_sec.getROIOpacity()
                    drawROI(painter, dict_roi_coords_single, color, opacity)

    painter.end()
    view_control.layer_roi.setPixmap(pixmap)

# update layer_roi for TIFStackExplorer
def updateLayerROI_TIFStackExplorer(
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        draw_selected_roi: bool = True
    ) -> None:
    width, height = view_control.getImageSize()
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent) 

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    # roi_display = control_manager.getSharedAttr(app_key, "roi_display")
    # ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    
    # draw all ROIs except selected ROI
    dict_roi_coords = data_manager.getDictROICoords(app_key)
    if dict_roi_coords is not None:
        for roiId, dict_roi_coords_single in dict_roi_coords.items():
            color = (0, 0, 255) # hardcoded !!!
            opacity = 255 # hardcoded !!!
            drawROI(painter, dict_roi_coords_single, color, opacity)

    painter.end()
    view_control.layer_roi.setPixmap(pixmap)

"""
ROI drawing functions
"""
# draw single ROI
def drawROI(
        painter: QPainter, 
        dict_roi_coords_single: Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]],
        color: Tuple[int, int, int],
        opacity: int
        ) -> None:
    xpix, ypix = dict_roi_coords_single["xpix"], dict_roi_coords_single["ypix"]
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

# draw single ROI contour
def drawROIContour(
        painter: QPainter, 
        dict_roi_coords_single: Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]],
        color: Tuple[int, int, int],
        opacity: int
        ) -> None:
    xpix, ypix = dict_roi_coords_single["xpix"], dict_roi_coords_single["ypix"]
    xpix_contour, ypix_contour = getROIContour(xpix, ypix)
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix_contour, ypix_contour):
        painter.drawPoint(int(x), int(y))

# draw single ROI pair
# WARNING !!! Suite2p Fall's ROI center (med) is in the format of (y, x),
def drawROIPair(
        painter: QPainter,
        coords_pri: Tuple[int, int],
        coords_sec: Tuple[int, int],
        opacity: int,
) -> None:
    y_pri, x_pri = coords_pri
    y_sec, x_sec = coords_sec
    color = PenColors.ROI_PAIR
    width = PenWidth.ROI_PAIR
    
    qcolor = QColor(color)
    qcolor.setAlpha(opacity)
    pen = QPen(qcolor)
    pen.setWidth(width)
    painter.setPen(pen)
    # draw line
    painter.drawLine(x_pri, y_pri, x_sec, y_sec)
    # draw circle
    marker_size = width * 1
    painter.drawEllipse(x_pri - marker_size//2, y_pri - marker_size//2, marker_size, marker_size)
    painter.drawEllipse(x_sec - marker_size//2, y_sec - marker_size//2, marker_size, marker_size)

# find Closest ROI to click position
def findClosestROI(
        x: int, 
        y: int, 
        dict_roi_med: Dict[int, Tuple[int, int]],
        skip_roi: Dict[int, bool] = None
        ) -> Optional[int]:
    if not dict_roi_med:
        return None
    
    min_distance = float('inf')
    closest_roi_id = None

    for roi_id, med in dict_roi_med.items():
        if skip_roi and skip_roi.get(roi_id, False):
            continue
        """
        WARNING !!!
        Suite2p Fall's ROI center (med) is in the format of (y, x),
        """
        distance = np.sqrt((x - med[1])**2 + (y - med[0])**2)
        if distance < min_distance:
            min_distance = distance
            closest_roi_id = roi_id

    return closest_roi_id

# Skip ROIs with "Skip" checkbox checked
def shouldSkipROI(
        roi_id: int, 
        table_columns: TableColumns, 
        q_table: QTableWidget, 
        skip_roi_types: Dict[str, bool],
        ) -> bool:
    for celltype, skip in skip_roi_types.items():
        if skip:
            for col_name, col_info in table_columns.getColumns().items():
                if col_name == celltype:
                    if col_info['type'] == 'celltype':
                        radio_button = q_table.cellWidget(roi_id, col_info['order'])
                        if radio_button and radio_button.isChecked():
                            return True
                    elif col_info['type'] == 'checkbox':
                        checkbox_item = q_table.item(roi_id, col_info['order'])
                        if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                            return True
    return False

# highlight selected ROI with tracking
def highlightROISelectedWithTracking(
        view_control: ViewControl, 
        painter: QPainter, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key_pri: AppKeys,
        app_key_sec: AppKeys = None
        ) -> None:
    # pri selected ROI
    ROISelectedId = control_manager.getSharedAttr(app_key_pri, "roi_selected_id")
    if ROISelectedId is not None:
        if view_control.show_reg_im_roi:
            dict_roi_coords_single = data_manager.getDictROICoordsRegistered(app_key_pri)[ROISelectedId]
        else:
            dict_roi_coords_single = data_manager.getDictROICoords(app_key_pri)[ROISelectedId]
        color = view_control.getROIColor(ROISelectedId)
        opacity = view_control.getHighlightOpacity()
        drawROI(painter, dict_roi_coords_single, color, opacity)

    # sec selected ROI
    if app_key_sec is not None:
        ROISelectedId = control_manager.getSharedAttr(app_key_sec, "roi_selected_id")
        if ROISelectedId is not None:
            if view_control.show_reg_im_roi:
                dict_roi_coords_single = data_manager.getDictROICoordsRegistered(app_key_sec)[ROISelectedId]
            else:
                dict_roi_coords_single = data_manager.getDictROICoords(app_key_sec)[ROISelectedId]
            color = (0, 0, 255) # hardcoded !!!
            opacity = view_control.getHighlightOpacity()
            drawROI(painter, dict_roi_coords_single, color, opacity)

# draw ROI pairs
def drawROIPairsOnlyDisplay(
        view_control: ViewControl, 
        painter: QPainter, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        ROISelectedId: int,
        app_key_pri: AppKeys,
        app_key_sec: AppKeys
        ) -> None:
    if view_control.show_roi_pair and app_key_sec is not None:
        roi_display_pri = control_manager.getSharedAttr(app_key_pri, "roi_display")
        roi_display_sec = control_manager.getSharedAttr(app_key_sec, "roi_display")
        try:
            table_control_pri = control_manager.table_controls[app_key_pri]
            table_control_sec = control_manager.table_controls[app_key_sec]
            roiId_pairs = table_control_pri.getMatchedROIPairs(table_control_sec)
            # all ROI pairs
            for roiId_pri, roiId_sec in roiId_pairs:
                coords_pri = data_manager.getDictROICoords(app_key_pri)[roiId_pri]["med"]
                if view_control.show_reg_im_roi:
                    coords_sec = data_manager.getDictROICoordsRegistered(app_key_sec)[roiId_sec]["med"]
                else:
                    coords_sec = data_manager.getDictROICoords(app_key_sec)[roiId_sec]["med"]
                # show only if both ROIs are displayed
                if roi_display_pri[roiId_pri] and roi_display_sec[roiId_sec] and roiId_pri != ROISelectedId:
                    drawROIPair(painter, coords_pri, coords_sec, view_control.getROIPairOpacity())
                elif roiId_pri == ROISelectedId:
                    coords_pri_selected, coords_sec_selected = coords_pri, coords_sec
        except (TypeError, KeyError):
            pass
        # selected ROI pair 
        try:
            drawROIPair(painter, coords_pri_selected, coords_sec_selected, view_control.getROIPairOpacity())
        except (NameError, UnboundLocalError):
            pass