from ..visualization.view_visual import updateView

class ViewControls:
    def __init__(self, q_view, q_scene, data_manager):
        self.q_view = q_view
        self.q_scene = q_scene
        self.data_manager = data_manager
        self.last_click_position = None

    def updateView(self, key):
        updateView(self.q_scene, self.q_view, self.data_manager, key)

def onBGImageTypeChanged(data_manager, key_im_bg_current_type, bg_image_type):
    data_manager.setBGImageCurrentType(key_im_bg_current_type, bg_image_type)

