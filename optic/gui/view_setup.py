from __future__ import annotations
from ..type_definitions import *

# Floor that the View widget cannot shrink below. Kept small so the window can be freely
# resized down — AutoFitGraphicsView rescales the image to whichever edge is shorter via
# fitInView(scene_rect, Qt.KeepAspectRatio), so aspect ratio is preserved at any view size.
MIN_VIEW_WIDTH_PX  = 200
MIN_VIEW_HEIGHT_PX = 200


def setViewSize(q_view: QGraphicsView, width_min: int=0, width_max: int=0, height_min: int=0, height_max: int=0) -> None:
    if width_min:
        q_view.setMinimumWidth(width_min)
    if width_max:
        q_view.setMaximumWidth(width_max)
    if height_min:
        q_view.setMinimumHeight(height_min)
    if height_max:
        q_view.setMaximumHeight(height_max)


# View's minimum size. image_size is intentionally unused now: image scaling is handled by
# AutoFitGraphicsView on every resize. The fixed floor keeps the view from collapsing to zero
# and keeps signature stable for existing callers.
def resolveViewMinSize(
    image_size: Tuple[int, int],
    n_panels: int=1,
) -> Tuple[int, int]:
    return (MIN_VIEW_WIDTH_PX, MIN_VIEW_HEIGHT_PX)
