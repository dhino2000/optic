# behavior_camera/camera/device.py
# Module for camera device detection and initialization management

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
    """Camera type enumeration"""
    BASLER = "Basler"
    USB = "USB"
    NONE = "None"


class CameraDevice:
    """
    Class for managing camera device detection, initialization, and control
    Supports both Basler and USB cameras
    """
    
    def __init__(self):
        self.camera_type = CameraType.NONE
        self.camera = None
        self.converter = None  # For Basler
        self.is_configured = False  # Flag for camera configuration applied
        
    def detectCameras(self) -> Tuple[List[str], List[str]]:
        """
        Detect connected cameras
        
        Returns:
            Tuple[List[str], List[str]]: (Basler camera list, USB camera list)
        """
        basler_cameras = []
        usb_cameras = []
        
        # Detect Basler cameras
        if PYPYLON_AVAILABLE:
            try:
                tl_factory = pylon.TlFactory.GetInstance()
                devices = tl_factory.EnumerateDevices()
                basler_cameras = [device.GetFriendlyName() for device in devices]
            except Exception as e:
                print(f"Error detecting Basler cameras: {e}")
        
        # Detect USB cameras (up to 10)
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
        Auto-detect and initialize camera
        
        Returns:
            Tuple[bool, str]: (success flag, message)
        """
        basler_cameras, usb_cameras = self.detectCameras()
        
        total_cameras = len(basler_cameras) + len(usb_cameras)
        
        # No camera found
        if total_cameras == 0:
            return False, "No camera detected."
        
        # Multiple cameras found
        if total_cameras > 1:
            camera_list = basler_cameras + usb_cameras
            error_msg = f"Multiple cameras detected ({total_cameras}):\n"
            error_msg += "\n".join([f"  - {cam}" for cam in camera_list])
            error_msg += "\n\nPlease connect only one camera."
            return False, error_msg
        
        # Initialize Basler camera
        if len(basler_cameras) == 1:
            try:
                self._initializeBaslerCamera()
                return True, f"Basler camera initialized: {basler_cameras[0]}"
            except Exception as e:
                return False, f"Failed to initialize Basler camera: {e}"
        
        # Initialize USB camera
        if len(usb_cameras) == 1:
            try:
                self._initializeUSBCamera(0)
                return True, f"USB camera initialized: {usb_cameras[0]}"
            except Exception as e:
                return False, f"Failed to initialize USB camera: {e}"
        
        return False, "Unknown error during camera initialization."
    
    def _initializeBaslerCamera(self):
        """Initialize Basler camera"""
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
        """Initialize USB camera"""
        self.camera = cv2.VideoCapture(index, cv2.CAP_DSHOW) # cv2.CAP_MSMF does not work well on some systems
        if not self.camera.isOpened():
            raise RuntimeError(f"Failed to open USB camera {index}")
        self.camera_type = CameraType.USB
    
    def setCameraConfig(self, fps: float, width: int, height: int, 
                       offsetx: int, offsety: int, gain: float, 
                       exposure_time: float):
        """
        Apply camera configuration
        
        Args:
            fps: Frame rate
            width: Image width
            height: Image height
            offsetx: X offset
            offsety: Y offset
            gain: Gain
            exposure_time: Exposure time
        """
        if self.camera_type == CameraType.BASLER:
            self._setBaslerConfig(fps, width, height, offsetx, offsety, gain, exposure_time)
        elif self.camera_type == CameraType.USB:
            self._setUSBConfig(fps, width, height)
        
        self.is_configured = True
    
    def _setBaslerConfig(self, fps: float, width: int, height: int,
                        offsetx: int, offsety: int, gain: float,
                        exposure_time: float):
        """Configure Basler camera"""
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
        """Configure USB camera"""
        self.camera.set(cv2.CAP_PROP_FPS, fps)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print(f"USB Camera set Width: {self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"USB Camera set Height: {self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"USB Camera set FPS: {self.camera.get(cv2.CAP_PROP_FPS)}")
    
    def getResolution(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Get camera resolution (width, height)
        
        Returns:
            Tuple[Optional[int], Optional[int]]: (width, height), None if failed
        """
        if self.camera_type == CameraType.BASLER:
            try:
                width = self.camera.Width.GetValue()
                height = self.camera.Height.GetValue()
                return width, height
            except Exception as e:
                print(f"Error getting Basler resolution: {e}")
                return None, None
        elif self.camera_type == CameraType.USB:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return None, None
    
    def captureFrame(self) -> Optional[np.ndarray]:
        """
        Capture one frame
        
        Returns:
            Optional[np.ndarray]: Captured image, None if failed
        """
        if self.camera_type == CameraType.BASLER:
            return self._captureBaslerFrame()
        elif self.camera_type == CameraType.USB:
            return self._captureUSBFrame()
        return None
    
    def _captureBaslerFrame(self) -> Optional[np.ndarray]:
        """Capture one frame from Basler camera"""
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
        """Capture one frame from USB camera"""
        ret, frame = self.camera.read()
        if ret:
            # Convert to grayscale
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return frame
        return None
    
    def startGrabbing(self):
        """Start continuous capture"""
        if self.camera_type == CameraType.BASLER:
            if not self.camera.IsGrabbing():
                self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    
    def stopGrabbing(self):
        """Stop continuous capture"""
        if self.camera_type == CameraType.BASLER:
            if self.camera.IsGrabbing():
                self.camera.StopGrabbing()
    
    def close(self):
        """Close camera"""
        if self.camera_type == CameraType.BASLER:
            if self.camera.IsOpen():
                self.camera.Close()
        elif self.camera_type == CameraType.USB:
            if self.camera is not None:
                self.camera.release()
        
        self.camera = None
        self.camera_type = CameraType.NONE
    
    def getCameraType(self) -> CameraType:
        """Get camera type"""
        return self.camera_type
    
    def isInitialized(self) -> bool:
        """Check if camera is initialized"""
        return self.camera_type != CameraType.NONE