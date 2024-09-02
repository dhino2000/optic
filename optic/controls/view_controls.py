from ..visualization.view_visual import updateView
import random

class ViewControls:
    def __init__(self, key_app, q_view, q_scene, data_manager, widget_manager, config_manager):
        """
        Initializes the ViewControls object.

        Args:
            key_app (str): The key for the application.
            q_view (QGraphicsView): The QGraphicsView object.
            q_scene (QGraphicsScene): The QGraphicsScene object.
            data_manager (DataManager): The DataManager object.
            widget_manager (WidgetManager): The WidgetManager object.
            config_manager (ConfigManager): The ConfigManager object.
        """
        # Rest of the code...
        self.key_app = key_app
        self.q_view = q_view
        self.q_scene = q_scene
        self.data_manager = data_manager
        self.widget_manager = widget_manager
        self.config_manager = config_manager
        self.last_click_position = None
        self.roi_colors = {}
        self.roi_opacity = config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_ROI_OPACITY"]
        self.highlight_opacity = config_manager.gui_defaults["ROI_VISUAL_SETTINGS"]["DEFAULT_HIGHLIGHT_OPACITY"]
        self.roi_display = {}
        self.initializeROIColors()
        self.initializeROIDisplay()

    def updateView(self):
        updateView(self, self.q_scene, self.q_view, self.data_manager, self.key_app)

    def initializeROIColors(self):
        for roi_id in self.data_manager.dict_Fall[self.key_app]["stat"].keys():
            self.roi_colors[roi_id] = self.generateRandomColor()

    def initializeROIDisplay(self):
        for roi_id in self.data_manager.dict_Fall[self.key_app]["stat"].keys():
            self.roi_display[roi_id] = True

    def generateRandomColor(self):
        return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    def getROIColor(self, roi_id):
        return self.roi_colors[roi_id]

    def getROIOpacity(self):
        return self.roi_opacity

    def getHighlightOpacity(self):
        return self.highlight_opacity
    
    def getROIDisplay(self, roi_id):
        return self.roi_display[roi_id]

    def setROIOpacity(self, opacity):
        self.roi_opacity = opacity

    def setHighlightOpacity(self, opacity):
        self.highlight_opacity = opacity

def onBGImageTypeChanged(data_manager, key_im_bg_current_type, bg_image_type):
    data_manager.setBGImageCurrentType(key_im_bg_current_type, bg_image_type)

