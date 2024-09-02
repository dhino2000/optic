from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from ..preprocessing.preprocessing_image import convertMonoImageToRGBImage

# q_view widget visualization
def updateView(view_control, q_scene, q_view, data_manager, key_app):
    bg_image_g = data_manager.getBGImage(key_app)
    bg_image_r = data_manager.getBGChan2Image(key_app)

    bg_image = convertMonoImageToRGBImage(image_g=bg_image_g, image_r=bg_image_r)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    drawAllROIs(view_control, pixmap, data_manager, key_app)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

def drawAllROIs(view_control, pixmap, data_manager, key_app):
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    for roiId, roiStat in data_manager.dict_Fall[key_app]["stat"].items():
        if view_control.getROIDisplay(roiId):
            drawROI(view_control, painter, roiStat, roiId)
    
    highlightSelectedROI(view_control, painter, data_manager, key_app)
    painter.end()

def drawROI(view_control, painter, roiStat, roiId):
    xpix, ypix = roiStat["xpix"], roiStat["ypix"]
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

def highlightSelectedROI(view_control, painter, data_manager, key_app):
    selectedRoiId = data_manager.getSelectedROI(key_app)
    if selectedRoiId is not None:
        roiStat = data_manager.dict_Fall[key_app]["stat"][selectedRoiId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        color = view_control.getROIColor(selectedRoiId)
        opacity = view_control.getHighlightOpacity()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))

def adjustChannelContrast(self, image, min_val, max_val, dtype=np.uint8):
    return np.clip(((image - min_val) / (max_val - min_val) * 255), 0, 255).astype(dtype)
