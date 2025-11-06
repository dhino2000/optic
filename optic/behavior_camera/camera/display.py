# behavior_camera/camera/display.py
# カメラ画像の表示を管理するモジュール

import numpy as np
from typing import Optional
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


class DisplayEngine:
    """
    カメラ画像の表示を管理するクラス
    numpy配列をQtウィジェットに表示する
    """
    
    def __init__(self, q_label: Optional[QLabel] = None):
        self.q_label = q_label
        self.keep_aspect_ratio = True
        self.smooth_transform = True
    
    def setDisplayLabel(self, q_label: QLabel):
        """
        表示先ラベルを設定
        
        Args:
            q_label: 画像を表示するQLabel
        """
        self.q_label = q_label
    
    def updateDisplay(self, frame: np.ndarray) -> bool:
        """
        フレームを表示
        
        Args:
            frame: 表示する画像（numpy配列）
            
        Returns:
            bool: 成功フラグ
        """
        if self.q_label is None:
            print("Error: Display label not set")
            return False
        
        if frame is None:
            return False
        
        # numpy配列をQImageに変換
        q_image = self._convertNumpyToQImage(frame)
        if q_image is None:
            return False
        
        # QPixmapに変換
        pixmap = QPixmap.fromImage(q_image)
        
        # スケーリング
        if self.keep_aspect_ratio:
            scaled_pixmap = pixmap.scaled(
                self.q_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation if self.smooth_transform else Qt.FastTransformation
            )
        else:
            scaled_pixmap = pixmap.scaled(
                self.q_label.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation if self.smooth_transform else Qt.FastTransformation
            )
        
        # ラベルに表示
        self.q_label.setPixmap(scaled_pixmap)
        
        return True
    
    def _convertNumpyToQImage(self, frame: np.ndarray) -> Optional[QImage]:
        """
        numpy配列をQImageに変換
        
        Args:
            frame: 変換する画像
            
        Returns:
            Optional[QImage]: 変換されたQImage、失敗時はNone
        """
        if frame is None or frame.size == 0:
            return None
        
        # グレースケール画像の場合
        if len(frame.shape) == 2:
            height, width = frame.shape
            bytes_per_line = width
            q_image = QImage(
                frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_Grayscale8
            )
            return q_image.copy()  # データのコピーを作成
        
        # RGB画像の場合
        elif len(frame.shape) == 3:
            height, width, channels = frame.shape
            bytes_per_line = width * channels
            
            if channels == 3:
                q_image = QImage(
                    frame.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGB888
                )
                return q_image.copy()
            elif channels == 4:
                q_image = QImage(
                    frame.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGBA8888
                )
                return q_image.copy()
        
        print(f"Error: Unsupported image format: shape={frame.shape}")
        return None
    
    def clearDisplay(self):
        """表示をクリア"""
        if self.q_label:
            self.q_label.clear()
    
    def setKeepAspectRatio(self, keep: bool):
        """
        アスペクト比維持の設定
        
        Args:
            keep: Trueならアスペクト比維持
        """
        self.keep_aspect_ratio = keep
    
    def setSmoothTransform(self, smooth: bool):
        """
        スムーズ変換の設定
        
        Args:
            smooth: Trueならスムーズ変換
        """
        self.smooth_transform = smooth