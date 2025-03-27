from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap, QTransform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
import numpy as np
from ..config.constants import ChannelKeys, PenColors, PenWidth
from .view_visual_roi import updateLayerROI_Suite2pROICuration, updateLayerROI_Suite2pROITracking, updateLayerROI_MicrogliaTracking, updateLayerROI_TIFStackExplorer
from ..preprocessing.preprocessing_roi import updateROIImage

"""
update View
"""
# q_view widget visualization
# update view for Fall data
def updateView_Suite2pROICuration(
        q_scene: QGraphicsScene, 
        q_view: QGraphicsView, 
        view_control: ViewControl, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys,
        ) -> None:
    # background image
    bg_image_chan1 = None
    bg_image_chan2 = None
    bg_image_chan3 = None  # optional

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

    # convert mono images to RGB image
    (width, height) = view_control.getImageSize()
    bg_image = convertMonoImageToRGBImage(
        image_g=bg_image_chan1, 
        image_r=bg_image_chan2, 
        image_b=bg_image_chan3,
        height=height,
        width=width,
        dtype=np.uint8)

    # update background layer
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    view_control.layer_bg.setPixmap(pixmap)

    # update ROI layer
    updateLayerROI_Suite2pROICuration(view_control, data_manager, control_manager, app_key)

# update view for Fall data for ROI Tracking
def updateView_Suite2pROITracking(
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
    # if view_control.getBackgroundVisibility(ChannelKeys.CHAN2) and data_manager.getNChannels(app_key) == 2:
    #     if view_control.getShowRegImBG():
    #         image = data_manager.getDictBackgroundImageChannel2Registered(app_key).get("meanImg")
    #     else:
    #         image = data_manager.getDictBackgroundImageChannel2(app_key).get("meanImg")
    #     bg_image_chan2 = adjustChannelContrast(
    #         image=image,
    #         min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
    #         max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
    #         )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2) and app_key == "pri":
        image_type = control_manager.view_controls[app_key_sec].getBackgroundImageType()
        if view_control.getShowRegImBG():
            image = data_manager.getDictBackgroundImageRegistered(app_key_sec).get(image_type)
        else:
            image = data_manager.getDictBackgroundImage(app_key_sec).get(image_type)
        bg_image_chan2 = adjustChannelContrast(
            image=image,
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )
    # ROI image, only "pri" view
    if app_key_sec:
        if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
            control_manager.view_controls[app_key_sec].updateROIImage() # update ROI image for pri view
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

    # update background layer
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    view_control.layer_bg.setPixmap(pixmap)

    # update ROI layer
    updateLayerROI_Suite2pROITracking(view_control, data_manager, control_manager, app_key, app_key_sec)

# update view for Tiff data, microglia tracking
def updateView_MicrogliaTracking(
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
    bg_image_chan3 = None 
    plane_z = view_control.getPlaneZ()
    plane_t = view_control.getPlaneT()
    min_val_image = np.min(data_manager.getTiffStack(app_key))
    max_val_image = np.max(data_manager.getTiffStack(app_key))

    # chan 1
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 0, view_control.getShowRegStack()),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    # chan 2
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getImageFromXYCZTTiffStack(app_key, plane_z, plane_t, 1, view_control.getShowRegStack()),
            min_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val_slider=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            min_val_image=min_val_image,
            max_val_image=max_val_image
            )
    # ROI image, only "pri" view
    if app_key_sec:
        if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
            control_manager.view_controls[app_key_sec].updateROIImageForXYCT() # update ROI image for pri view
            if view_control.getShowRegImROI():
                image = data_manager.getDictROIImageRegistered(app_key_sec).get("all")
            else:
                image = data_manager.getDictROIImage(app_key_sec).get("all")
            if image is None:
                bg_image_chan3 = None
            else:
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
        )

    # Caution !!! width and height are swapped between TIFF and QImage
    bg_image_corrected = np.ascontiguousarray(bg_image.transpose(1, 0, 2))

    # Create QImage
    qimage = QImage(
        bg_image_corrected.data,
        width,
        height,
        width * 3,
        QImage.Format_RGB888
    )
    pixmap = QPixmap.fromImage(qimage)
    view_control.layer_bg.setPixmap(pixmap)

    try:
        updateLayerROI_MicrogliaTracking(view_control, data_manager, control_manager, app_key, app_key_sec)
    except AttributeError:
        pass


# update view for Tiff data
def updateView_TIFStackExplorer(
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

    # update background layer
    # Caution !!! width and height are swapped between TIFF and QImage
    bg_image_corrected = np.ascontiguousarray(bg_image.transpose(1, 0, 2))

    # Create QImage
    qimage = QImage(
        bg_image_corrected.data,
        width,
        height,
        width * 3,
        QImage.Format_RGB888
    )
    pixmap = QPixmap.fromImage(qimage)
    view_control.layer_bg.setPixmap(pixmap)

    # update ROI layer
    updateLayerROI_TIFStackExplorer(view_control, data_manager, control_manager, app_key)


"""
Sub functions for updateView
"""
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
    
# scroll zoom event
def zoomView(
    q_view: QGraphicsView,
    delta: float,
    center_pos: QPoint,
    zoom_factor: float = 1.2,
    max_scale: float = 10.0
) -> None:
    """
    Zoom view with specified position as center
    
    Args:
        q_view: Target view
        delta: Zoom delta value (positive for zoom in, negative for zoom out)
        center_pos: Center position for zooming
        zoom_factor: Zoom scale factor
        max_scale: Maximum zoom scale
    """
    scene_pos = q_view.mapToScene(center_pos)
    current_scale = q_view.transform().m11()
    
    if delta > 0 and current_scale < max_scale:
        factor = zoom_factor
    elif delta < 0:
        factor = 1.0/zoom_factor
    else:
        return

    q_view.scale(factor, factor)
    new_pos = q_view.mapFromScene(scene_pos)
    delta = center_pos - new_pos
    q_view.horizontalScrollBar().setValue(q_view.horizontalScrollBar().value() - delta.x())
    q_view.verticalScrollBar().setValue(q_view.verticalScrollBar().value() - delta.y())
    q_view.viewport().update()

# reset zoom
def resetZoomView(
    view: QGraphicsView,
    scene_rect: QRectF
) -> None:
    view.setTransform(QTransform())
    view.fitInView(scene_rect, Qt.KeepAspectRatio)