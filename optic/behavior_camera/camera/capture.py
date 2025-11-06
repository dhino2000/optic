# behavior_camera/camera/capture.py
# 連続撮影セッションを管理するモジュール

import time
import numpy as np
from typing import Optional, List, Callable
from .device import CameraDevice


class CaptureSession:
    """
    連続撮影セッションを管理するクラス
    タイムスタンプ記録、FPS計算、フレームバッファ管理を担当
    """
    
    def __init__(self, camera_device: CameraDevice):
        """
        Args:
            camera_device: CameraDeviceインスタンス
        """
        self.camera_device = camera_device
        self.is_capturing = False
        self.timestamps = []
        self.frame_count = 0
        self.start_time = None
        
        # コールバック関数
        self.on_frame_callback = None  # フレーム取得時に呼ばれる
    
    def startCapture(self) -> bool:
        """
        連続撮影を開始
        
        Returns:
            bool: 成功フラグ
        """
        if not self.camera_device.isInitialized():
            print("Error: Camera not initialized")
            return False
        
        if self.is_capturing:
            print("Warning: Already capturing")
            return False
        
        # カメラの連続撮影開始
        self.camera_device.startGrabbing()
        
        # 初期化
        self.timestamps = []
        self.frame_count = 0
        self.start_time = time.time()
        self.is_capturing = True
        
        print("Capture started")
        return True
    
    def stopCapture(self) -> bool:
        """
        連続撮影を停止
        
        Returns:
            bool: 成功フラグ
        """
        if not self.is_capturing:
            print("Warning: Not capturing")
            return False
        
        # カメラの連続撮影停止
        self.camera_device.stopGrabbing()
        
        self.is_capturing = False
        print(f"Capture stopped. Total frames: {self.frame_count}")
        
        return True
    
    def getFrame(self) -> Optional[np.ndarray]:
        """
        1フレーム取得してタイムスタンプ記録
        
        Returns:
            Optional[np.ndarray]: 取得したフレーム、失敗時はNone
        """
        if not self.is_capturing:
            return None
        
        # フレーム取得
        frame = self.camera_device.captureFrame()
        
        if frame is not None:
            # タイムスタンプ記録
            timestamp = time.time()
            self.timestamps.append(timestamp)
            self.frame_count += 1
            
            # コールバック実行
            if self.on_frame_callback:
                self.on_frame_callback(frame, timestamp)
        
        return frame
    
    def setOnFrameCallback(self, callback: Callable[[np.ndarray, float], None]):
        """
        フレーム取得時のコールバック関数を設定
        
        Args:
            callback: コールバック関数 (frame, timestamp) -> None
        """
        self.on_frame_callback = callback
    
    def calculateFPS(self) -> float:
        """
        現在のFPSを計算
        
        Returns:
            float: FPS値
        """
        if not self.start_time or self.frame_count == 0:
            return 0.0
        
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            return 0.0
        
        return self.frame_count / elapsed_time
    
    def getAverageFPS(self) -> float:
        """
        タイムスタンプから平均FPSを計算
        
        Returns:
            float: 平均FPS
        """
        if len(self.timestamps) < 2:
            return 0.0
        
        total_time = self.timestamps[-1] - self.timestamps[0]
        if total_time == 0:
            return 0.0
        
        return (len(self.timestamps) - 1) / total_time
    
    def getTimestamps(self) -> List[float]:
        """
        記録されたタイムスタンプのリストを取得
        
        Returns:
            List[float]: タイムスタンプのリスト
        """
        return self.timestamps.copy()
    
    def getFrameCount(self) -> int:
        """
        取得したフレーム数を取得
        
        Returns:
            int: フレーム数
        """
        return self.frame_count
    
    def isCapturing(self) -> bool:
        """
        撮影中かどうかを取得
        
        Returns:
            bool: 撮影中ならTrue
        """
        return self.is_capturing
    
    def reset(self):
        """撮影データをリセット"""
        self.timestamps = []
        self.frame_count = 0
        self.start_time = None