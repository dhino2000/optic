from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from ..preprocessing.preprocessing_image import convertMonoImageToRGBImage

class ViewControls:
    def __init__(self, q_view, q_scene, data_manager):
        self.q_view = q_view
        self.q_scene = q_scene
        self.data_manager = data_manager
        self.last_click_position = None

    def updateView(self, key):
        bg_image_g = self.data_manager.getBGImage(key)
        bg_image = convertMonoImageToRGBImage(image_g=bg_image_g)

        height, width = bg_image.shape[:2]
        qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        self.q_scene.clear()
        self.q_scene.addPixmap(pixmap)
        self.q_view.setScene(self.q_scene)
        self.q_view.fitInView(self.q_scene.sceneRect(), Qt.KeepAspectRatio)


def onBGImageTypeChanged(data_manager, key_im_bg_current_type, bg_image_type):
    data_manager.setBGImageCurrentType(key_im_bg_current_type, bg_image_type)

