from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import random
import numpy as np
from ..preprocessing.preprocessing_image import convertMonoImageToRGBImage, convertImageDtypeToINT

# q_view widget visualization
def updateView(q_scene, q_view, data_manager, key):
    bg_image_g = data_manager.getBGImage(key)
    bg_image = convertMonoImageToRGBImage(image_g=bg_image_g)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    # drawAllROIs(pixmap, dataManager, widgetManager, key)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

def drawAllROIs(pixmap, dataManager, widgetManager, key):
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    for roiId, roiStat in dataManager.dict_Fall[key]["stat"].items():
        if shouldDisplayROI(dataManager, widgetManager, key, roiId):
            drawROI(painter, roiStat, roiId, widgetManager, key)
    
    highlightSelectedROI(painter, dataManager, widgetManager, key)
    painter.end()

def drawROI(painter, roiStat, roiId, widgetManager, key):
    xpix, ypix = roiStat["xpix"], roiStat["ypix"]
    color = getROIColor(roiId)
    opacity = widgetManager.dict_slider[f"{key}_opacity_allroi"].value()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

def highlightSelectedROI(painter, dataManager, widgetManager, key):
    selectedRoiId = dataManager.getSelectedROI(key)
    if selectedRoiId is not None:
        roiStat = dataManager.dict_Fall[key]["stat"][selectedRoiId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        color = getROIColor(selectedRoiId)
        opacity = widgetManager.dict_slider[f"{key}_opacity_selectedroi"].value()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))

def getROIColor(roiId):
    # This is a placeholder. You should implement a proper color assignment method.
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def shouldDisplayROI(dataManager, widgetManager, key, roiId):
    # This is a placeholder. You should implement the logic to determine if an ROI should be displayed.
    return True