from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from ..config.constants import ChannelKeys

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

    if view_control.getBackgroundVisibility(ChannelKeys.CHAN1):
        image_type = view_control.getBackgroundImageType()
        bg_image_chan1 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImage(key_app).get(image_type),
            min_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'min'),
            max_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN1, 'max'),
            )
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN2):
        image_type = view_control.getBackgroundImageType()
        bg_image_chan2 = adjustChannelContrast(
            image=data_manager.getDictBackgroundImage(key_app).get(image_type), # 後でchannel2用に修正
            min_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'min'),
            max_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN2, 'max'),
            )
    # optional
    if view_control.getBackgroundVisibility(ChannelKeys.CHAN3):
        bg_image_chan3 = adjustChannelContrast(
            image=data_manager.getBackgroundImageOptional(key_app),
            min_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'min'),
            max_val=view_control.getBackgroundContrastValue(ChannelKeys.CHAN3, 'max'),
            )

    (width, height) = view_control.getImageSize()
    bg_image = convertMonoImageToRGBImage(image_g=bg_image_chan1, image_r=bg_image_chan2, image_b=bg_image_chan3)

    height, width = bg_image.shape[:2]
    qimage = QImage(bg_image.data, width, height, width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    drawAllROIs(view_control, pixmap, data_manager, control_manager, key_app)

    q_scene.clear()
    q_scene.addPixmap(pixmap)
    q_view.setScene(q_scene)
    q_view.fitInView(q_scene.sceneRect(), Qt.KeepAspectRatio)

# update view for Tiff data
def updateViewTiff() -> None:
    pass

# 白黒画像からカラー画像作成
def convertMonoImageToRGBImage(
        image_r: Optional[np.ndarray] = None, 
        image_g: Optional[np.ndarray] = None, 
        image_b: Optional[np.ndarray] = None,
        height: int = 512,
        width: int = 512
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

def adjustChannelContrast(
        image: np.ndarray, 
        min_val: int, 
        max_val: int, 
        dtype: np.dtype=np.uint8
        ) -> np.ndarray:
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

def drawAllROIs(
        view_control: ViewControl, 
        pixmap: QPixmap, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        key_app: str
        ) -> None:
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    roi_display = control_manager.getSharedAttr(key_app, "roi_display")
    
    for roiId, roiStat in data_manager.getStat(key_app).items():
        if roi_display[roiId]:
            drawROI(view_control, painter, roiStat, roiId)
    
    highlightROISelected(view_control, painter, data_manager, control_manager, key_app)
    painter.end()

def drawROI(
        view_control: ViewControl, 
        painter: QPainter, 
        roiStat: Dict[str, Any],
        roiId: int
        ) -> None:
    xpix, ypix = roiStat["xpix"], roiStat["ypix"]
    color = view_control.getROIColor(roiId)
    opacity = view_control.getROIOpacity()
    
    pen = QPen(QColor(*color, opacity))
    painter.setPen(pen)
    
    for x, y in zip(xpix, ypix):
        painter.drawPoint(int(x), int(y))

def highlightROISelected(
        view_control: ViewControl, 
        painter: QPainter, 
        data_manager: DataManager, 
        control_manager: ControlManager, 
        key_app: str
        ) -> None:
    ROISelectedId = control_manager.getSharedAttr(key_app, "roi_selected_id")
    if ROISelectedId is not None:
        roiStat = data_manager.getStat(key_app)[ROISelectedId]
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        color = view_control.getROIColor(ROISelectedId)
        opacity = view_control.getHighlightOpacity()
        
        pen = QPen(QColor(*color, opacity))
        painter.setPen(pen)
        
        for x, y in zip(xpix, ypix):
            painter.drawPoint(int(x), int(y))

# find Closest ROI to click position
def findClosestROI(
        x: int, 
        y: int, 
        dict_roi_med: dict, 
        skip_roi: dict = None
        ) -> Optional[int]:
    if not dict_roi_med:
        return None
    
    min_distance = float('inf')
    closest_roi_id = None

    for roi_id, med in dict_roi_med.items():
        if skip_roi and skip_roi.get(roi_id, False):
            continue
        distance = np.sqrt((x - med[0])**2 + (y - med[1])**2)
        if distance < min_distance:
            min_distance = distance
            closest_roi_id = roi_id

    return closest_roi_id

# Skip ROIs with "Skip" checkbox checked
def shouldSkipROI(
        roi_id: int, 
        table_columns: dict, 
        q_table: QTableWidget, 
        skip_checkboxes: List[QCheckBox]
        ) -> bool:
    for checkbox in skip_checkboxes:
        if checkbox.isChecked():
            celltype = checkbox.text().replace("Skip ", "").replace(" ROI", "")
            for col_name, col_info in table_columns.items():
                if col_name == celltype:
                    if col_info['type'] == 'celltype':
                        radio_button = q_table.cellWidget(roi_id, col_info['order'])
                        if radio_button and radio_button.isChecked():
                            return True
                    elif col_info['type'] == 'checkbox':
                        checkbox_item = q_table.item(roi_id, col_info['order'])
                        if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                            return True
    return False



