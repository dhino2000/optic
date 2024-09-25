from __future__ import annotations
from ..type_definitions import *
from ..visualization.view_visual import updateView, findClosestROI, shouldSkipROI
from ..gui.view_setup import setViewSize
from ..config.constants import BGImageTypeList
import random
import numpy as np


class ViewControl:
    def __init__(
            self, 
            key_app         : str, 
            q_view          : QGraphicsView, 
            q_scene         : QGraphicsScene, 
            data_manager    : DataManager, 
            widget_manager  : WidgetManager, 
            config_manager  : ConfigManager, 
            control_manager : ControlManager,
        ):
        # Rest of the code...
        self.key_app         = key_app
        self.q_view          = q_view
        self.q_scene         = q_scene
        self.data_manager    = data_manager
        self.widget_manager  = widget_manager
        self.config_manager  = config_manager
        self.control_manager = control_manager

        self.last_click_position:   Tuple[int, int]             = ()
        self.image_sizes:           Tuple[int, int]             = ()
        self.bg_image_type:         str                         = BGImageTypeList.FALL[0]
        self.bg_contrast:           Dict[str, Dict[str, int]]   = {}
        self.bg_visibility:         Dict[str, bool]             = {}
        for channel in config_manager.gui_defaults["CHANNELS"]:
            self.bg_contrast[channel] = {
                'min': config_manager.gui_defaults["VIEW_SETTINGS"]["DEFAULT_CONTRAST_MIN"],
                'max': config_manager.gui_defaults["VIEW_SETTINGS"]["DEFAULT_CONTRAST_MAX"]
            }
            self.bg_visibility[channel] = True

        self.roi_colors:        Dict[int, Tuple[int, int, int]] = {}
        self.roi_opacity:       int                             = int(config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_ROI_OPACITY"])
        self.highlight_opacity: int                             = int(config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_HIGHLIGHT_OPACITY"])

        self.initializeROIColors()
        self.setImageSize()
        self.setSharedAttr_ROISelected(roi_id=0)


    def updateView(self):
        updateView(self.q_scene, self.q_view, self, self.data_manager, self.control_manager, self.key_app)

    """
    initialize Functions
    """
    def setViewSize(self, use_self_size=True):
        if use_self_size:
            width_min, height_min = self.getImageSize()
            setViewSize(self.q_view, width_min=width_min, height_min=height_min)

    def initializeROIColors(self):
        for roi_id in self.data_manager.dict_Fall[self.key_app]["stat"].keys():
            self.roi_colors[roi_id] = self.generateRandomColor()

    def generateRandomColor(self):
        return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    """
    get Functions
    """
    def getROIColor(self, roi_id):
        return self.roi_colors[roi_id]

    def getROIOpacity(self):
        return self.roi_opacity

    def getHighlightOpacity(self):
        return self.highlight_opacity
    
    def getBackgroundImageType(self) -> str:
        return self.bg_image_type
    
    def getBackgroundContrastValue(self, channel, min_or_max):
        if channel in self.bg_contrast and min_or_max in ['min', 'max']:
            return self.bg_contrast[channel][min_or_max]
        return None
    
    def getBackgroundVisibility(self, channel):
        return self.bg_visibility[channel]
    
    def getImageSize(self):
        return self.image_sizes
    
    """
    set Functions
    """
    def setROIOpacity(self, opacity):
        self.roi_opacity = opacity

    def setHighlightOpacity(self, opacity):
        self.highlight_opacity = opacity

    def setBackgroundImageType(self, bg_type: str):
        self.bg_image_type = bg_type

    def setBackgroundContrastValue(self, channel, min_or_max, value):
        if channel in self.bg_contrast and min_or_max in ['min', 'max']:
            self.bg_contrast[channel][min_or_max] = value

    def setBackgroundVisibility(self, channel, is_visible):
        if channel in self.bg_visibility:
            self.bg_visibility[channel] = is_visible

    def setImageSize(self):
        self.image_sizes = self.data_manager.getImageSize(self.key_app)

    """
    shared_attr Functions
    """
    def setSharedAttr_ROISelected(self, roi_id):
        self.control_manager.setSharedAttr(self.key_app, 'roi_selected_id', roi_id)

    def getSharedAttr_ROISelected(self):
        return self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')
    
    """
    event Functions
    """
    def mousePressEvent(self, x:int, y:int):
        dict_Fall_stat = self.data_manager.dict_Fall[self.key_app]["stat"]
        dict_roi_med = {roi_id: dict_Fall_stat[roi_id]["med"] for roi_id in dict_Fall_stat.keys()}
        skip_checkboxes = [checkbox for key, checkbox in self.widget_manager.dict_checkbox.items() if key.startswith(f"{self.key_app}_skip_choose_")]
        dict_roi_skip = {roi_id: shouldSkipROI(roi_id, 
                                               self.config_manager.getTableColumns(self.key_app).getColumns(),
                                               self.widget_manager.dict_table[self.key_app],
                                               skip_checkboxes) 
                        for roi_id in dict_roi_med.keys()}
        closest_roi_id = findClosestROI(x, y, dict_roi_med, dict_roi_skip)
        if closest_roi_id is not None:
            self.control_manager.setSharedAttr(self.key_app, 'roi_selected_id', closest_roi_id)
            self.updateView()