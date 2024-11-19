from __future__ import annotations
from ..type_definitions import *
from ..visualization.view_visual import updateViewFall, updateViewTiff, updateViewFallWithTracking
from ..visualization.view_visual_roi import findClosestROI, shouldSkipROI
from ..visualization.view_visual_rectangle import initializeDragRectangle, updateDragRectangle, clipRectangleRange
from ..visualization.info_visual import updateZPlaneDisplay, updateTPlaneDisplay
from ..gui.view_setup import setViewSize
from ..config.constants import BGImageTypeList, Extension
from PyQt5.QtCore import Qt
import random
import numpy as np

class ViewControl:
    def __init__(
            self, 
            app_key         : str, 
            q_view          : QGraphicsView, 
            q_scene         : QGraphicsScene, 
            data_manager    : DataManager, 
            widget_manager  : WidgetManager, 
            config_manager  : ConfigManager, 
            control_manager : ControlManager,
            app_key_sec     : str=None,
        ):
        self.app_key         = app_key
        self.app_key_sec     = app_key_sec
        self.q_view          = q_view
        self.q_scene         = q_scene
        self.data_manager    = data_manager
        self.widget_manager  = widget_manager
        self.config_manager  = config_manager
        self.control_manager = control_manager

        self.data_dtype:            str                         = "" # ".mat" or ".tif"
        self.im_dtype:              np.dtype                    = np.uint8
        self.image_sizes:           Tuple[int, int]             = ()
        self.bg_image_type:         str                         = BGImageTypeList.FALL[0]
        self.bg_contrast:           Dict[str, Dict[str, int]]   = {}
        self.bg_visibility:         Dict[str, bool]             = {} # show or hide background image
        for channel in config_manager.gui_defaults["CHANNELS"]:
            self.bg_contrast[channel] = {
                'min': config_manager.gui_defaults["VIEW_SETTINGS"]["DEFAULT_CONTRAST_MIN"],
                'max': config_manager.gui_defaults["VIEW_SETTINGS"]["DEFAULT_CONTRAST_MAX"]
            }
            self.bg_visibility[channel] = True
        # show or hide registration image
        self.show_reg_stack:        bool                        = True 
        self.show_reg_im_roi:       bool                        = True
        self.show_reg_im_bg:        bool                        = True

        self.show_roi_match:        bool                        = True
        self.show_roi_pair:         bool                        = True

        # for tiff view
        self.tiff_shape:            Tuple[int, int, int, int, int]  = ()
        self.plane_z:               int                             = 0
        self.plane_t:               int                             = 0
        self.rect:                  QGraphicsRectItem               = None
        self.rect_range:            List[int, int, int, int, int, int, int, int] = None
        self.rect_highlight:        QGraphicsRectItem               = None
        self.rect_highlight_range:  List[int, int, int, int, int, int, int, int] = None

        self.roi_colors:        Dict[int, Tuple[int, int, int]] = {}
        self.roi_opacity:       int                             = int(config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_ROI_OPACITY"])
        self.highlight_opacity: int                             = int(config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_HIGHLIGHT_OPACITY"])
        self.roi_pair_opacity:  int                             = 255

        # Key pushing state, Mouse dragging state
        self.dict_key_pushed:   Dict[str, bool]                 = {Qt.Key_Control: False, Qt.Key_Shift: False}
        self.is_dragging:       bool                            = False
        self.drag_pos_start:    Tuple[int, int]                 = (0, 0)

        self.setDataType()
        self.setImageSize()
        if self.data_dtype == Extension.MAT:
            self.initializeROIColors()
            self.setSharedAttr_ROISelected(roi_id=0)
        elif self.data_dtype == Extension.TIFF:
            self.setImageDataType()
            self.setTIFFShape()


    def updateView(self) -> None:
        if self.config_manager.current_app == "SUITE2P_ROI_CHECK":
            updateViewFall(self.q_scene, self.q_view, self, self.data_manager, self.control_manager, self.app_key)
        elif self.config_manager.current_app == "SUITE2P_ROI_TRACKING":
            updateViewFallWithTracking(self.q_scene, self.q_view, self, self.data_manager, self.control_manager, self.app_key, self.app_key_sec)
        elif self.config_manager.current_app == "TIFSTACK_EXPLORER":
            updateViewTiff(self.q_scene, self.q_view, self, self.data_manager, self.control_manager, self.app_key)
        

    """
    initialize Functions
    """
    def setDataType(self) -> None:
        self.data_dtype = self.data_manager.getDataType(self.app_key)

    def setImageDataType(self) -> None:
        self.im_dtype = self.data_manager.getDataTypeOfTiffStack(self.app_key)

    def setViewSize(self, use_self_size: bool=True) -> None:
        if use_self_size:
            width_min, height_min = self.getImageSize()
            setViewSize(self.q_view, width_min=width_min, height_min=height_min)

    def setTIFFShape(self) -> None:
        self.tiff_shape = (
            self.data_manager.getSizeOfX(self.app_key),
            self.data_manager.getSizeOfY(self.app_key),
            self.data_manager.getSizeOfC(self.app_key),
            self.data_manager.getSizeOfZ(self.app_key),
            self.data_manager.getSizeOfT(self.app_key)
        )

    def initializeROIColors(self):
        for roi_id in self.data_manager.getStat(self.app_key).keys():
            self.roi_colors[roi_id] = self.generateRandomColor()

    def generateRandomColor(self) -> Tuple[int, int, int]:
        return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    """
    get Functions
    """
    def getPlaneZ(self) -> int:
        return self.plane_z
    
    def getPlaneT(self) -> int:
        return self.plane_t
    
    def getRect(self) -> Optional[QGraphicsRectItem]:
        return self.rect
    
    def getRectRange(self) -> Optional[List[int, int, int, int, int, int, int, int]:]:
        return self.rect_range
    
    def getRectHighlight(self) -> Optional[QGraphicsRectItem]:
        return self.rect_highlight
    
    def getRectHighlightRange(self) -> Optional[List[int, int, int, int, int, int, int, int]]:
        return self.rect_highlight_range
    
    def getROIColor(self, roi_id: int) -> Tuple[int, int, int]:
        return self.roi_colors[roi_id]

    def getROIOpacity(self) -> int:
        return self.roi_opacity

    def getHighlightOpacity(self) -> int:
        return self.highlight_opacity
    
    def getROIPairOpacity(self) -> int:
        return self.roi_pair_opacity
    
    def getBackgroundImageType(self) -> str:
        return self.bg_image_type
    
    def getBackgroundContrastValue(self, channel: str, min_or_max: Literal['min', 'max']) -> Optional[int]:
        if channel in self.bg_contrast and min_or_max in ['min', 'max']:
            return self.bg_contrast[channel][min_or_max]
        return None
    
    def getBackgroundVisibility(self, channel: str) -> bool:
        return self.bg_visibility[channel]
    
    def getImageSize(self) -> Tuple[int, int]:
        return self.image_sizes
    
    def getShowRegStack(self) -> bool:
        return self.show_reg_stack
    def getShowRegImROI(self) -> bool:
        return self.show_reg_im_roi
    def getShowRegImBG(self) -> bool:
        return self.show_reg_im_bg
    def getShowROIMatch(self) -> bool:
        return self.show_roi_match
    def getShowROIPair(self) -> bool:
        return self.show_roi_pair
    
    """
    set Functions
    """
    def setPlaneZ(self, plane_z: int) -> None:
        self.plane_z = plane_z
        updateZPlaneDisplay(self.widget_manager, self.app_key, plane_z)

    def setPlaneT(self, plane_t: int) -> None:
        self.plane_t = plane_t
        updateTPlaneDisplay(self.widget_manager, self.app_key, plane_t)

    def setRect(self, rect: Optional[QGraphicsRectItem]) -> None:
        self.rect = rect

    def setRectRange(self, rect_range: List[int, int, int, int, int, int, int, int]) -> None:
        self.rect_range = rect_range

    def setRectHighlight(self, rect_highlight: Optional[QGraphicsRectItem]) -> None:
        self.rect_highlight = rect_highlight

    def setRectHighlightRange(self, rect_highlight_range: List[int, int, int, int, int, int, int, int]) -> None:
        self.rect_highlight_range = rect_highlight_range

    def setROIOpacity(self, opacity: int) -> None:
        self.roi_opacity = opacity

    def setHighlightOpacity(self, opacity: int) -> None:
        self.highlight_opacity = opacity

    def setROIPairOpacity(self, opacity: int) -> None:
        self.roi_pair_opacity = opacity

    def setBackgroundImageType(self, bg_type: str) -> None:
        self.bg_image_type = bg_type

    def setBackgroundContrastValue(self, channel: str, min_or_max: Literal['min', 'max'], value: int) -> None:
        if channel in self.bg_contrast and min_or_max in ['min', 'max']:
            self.bg_contrast[channel][min_or_max] = value

    def setBackgroundVisibility(self, channel: str, is_visible: bool) -> None:
        if channel in self.bg_visibility:
            self.bg_visibility[channel] = is_visible

    def setImageSize(self) -> None:
        self.image_sizes = self.data_manager.getImageSize(self.app_key)

    def setShowRegStack(self, show_reg: bool) -> None:
        self.show_reg_stack = show_reg
    def setShowRegImROI(self, show_reg: bool) -> None:
        self.show_reg_im_roi = show_reg
    def setShowRegImBG(self, show_reg: bool) -> None:
        self.show_reg_im_bg = show_reg
    def setShowROIMatch(self, show_match: bool) -> None:
        self.show_roi_match = show_match
    def setShowROIPair(self, show_pair: bool) -> None:
        self.show_roi_pair = show_pair

    """
    shared_attr Functions
    """
    def setSharedAttr_ROISelected(self, roi_id: int) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', roi_id)

    def getSharedAttr_ROISelected(self):
        return self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')
    
    """
    event Functions
    """
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in self.dict_key_pushed:
            self.dict_key_pushed[event.key()] = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() in self.dict_key_pushed:
            self.dict_key_pushed[event.key()] = False
            if self.is_dragging:
                self.cancelDraggingWithCtrlKey()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if self.dict_key_pushed[Qt.Key_Control]:
                self.startDraggingWithCtrlKey(event)
            else:
                scene_pos = self.q_view.mapToScene(event.pos())
                self.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()))

    def mousePressEventWithTracking(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            scene_pos = self.q_view.mapToScene(event.pos())
            self.getROIwithClick(int(scene_pos.x()), int(scene_pos.y()), reg=self.show_reg_im_roi)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_dragging and self.dict_key_pushed[Qt.Key_Control]:
            self.updateDraggingWithCtrlKey(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.is_dragging:
            if self.dict_key_pushed[Qt.Key_Control]:
                self.finishDraggingWithCtrlKey(event)
            else:
                self.cancelDraggingWithCtrlKey()
    
    def startDraggingWithCtrlKey(self, event: QMouseEvent) -> None:
        self.drag_start_pos = self.q_view.mapToScene(event.pos())
        self.is_dragging = True
        self.rect = initializeDragRectangle(self.q_scene, self.drag_start_pos, self.drag_start_pos)

    def updateDraggingWithCtrlKey(self, event: QMouseEvent) -> None:
        current_pos = self.q_view.mapToScene(event.pos())
        updateDragRectangle(self.rect, self.drag_start_pos, current_pos)

    def finishDraggingWithCtrlKey(self, event: QMouseEvent) -> None:
        self.is_dragging = False
        end_pos = self.q_view.mapToScene(event.pos())
        updateDragRectangle(self.rect, self.drag_start_pos, end_pos)
        final_rect = self.rect.rect()
        rect_range = self.getRectRangeFromQRectF(final_rect)
        self.setRectRange(clipRectangleRange(self.tiff_shape, rect_range))

    def cancelDraggingWithCtrlKey(self) -> None:
        if self.rect:
            self.q_scene.removeItem(self.rect)
        self.is_dragging = False
        self.rect = None

    def getROIwithClick(self, x:int, y:int, reg=False) -> None:
        if reg:
            dict_roi_coords = self.data_manager.getDictROICoordsRegistered(self.app_key)
        else:
            dict_roi_coords = self.data_manager.getDictROICoords(self.app_key)
        dict_roi_med = {roi_id: dict_roi_coords[roi_id]["med"] for roi_id in dict_roi_coords.keys()}
        skip_checkboxes = [checkbox for key, checkbox in self.widget_manager.dict_checkbox.items() if key.startswith(f"{self.app_key}_skip_choose_")]
        dict_roi_skip = {roi_id: shouldSkipROI(roi_id, 
                                               self.config_manager.getTableColumns(self.app_key).getColumns(),
                                               self.widget_manager.dict_table[self.app_key],
                                               skip_checkboxes) 
                        for roi_id in dict_roi_med.keys()}
        closest_roi_id = findClosestROI(x, y, dict_roi_med, dict_roi_skip)
        if closest_roi_id is not None:
            self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', closest_roi_id)
            self.updateView()

    def getRectRangeFromQRectF(self, rect: QRectF) -> List[int, int, int, int, int, int, int, int]:
        x_start = int(rect.left())
        x_end = int(rect.right())
        y_start = int(rect.top())
        y_end = int(rect.bottom())
        z_start = self.getPlaneZ()
        z_end = z_start
        t_start = self.getPlaneT()
        t_end = t_start
        return [x_start, x_end, y_start, y_end, z_start, z_end, t_start, t_end]