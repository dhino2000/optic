from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
from ..preprocessing.preprocessing_image import convertMonoImageToRGBImage

# q_view widget visualization
def updateView(view_control, q_scene, q_view, data_manager, key):
    bg_image_g = data_manager.getBGImage(key)
    bg_image = convertMonoImageToRGBImage(image_g=bg_image_g)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    drawAllROIs(view_control, pixmap, data_manager, key)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

def drawAllROIs(view_control, pixmap, data_manager, key):
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    for roiId, roiStat in data_manager.dict_Fall[key]["stat"].items():
        if shouldDisplayROI(view_control, data_manager, key, roiId):
            drawROI(view_control, painter, roiStat, roiId, key)
    
    # highlightSelectedROI(painter, dataManager, widgetManager, key)
    painter.end()

def drawROI(view_control, painter, roiStat, roiId, key):
    xpix, ypix = roiStat["xpix"], roiStat["ypix"]
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

def highlightSelectedROI(view_control, painter, data_manager, key):
    selectedRoiId = data_manager.getSelectedROI(key)
    if selectedRoiId is not None:
        roiStat = data_manager.dict_Fall[key]["stat"][selectedRoiId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        color = view_control.getROIColor(selectedRoiId)
        opacity = view_control.getHighlightOpacity()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))

def shouldDisplayROI(view_control, data_manager, key, roiId):
    # This is a placeholder. You should implement the logic to determine if an ROI should be displayed.
    return True