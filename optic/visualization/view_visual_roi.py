from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter
from ..preprocessing.preprocessing_roi import getROIContour
import numpy as np

# draw all ROIs
def drawAllROIs(
        view_control: ViewControl, 
        pixmap: QPixmap, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: str
        ) -> None:
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(app_key, "roi_display")
    
    dict_roi_coords = data_manager.getDictROICoords(app_key)
    for roiId, dict_roi_coords_single in dict_roi_coords.items():
        if roi_display[roiId]:
            drawROI(view_control, painter, dict_roi_coords_single, roiId)
    
    highlightROISelected(view_control, painter, data_manager, control_manager, app_key)
    painter.end()

# draw all ROIs and contour of selected ROI
def drawAllROIsWithTracking(
        view_control: ViewControl, 
        pixmap: QPixmap, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key_pri: str,
        app_key_sec: str,
        ) -> None:
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(app_key_pri, "roi_display")

    if view_control.show_reg_im_roi:
        dict_roi_coords = data_manager.getDictROICoordsRegistered(app_key_pri)
    else:
        dict_roi_coords = data_manager.getDictROICoords(app_key_pri)

    for roiId, dict_roi_coords_single in dict_roi_coords.items():
        if roi_display[roiId]:
            drawROI(view_control, painter, dict_roi_coords_single, roiId)
    
    highlightROISelected(view_control, painter, data_manager, control_manager, app_key_pri)
    # draw contour of selected ROI of "sec"
    try:
        roiId_match = control_manager.getSharedAttr(app_key_pri, "roi_match_id")
        view_control_sec = control_manager.view_controls[app_key_sec]
        dict_roi_coords_single = dict_roi_coords[roiId_match]
        drawROIContour(view_control_sec, painter, dict_roi_coords_single, roiId_match)
    except KeyError:
        pass

    painter.end()

# draw single ROI
def drawROI(
        view_control: ViewControl, 
        painter: QPainter, 
        dict_roi_coords_single: Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]],
        roiId: int
        ) -> None:
    xpix, ypix = dict_roi_coords_single["xpix"], dict_roi_coords_single["ypix"]
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

# draw single ROI contour
def drawROIContour(
        view_control: ViewControl, 
        painter: QPainter, 
        dict_roi_coords_single: Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]],
        roiId: int
        ) -> None:
    xpix, ypix = dict_roi_coords_single["xpix"], dict_roi_coords_single["ypix"]
    xpix_contour, ypix_contour = getROIContour(xpix, ypix)
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix_contour, ypix_contour):
        painter.drawPoint(int(x), int(y))

def highlightROISelected(
        view_control: ViewControl, 
        painter: QPainter, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: str
        ) -> None:
    ROISelectedId = control_manager.getSharedAttr(app_key, "roi_selected_id")
    if ROISelectedId is not None:
        roiStat = data_manager.getStat(app_key)[ROISelectedId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
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