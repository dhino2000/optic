from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter
from ..preprocessing.preprocessing_roi import getROIContour
from ..config.constants import PenColors, PenWidth
import numpy as np

# draw all ROIs
def drawAllROIs(
        view_control: ViewControl, 
        pixmap: QPixmap, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys
        ) -> None:
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(app_key, "roi_display")
    ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    
    dict_roi_coords = data_manager.getDictROICoords(app_key)
    for roiId, dict_roi_coords_single in dict_roi_coords.items():
        if roi_display[roiId] and roiId != ROISelectedId:
            color = view_control.getROIColor(roiId)
            opacity = view_control.getROIOpacity()
            drawROI(painter, dict_roi_coords_single, color, opacity)
    
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

# draw all ROIs and contour of selected ROI
def drawAllROIsWithTracking(
        view_control: ViewControl, 
        pixmap: QPixmap, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key_pri: AppKeys,
        app_key_sec: AppKeys,
        ) -> None:
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
    
    highlightROISelectedWithTracking(view_control, painter, data_manager, control_manager, app_key_pri)
    # draw contour of selected ROI of "sec"
    if view_control.show_roi_match:
        try:
            roiId_match = control_manager.getSharedAttr(app_key_pri, "roi_match_id")
            view_control_sec = control_manager.view_controls[app_key_sec]
            if view_control_sec.show_reg_im_roi:
                dict_roi_coords_sec = data_manager.getDictROICoordsRegistered(app_key_sec)
            else:
                dict_roi_coords_sec = data_manager.getDictROICoords(app_key_sec)
            dict_roi_coords_sec_single = dict_roi_coords_sec[roiId_match]
            color = view_control_sec.getROIColor(roiId_match)
            opacity = view_control_sec.getROIOpacity()
            drawROIContour(painter, dict_roi_coords_sec_single, color, opacity)
        except KeyError:
            pass

    # draw ROI pairs
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

    painter.end()

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
def drawROIPair(
        painter: QPainter,
        coords_pri: Tuple[int, int],
        coords_sec: Tuple[int, int],
        opacity: int,
) -> None:
    x_pri, y_pri = coords_pri
    x_sec, y_sec = coords_sec
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


# highlight selected ROI with tracking
def highlightROISelectedWithTracking(
        view_control: ViewControl, 
        painter: QPainter, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys
        ) -> None:
    ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    if ROISelectedId is not None:
        if view_control.show_reg_im_roi:
            dict_roi_coords_single = data_manager.getDictROICoordsRegistered(app_key)[ROISelectedId]
        else:
            dict_roi_coords_single = data_manager.getDictROICoords(app_key)[ROISelectedId]
        xpix, ypix = dict_roi_coords_single["xpix"], dict_roi_coords_single["ypix"]
        color = view_control.getROIColor(ROISelectedId)
        opacity = view_control.getHighlightOpacity()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))

# find Closest ROI to click position
def findClosestROI(
        x: int, 
        y: int, 
        dict_roi_med: dict, 
        skip_roi: dict = None
        ) -> Optional[int]:
    if not dict_roi_med:
        return None
    
    min_distance = float('inf')
    closest_roi_id = None

    for roi_id, med in dict_roi_med.items():
        if skip_roi and skip_roi.get(roi_id, False):
            continue
        distance = np.sqrt((x - med[0])**2 + (y - med[1])**2)
        if distance < min_distance:
            min_distance = distance
            closest_roi_id = roi_id

    return closest_roi_id

# Skip ROIs with "Skip" checkbox checked
def shouldSkipROI(
        roi_id: int, 
        table_columns: dict, 
        q_table: QTableWidget, 
        skip_checkboxes: List[QCheckBox]
        ) -> bool:
    for checkbox in skip_checkboxes:
        if checkbox.isChecked():
            celltype = checkbox.text().replace("Skip ", "").replace(" ROI", "")
            for col_name, col_info in table_columns.items():
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