class ViewControls:
    def __init__(self, q_view):
        self.q_view = q_view
        self.last_click_position = None


def onBGImageTypeChanged(data_manager, key_im_bg_current_type, bg_image_type):
    data_manager.setBGImageCurrentType(key_im_bg_current_type, bg_image_type)

