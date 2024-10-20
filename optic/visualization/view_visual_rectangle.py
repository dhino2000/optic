from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor

# draw rectangle
def drawRectangle(
        q_scene: QGraphicsScene,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
        color: QColor = Qt.yellow,
        width: int = 2
        ) -> QGraphicsRectItem:
    pen = QPen(color)
    pen.setWidth(width)
    rect_item = q_scene.addRect(x_min, y_min, x_max - x_min, y_max - y_min, pen)
    return rect_item

# draw rectangle within range of Z,T
def drawRectangleIfInRange(
        q_scene: QGraphicsScene,
        current_z: int,
        current_t: int,
        x_min: int,
        x_max: int,
        y_min: int,
        y_max: int,
        z_min: int,
        z_max: int,
        t_min: int,
        t_max: int,
        existing_rect: Optional[QGraphicsRectItem] = None
) -> Optional[QGraphicsRectItem]:
    if (z_min <= current_z <= z_max) and (t_min <= current_t <= t_max):
        if existing_rect is not None and existing_rect in q_scene.items():
            q_scene.removeItem(existing_rect)
        return drawRectangle(q_scene, x_min, x_max, y_min, y_max)
    elif existing_rect is not None and existing_rect in q_scene.items():
        q_scene.removeItem(existing_rect)
    return None