from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt

def initializeDragRectangle(
        layer_roi_edit: QGraphicsPixmapItem,
        start_pos: QPointF,
        end_pos: QPointF,
        color: QColor,
        width: int
) -> None:
    """
    Initialize a rectangle in the ViewControl's layer_roi_edit.

    Parameters:
        layer_roi_edit (QGraphicsPixmapItem): The pixmap item for rectangle drawing.
        start_pos (QPointF): Starting position of the drag.
        end_pos (QPointF): Ending position of the drag.
        color (QColor): Color of the rectangle.
        width (int): Border width of the rectangle.
    """
    pixmap = layer_roi_edit.pixmap()
    painter = QPainter(pixmap)
    pen = QPen(color)
    pen.setWidth(width)
    painter.setPen(pen)

    rect = QRectF(start_pos, end_pos).normalized()
    painter.drawRect(rect)
    painter.end()

    layer_roi_edit.setPixmap(pixmap)


def updateDragRectangle(
        layer_roi_edit: QGraphicsPixmapItem,
        start_pos: QPointF,
        end_pos: QPointF,
        color: QColor,
        width: int
) -> None:
    """
    Update the rectangle during drag.

    Parameters:
        layer_roi_edit (QGraphicsPixmapItem): The pixmap item for rectangle drawing.
        start_pos (QPointF): Starting position of the drag.
        end_pos (QPointF): Current ending position of the drag.
        color (QColor): Color of the rectangle.
        width (int): Border width of the rectangle.
    """
    pixmap = layer_roi_edit.pixmap()
    pixmap.fill(Qt.transparent)  # Clear the previous rectangle
    painter = QPainter(pixmap)
    pen = QPen(color)
    pen.setWidth(width)
    painter.setPen(pen)

    rect = QRectF(start_pos, end_pos).normalized()
    painter.drawRect(rect)
    painter.end()

    layer_roi_edit.setPixmap(pixmap)


def highlightRectangle(
        layer_roi_edit: QGraphicsPixmapItem,
        rect_coords: QRectF,
        color: QColor,
        width: int
) -> None:
    """
    Highlight a specific rectangle.

    Parameters:
        layer_roi_edit (QGraphicsPixmapItem): The pixmap item for rectangle drawing.
        rect_coords (QRectF): Rectangle coordinates.
        color (QColor): Color of the rectangle.
        width (int): Border width of the rectangle.
    """
    pixmap = layer_roi_edit.pixmap()
    painter = QPainter(pixmap)
    pen = QPen(color)
    pen.setWidth(width)
    painter.setPen(pen)

    painter.drawRect(rect_coords)
    painter.end()

    layer_roi_edit.setPixmap(pixmap)

def clipRectangleRange(
        tiff_shape: Tuple[int, int, int, int, int],
        rect_range: List[float, float, float, float]
) -> List[int, int, int, int]:
    """
    Clip rectangle coordinates to ensure they fit within the TIFF image bounds.

    Parameters:
        tiff_shape (Tuple[int, int, int, int, int]): Dimensions of the TIFF image (width, height, _, depth, frames).
        rect_range (List[float, float, float, float]): Rectangle coordinates [x_start, x_end, y_start, y_end].

    Returns:
        List[int, int, int, int]: Clipped rectangle coordinates [x_start, x_end, y_start, y_end].
    """
    width, height, _, depth, frames = tiff_shape
    x_start, x_end, y_start, y_end = rect_range

    # Clip coordinates to the image boundaries
    x_start = max(0, min(x_start, width - 1))
    x_end = max(0, min(x_end, width - 1))
    y_start = max(0, min(y_start, height - 1))
    y_end = max(0, min(y_end, height - 1))

    # Ensure start <= end
    x_start, x_end = sorted((int(x_start), int(x_end)))
    y_start, y_end = sorted((int(y_start), int(y_end)))

    return [x_start, x_end, y_start, y_end]