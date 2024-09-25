from __future__ import annotations
from ..type_definitions import *

def setViewSize(q_view: QGraphicsView, width_min: int=0, width_max: int=0, height_min: int=0, height_max: int=0) -> None:
    if width_min:
        q_view.setMinimumWidth(width_min)
    if width_max:
        q_view.setMaximumWidth(width_max)
    if height_min:
        q_view.setMinimumHeight(height_min)
    if height_max:
        q_view.setMaximumHeight(height_max)