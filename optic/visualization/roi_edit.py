from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt

# ROI editing functions

# Draw ROI
def editROIdraw(
        points: set[Tuple[int, int]], 
        x: int, 
        y: int, 
        radius: int = 5, 
        x_min: int = 0,
        x_max: int = 511,
        y_min: int = 0,
        y_max: int = 511) -> None:
    """
    Adds a point to the ROI points list with a specified radius.

    Args:
        points (Set[Tuple[int, int]]): Set of current ROI points.
        x (int): X-coordinate to add.
        y (int): Y-coordinate to add.
        radius (int): Radius of the point to add.
    """
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx**2 + dy**2 <= radius**2:  # 円形にする
                if x + dx < x_min:
                    dx = x_min - x
                if x + dx > x_max:
                    dx = x_max - x
                if y + dy < y_min:
                    dy = y_min - y
                if y + dy > y_max:
                    dy = y_max - y
                points.add((x + dx, y + dy))

# Erase ROI
def editROIerase(points: set[Tuple[int, int]], x: int, y: int, radius: int = 5) -> None:
    """
    Removes points within a radius from the specified position.

    Args:
        points (Set[Tuple[int, int]]): Set of current ROI points.
        x (int): X-coordinate of the erase position.
        y (int): Y-coordinate of the erase position.
        radius (int): Radius within which points are erased.
    """
    to_remove = {
        point for point in points 
        if (point[0] - x)**2 + (point[1] - y)**2 <= radius**2
    }
    points.difference_update(to_remove)

def updateROIEditLayer(
        view_control: ViewControl,
        layer: QGraphicsPixmapItem, 
        points: set[Tuple[int, int]], 
        color: Tuple[int, int, int] = (255, 0, 0), 
        opacity: int = 150
    ) -> None:
    """
    Updates the pixmap of a specified layer with the current ROI points.

    Args:
        layer (QGraphicsPixmapItem): The layer to update.
        points (set[Tuple[int, int]]): Set of ROI points to draw.
        color (Tuple[int, int, int]): Color of the ROI.
        opacity (int): Opacity of the ROI.
    """
    width, height = view_control.getImageSize()
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent) 
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor(*color, opacity)))
    for point in points:
        painter.drawPoint(*point)
    painter.end()
    layer.setPixmap(pixmap)