from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem

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

# clip rectangle within image size
def clipRectangleRange(
        tiff_shape: Tuple[int, int, int, int, int], 
        rect_range: List[int, int, int, int, int, int, int, int]
        ) -> List[int, int, int, int, int, int, int, int]:
    width, height, _, depth, frames = tiff_shape
    x_start, x_end, y_start, y_end, z_start, z_end, t_start, t_end = rect_range

    # Clip values to valid ranges
    x_start = max(0, min(x_start, width - 1))
    x_end = max(x_start, min(x_end, width - 1))
    y_start = max(0, min(y_start, height - 1))
    y_end = max(y_start, min(y_end, height - 1))
    z_start = max(0, min(z_start, depth - 1))
    z_end = max(z_start, min(z_end, depth - 1))
    t_start = max(0, min(t_start, frames - 1))
    t_end = max(t_start, min(t_end, frames - 1))

    return [x_start, x_end, y_start, y_end, z_start, z_end, t_start, t_end]

# draw rectangle with mouse drag
def initializeDragRectangle(
        q_scene: QGraphicsScene,
        start_pos: QPointF,
        end_pos: QPointF,
        color: QColor = Qt.yellow,
        width: int = 2
) -> QGraphicsRectItem:
    pen = QPen(color)
    pen.setWidth(width)

    rect = QRectF(start_pos, end_pos).normalized()
    for item in q_scene.items():
        if isinstance(item, QGraphicsRectItem):
            q_scene.removeItem(item)
    rect_item = q_scene.addRect(rect, pen)
    return rect_item

def updateDragRectangle(
        rect_item: QGraphicsRectItem,
        start_pos: QPointF,
        end_pos: QPointF
) -> None:
    rect = QRectF(start_pos, end_pos).normalized()
    rect_item.setRect(rect)