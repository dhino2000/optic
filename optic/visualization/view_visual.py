from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from ..config.constants import ChannelKeys, PenColors, PenWidth
from .view_visual_roi import drawAllROIs, drawAllROIsWithTracking, drawROI, findClosestROI, shouldSkipROI, drawAllROIsForMicrogliaTracking
from .view_visual_rectangle import drawRectangle, drawRectangleIfInRange
from ..preprocessing.preprocessing_roi import updateROIImage

# q_view widget visualization
# update view for Fall data
def updateViewFall(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None # optional

    # chan 1
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        image_type = view_control.getBackgroundImageType()
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImage(app_key).get(image_type),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            )
    # chan 2
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2) and data_manager.getNChannels(app_key) == 2:
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImageChannel2(app_key).get("meanImg"),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )
    # optional
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3) and isinstance(data_manager.getBackgroundImageOptional(app_key), np.ndarray):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getBackgroundImageOptional(app_key),
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

    drawAllROIs(view_control, pixmap, data_manager, control_manager, app_key)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# update view for Fall data for ROI Tracking
def updateViewFallWithTracking(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        app_key_sec: AppKeys = None,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None # optional

    # chan 1
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        image_type = view_control.getBackgroundImageType()
        if view_control.getShowRegImBG():
            image = data_manager.getDictBackgroundImageRegistered(app_key).get(image_type) 
        else:
            image = data_manager.getDictBackgroundImage(app_key).get(image_type)
        bg_image_chan1 = adjustChannelContrast(
            image=image,
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            )
    # chan 2
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2) and data_manager.getNChannels(app_key) == 2:
        if view_control.getShowRegImBG():
            image = data_manager.getDictBackgroundImageChannel2Registered(app_key).get("meanImg")
        else:
            image = data_manager.getDictBackgroundImageChannel2(app_key).get("meanImg")
        bg_image_chan2 = adjustChannelContrast(
            image=image,
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )
    # ROI image, only "pri" view
    if app_key_sec:
        if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
            control_manager.view_controls[app_key_sec].updateROIImage()
            if view_control.getShowRegImROI():
                image = data_manager.getDictROIImageRegistered(app_key_sec).get("all")
            else:
                image = data_manager.getDictROIImage(app_key_sec).get("all")
            bg_image_chan3 = adjustChannelContrast(
                image=image,
                min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'min'),
                max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'max'),
                scaling=False,
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

    drawAllROIsWithTracking(view_control, pixmap, data_manager, control_manager, app_key, app_key_sec)

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
        app_key: AppKeys,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None 
    plane_z = view_control.getPlaneZ()
    plane_t = view_control.getPlaneT()
    min_val_image = np.min(data_manager.getTiffStack(app_key))
    max_val_image = np.max(data_manager.getTiffStack(app_key))

    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 0, view_control.show_reg_stack),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 1, view_control.show_reg_stack),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 2, view_control.show_reg_stack),
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
            color=PenColors.RECTANGLE_DRAG,
            width=PenWidth.RECTANGLE,
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
            color=PenColors.RECTANGLE_HIGHLIGHT,
            width=PenWidth.RECTANGLE,
            existing_rect=existing_rect,
        )
        view_control.setRect(new_rect)

    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# update view for Tiff data, microglia tracking
def updateViewTiffWithTracking(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        ) -> None:
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None 
    plane_z = view_control.getPlaneZ()
    plane_t = view_control.getPlaneT()
    min_val_image = np.min(data_manager.getTiffStack(app_key))
    max_val_image = np.max(data_manager.getTiffStack(app_key))

    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 0, view_control.show_reg_stack),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 1, view_control.show_reg_stack),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 2, view_control.show_reg_stack),
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

    try:
        drawAllROIsForMicrogliaTracking(view_control, pixmap, data_manager, control_manager, app_key, plane_t)
    except AttributeError:
        pass

    q_scene.clear()
    q_scene.addPixmap(pixmap)

    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# create RGB image from Mono images
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
        min_val_slider: float,  # 0-255
        max_val_slider: float,  # 0-255
        min_val_image: float = None,
        max_val_image: float = None,
        scaling: bool = True,
        ) -> np.ndarray:
    try:
        # Get image min/max values if not provided
        if min_val_image is None:
            min_val_image = np.min(image)
        if max_val_image is None:
            max_val_image = np.max(image)

        image_float = image.astype(np.float32)

        if scaling:
            # Scale slider values to image range
            min_val = min_val_image + (min_val_slider / 255) * (max_val_image - min_val_image)
            max_val = min_val_image + (max_val_slider / 255) * (max_val_image - min_val_image)
            
            # Scale to 0-1 range
            image_scaled = (image_float - min_val) / (max_val - min_val)
            
            # Clip to 0-1 and scale to 0-255
            image_clipped = np.clip(image_scaled, 0, 1)
            image_uint8 = (image_clipped * 255).astype(np.uint8)
            
        else:
            # Use slider values directly as thresholds
            image_scaled = np.clip(image_float, min_val_slider, max_val_slider)
            
            # Scale the clipped values to maintain relative intensities
            if max_val_slider > min_val_slider:
                image_scaled = ((image_scaled - min_val_slider) / 
                              (max_val_slider - min_val_slider) * 255)
            else:
                image_scaled = np.zeros_like(image_float)
                
            image_uint8 = np.clip(image_scaled, 0, 255).astype(np.uint8)

        return image_uint8

    except Exception as e:
        print(f"Error in adjustChannelContrast: {str(e)}")
        raise e
        return None