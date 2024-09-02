from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from typing import Optional
from ..config.constants import ChannelKeys

# q_view widget visualization
def updateView(view_control, q_scene, q_view, data_manager, key_app):
    bg_image_chan1 = None
    bg_image_chan2 = None

    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getBGImage(key_app),
            min_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getBGChan2Image(key_app),
            min_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )

    (width, height) = view_control.getImageSize()
    bg_image = convertMonoImageToRGBImage(image_g=bg_image_chan1, image_r=bg_image_chan2)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    drawAllROIs(view_control, pixmap, data_manager, key_app)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# 白黒画像からカラー画像作成
def convertMonoImageToRGBImage(image_r: Optional[np.ndarray] = None, 
                               image_g: Optional[np.ndarray] = None, 
                               image_b: Optional[np.ndarray] = None,
                               width = 512, 
                               height = 512) -> np.ndarray:
    """
    1~3チャンネルの画像を組み合わせてRGB画像を生成する。

    Args:
    image_r (np.ndarray, optional): 赤チャンネルの画像
    image_g (np.ndarray, optional): 緑チャンネルの画像
    image_b (np.ndarray, optional): 青チャンネルの画像

    Returns:
    np.ndarray: 生成されたRGB画像

    Raises:
    ValueError: 提供された画像のサイズが異なる場合
    """
    # 非Noneの画像のリストを作成
    images = [img for img in [image_r, image_g, image_b] if img is not None]
    if not images:
        # 全てのチャンネルがNoneの場合、デフォルトサイズの黒い画像を返す
        return np.zeros((height, width, 3), dtype=np.uint8)
    # すべての画像のサイズが同じであることを確認
    if len(set(img.shape for img in images)) != 1:
        raise ValueError("All provided images must have the same dimensions")
    # 画像サイズを取得
    height, width = images[0].shape[:2]
    # RGB画像を初期化
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    # 各チャンネルを処理
    for i, img in enumerate([image_r, image_g, image_b]):
        if img is not None:
            rgb_image[:, :, i] = img

    return rgb_image

def adjustChannelContrast(image, min_val, max_val, dtype=np.uint8):
    try:
        epsilon = 1e-5 # Zero division prevention
        # 画像の正規化
        image_min, image_max = image.min(), image.max()
        image_normalized = (image - image_min) / (image_max - image_min + epsilon)

        # コントラスト調整
        min_val, max_val = min_val / 255, max_val / 255  # 0-1の範囲に正規化
        image_contrasted = np.clip((image_normalized - min_val) / (max_val - min_val + epsilon), 0, 1)
        image_adjusted = (image_contrasted * 255).astype(dtype)
    except (TypeError, AttributeError) as e:
        image_adjusted = None
    return image_adjusted

def drawAllROIs(view_control, pixmap, data_manager, key_app):
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    for roiId, roiStat in data_manager.dict_Fall[key_app]["stat"].items():
        if view_control.getROIDisplay(roiId):
            drawROI(view_control, painter, roiStat, roiId)
    
    highlightSelectedROI(view_control, painter, data_manager, key_app)
    painter.end()

def drawROI(view_control, painter, roiStat, roiId):
    xpix, ypix = roiStat["xpix"], roiStat["ypix"]
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

def highlightSelectedROI(view_control, painter, data_manager, key_app):
    selectedRoiId = data_manager.getSelectedROI(key_app)
    if selectedRoiId is not None:
        roiStat = data_manager.dict_Fall[key_app]["stat"][selectedRoiId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        color = view_control.getROIColor(selectedRoiId)
        opacity = view_control.getHighlightOpacity()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))


