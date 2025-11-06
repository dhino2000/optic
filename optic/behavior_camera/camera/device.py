# behavior_camera/camera/device.py
# カメラデバイスの検出と初期化を管理するモジュール

import cv2
import numpy as np
from typing import Optional, Tuple, List
from enum import Enum

try:
    from pypylon import pylon
    PYPYLON_AVAILABLE = True
except ImportError:
    PYPYLON_AVAILABLE = False
    print("Warning: pypylon not available. Basler camera support disabled.")


class CameraType(Enum):
    """カメラタイプの列挙"""
    BASLER = "Basler"
    USB = "USB"
    NONE = "None"


class CameraDevice:
    """
    カメラデバイスの検出、初期化、制御を管理するクラス
    BaslerカメラとUSBカメラの両方に対応
    """
    
    def __init__(self):
        self.camera_type = CameraType.NONE
        self.camera = None
        self.converter = None  # Basler用
        self.is_configured = False  # カメラ設定が適用済みか
        
    def detectCameras(self) -> Tuple[List[str], List[str]]:
        """
        接続されているカメラを検出
        
        Returns:
            Tuple[List[str], List[str]]: (Baslerカメラリスト, USBカメラリスト)
        """
        basler_cameras = []
        usb_cameras = []
        
        # Baslerカメラを検出
        if PYPYLON_AVAILABLE:
            try:
                tl_factory = pylon.TlFactory.GetInstance()
                devices = tl_factory.EnumerateDevices()
                basler_cameras = [device.GetFriendlyName() for device in devices]
            except Exception as e:
                print(f"Error detecting Basler cameras: {e}")
        
        # USBカメラを検出（最大10個まで）
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                usb_cameras.append(f"USB Camera {i}")
                cap.release()
            else:
                break
        
        return basler_cameras, usb_cameras
    
    def initializeCamera(self) -> Tuple[bool, str]:
        """
        カメラを自動検出して初期化
        
        Returns:
            Tuple[bool, str]: (成功フラグ, メッセージ)
        """
        basler_cameras, usb_cameras = self.detectCameras()
        
        total_cameras = len(basler_cameras) + len(usb_cameras)
        
        # カメラが見つからない場合
        if total_cameras == 0:
            return False, "No camera detected."
        
        # 複数カメラが見つかった場合
        if total_cameras > 1:
            camera_list = basler_cameras + usb_cameras
            error_msg = f"Multiple cameras detected ({total_cameras}):\n"
            error_msg += "\n".join([f"  - {cam}" for cam in camera_list])
            error_msg += "\n\nPlease connect only one camera."
            return False, error_msg
        
        # Baslerカメラを初期化
        if len(basler_cameras) == 1:
            try:
                self._initializeBaslerCamera()
                return True, f"Basler camera initialized: {basler_cameras[0]}"
            except Exception as e:
                return False, f"Failed to initialize Basler camera: {e}"
        
        # USBカメラを初期化
        if len(usb_cameras) == 1:
            try:
                self._initializeUSBCamera(0)
                return True, f"USB camera initialized: {usb_cameras[0]}"
            except Exception as e:
                return False, f"Failed to initialize USB camera: {e}"
        
        return False, "Unknown error during camera initialization."
    
    def _initializeBaslerCamera(self):
        """Baslerカメラを初期化"""
        if not PYPYLON_AVAILABLE:
            raise RuntimeError("pypylon is not available")
        
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_Mono8
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.camera_type = CameraType.BASLER
    
    def _initializeUSBCamera(self, index: int):
        """USBカメラを初期化"""
        self.camera = cv2.VideoCapture(index, cv2.CAP_DSHOW) # cv2.CAP_MSMF does not work well on some systems
        if not self.camera.isOpened():
            raise RuntimeError(f"Failed to open USB camera {index}")
        self.camera_type = CameraType.USB
    
    def setCameraConfig(self, fps: float, width: int, height: int, 
                       offsetx: int, offsety: int, gain: float, 
                       exposure_time: float):
        """
        カメラ設定を適用
        
        Args:
            fps: フレームレート
            width: 画像幅
            height: 画像高さ
            offsetx: X方向オフセット
            offsety: Y方向オフセット
            gain: ゲイン
            exposure_time: 露光時間
        """
        if self.camera_type == CameraType.BASLER:
            self._setBaslerConfig(fps, width, height, offsetx, offsety, gain, exposure_time)
        elif self.camera_type == CameraType.USB:
            self._setUSBConfig(fps, width, height)
        
        self.is_configured = True  # 設定適用済みフラグ
    
    def _setBaslerConfig(self, fps: float, width: int, height: int,
                        offsetx: int, offsety: int, gain: float,
                        exposure_time: float):
        """Baslerカメラの設定"""
        self.camera.Open()
        self.camera.AcquisitionFrameRateEnable.SetValue(True)
        self.camera.AcquisitionFrameRate.SetValue(fps)
        self.camera.OffsetX = offsetx
        self.camera.OffsetY = offsety
        self.camera.Width = width
        self.camera.Height = height
        self.camera.Gain = gain
        self.camera.ExposureTime.SetValue(exposure_time)
    
    def _setUSBConfig(self, fps: float, width: int, height: int):
        """USBカメラの設定"""
        self.camera.set(cv2.CAP_PROP_FPS, fps)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print(f"USB Camera set Width: {self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"USB Camera set Height: {self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"USB Camera set FPS: {self.camera.get(cv2.CAP_PROP_FPS)}")
    
    def captureFrame(self) -> Optional[np.ndarray]:
        """
        1フレームをキャプチャ
        
        Returns:
            Optional[np.ndarray]: キャプチャした画像、失敗時はNone
        """
        if self.camera_type == CameraType.BASLER:
            return self._captureBaslerFrame()
        elif self.camera_type == CameraType.USB:
            return self._captureUSBFrame()
        return None
    
    def _captureBaslerFrame(self) -> Optional[np.ndarray]:
        """Baslerカメラから1フレームキャプチャ"""
        try:
            if not self.camera.IsGrabbing():
                self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
            
            grab_result = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )
            
            if grab_result.GrabSucceeded():
                image = self.converter.Convert(grab_result)
                img = image.GetArray()
                grab_result.Release()
                return img
            else:
                grab_result.Release()
                return None
        except Exception as e:
            print(f"Error capturing Basler frame: {e}")
            return None
    
    def _captureUSBFrame(self) -> Optional[np.ndarray]:
        """USBカメラから1フレームキャプチャ"""
        ret, frame = self.camera.read()
        if ret:
            # グレースケール変換
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return frame
        return None
    
    def startGrabbing(self):
        """連続撮影を開始"""
        if self.camera_type == CameraType.BASLER:
            if not self.camera.IsGrabbing():
                self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    
    def stopGrabbing(self):
        """連続撮影を停止"""
        if self.camera_type == CameraType.BASLER:
            if self.camera.IsGrabbing():
                self.camera.StopGrabbing()
    
    def close(self):
        """カメラを閉じる"""
        if self.camera_type == CameraType.BASLER:
            if self.camera.IsOpen():
                self.camera.Close()
        elif self.camera_type == CameraType.USB:
            if self.camera is not None:
                self.camera.release()
        
        self.camera = None
        self.camera_type = CameraType.NONE
    
    def getCameraType(self) -> CameraType:
        """カメラタイプを取得"""
        return self.camera_type
    
    def isInitialized(self) -> bool:
        """カメラが初期化されているか確認"""
        return self.camera_type != CameraType.NONE