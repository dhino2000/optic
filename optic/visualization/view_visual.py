from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from ..preprocessing.preprocessing_image import convertMonoImageToRGBImage

# q_view widget visualization
def updateView(q_scene, q_view, data_manager, key):
    bg_image_g = data_manager.getBGImage(key)
    bg_image = convertMonoImageToRGBImage(image_g=bg_image_g)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)