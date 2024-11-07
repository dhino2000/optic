from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from ..config.constants import ChannelKeys, RectangleColors, DrawingWidth
from .view_visual_roi import drawAllROIs, drawROI, highlightROISelected, findClosestROI, shouldSkipROI
from .view_visual_rectangle import drawRectangle, drawRectangleIfInRange

# q_view widget visualization
# update view for Fall data
def updateViewFall(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        key_app: str,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None # optional

    # chan 1
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        image_type = view_control.getBackgroundImageType()
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImage(key_app).get(image_type),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            )
    # chan 2
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2) and data_manager.getNChannels(key_app) == 2:
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImageChannel2(key_app).get("meanImg"),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )
    # optional
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3) and isinstance(data_manager.getBackgroundImageOptional(key_app), np.ndarray):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getBackgroundImageOptional(key_app),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'max'),
            )

    (width, height) = view_control.getImageSize()
    bg_image = convertMonoImageToRGBImage(
        image_g=bg_image_chan1, 
        image_r=bg_image_chan2, 
        image_b=bg_image_chan3,
        height=height,
        width=width,
        dtype=np.uint8)

    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    drawAllROIs(view_control, pixmap, data_manager, control_manager, key_app)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# update view for Tiff data
def updateViewTiff(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        key_app: str,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None 
    plane_z = view_control.getPlaneZ()
    plane_t = view_control.getPlaneT()
    min_val_image = np.min(data_manager.getTiffStack(key_app))
    max_val_image = np.max(data_manager.getTiffStack(key_app))

    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(key_app, plane_z, plane_t, 0, view_control.show_reg),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(key_app, plane_z, plane_t, 1, view_control.show_reg),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(key_app, plane_z, plane_t, 2, view_control.show_reg),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )

    (width, height) = view_control.getImageSize()
    bg_image = convertMonoImageToRGBImage(
        image_g=bg_image_chan1, 
        image_r=bg_image_chan2, 
        image_b=bg_image_chan3, 
        height=height,
        width=width,
        )

    # Caution !!! width and height are swapped between TIFF and QImage
    qimage = QImage(bg_image.data, height, width, height * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    # draw rectangle
    rect_range = view_control.getRectRange()
    existing_rect = view_control.getRect()
    if rect_range:
        x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max = rect_range
        current_z = view_control.getPlaneZ()
        current_t = view_control.getPlaneT()
        new_rect = drawRectangleIfInRange(
            q_scene, current_z, current_t,
            x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max,
            color=RectangleColors.DRAG,
            width=DrawingWidth.RECTANGLE,
            existing_rect=existing_rect,
        )
        view_control.setRect(new_rect)

    # draw highlight rectangle
    rect_range = view_control.getRectHighlightRange()
    existing_rect = view_control.getRectHighlight()
    if rect_range:
        x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max = rect_range
        current_z = view_control.getPlaneZ()
        current_t = view_control.getPlaneT()
        new_rect = drawRectangleIfInRange(
            q_scene, current_z, current_t,
            x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max,
            color=RectangleColors.HIGHLIGHT,
            width=DrawingWidth.RECTANGLE,
            existing_rect=existing_rect,
        )
        view_control.setRect(new_rect)

    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# 白黒画像からカラー画像作成
def convertMonoImageToRGBImage(
        image_r: Optional[np.ndarray] = None, 
        image_g: Optional[np.ndarray] = None, 
        image_b: Optional[np.ndarray] = None,
        height: int = 512,
        width: int = 512,
        dtype: np.dtype = np.uint8
        ) -> np.ndarray:
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
    # return black image if no image provided
    images = [img for img in [image_r, image_g, image_b] if img is not None]
    if not images:
        return np.zeros((width, height, 3), dtype=dtype)
    # check if all images have the same shapes
    if len(set(img.shape for img in images)) != 1:
        raise ValueError("All provided images must have the same shapes")

    rgb_image = np.zeros((width, height, 3), dtype=dtype)
    for i, img in enumerate([image_r, image_g, image_b]):
        if img is not None:
            rgb_image[:, :, i] = img

    return rgb_image

def adjustChannelContrast(
        image: np.ndarray, 
        min_val_slider: float,  # 0-255の範囲
        max_val_slider: float,  # 0-255の範囲
        min_val_image: float = None,
        max_val_image: float = None
        ) -> np.ndarray:
    try:
        # 画像の最小値と最大値を取得または計算
        if min_val_image is None:
            min_val_image = np.min(image)
        if max_val_image is None:
            max_val_image = np.max(image)

        # スライダーの値を入力画像の型に応じた範囲にスケーリング
        min_val = min_val_image + (min_val_slider / 255) * (max_val_image - min_val_image)
        max_val = min_val_image + (max_val_slider / 255) * (max_val_image - min_val_image)

        # 入力範囲を0-1にスケーリング
        image_float = image.astype(np.float32)
        image_scaled = (image_float - min_val) / (max_val - min_val)

        # 0-1の範囲にクリップ
        image_clipped = np.clip(image_scaled, 0, 1)

        # 0-255の範囲にスケーリングしてuint8に変換
        image_uint8 = (image_clipped * 255).astype(np.uint8)

        return image_uint8

    except Exception as e:
        print(f"Error in adjustChannelContrast: {str(e)}")
        return None