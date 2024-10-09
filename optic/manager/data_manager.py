from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict
from scipy.io import loadmat
import numpy as np
from numpy.typing import NDArray
import tifffile
from ..preprocessing.preprocessing_image import getBGImageFromFall, getBGImageChannel2FromFall
from ..config.constants import Extension
from ..io.data_io import loadFallMat, loadTiffStack, loadTifImage

class DataManager:
    def __init__(self):
        self.dict_im_dtype:        Dict[str, str] = {}
        self.dict_Fall:            Dict[str, Any] = {}
        self.dict_tiff:            Dict[str, np.ndarray[Tuple[int, int, int, int, int]]] = {}

        self.dict_im_bg:           Dict[str, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_chan2:     Dict[str, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_optional:  Dict[str, np.ndarray[np.uint8, Tuple[int, int]]] = defaultdict(dict)
        self.dict_eventfile:       Dict[str, np.ndarray[Tuple[int]]] = {}
        self.dict_roicheck:        Dict[str, Any] = {}

    """
    IO Functions
    """
    # load Fall.mat data
    def loadFallMat(self, key_app: str, path_fall: str, preprocessing: bool=True) -> bool:
        try:
            dict_Fall = loadFallMat(path_fall)
            self.dict_Fall[key_app] = dict_Fall
            self.dict_im_dtype[key_app] = Extension.MAT
            self.dict_im_bg[key_app] = getBGImageFromFall(self, key_app)
            if self.getNChannels(key_app) == 2:
                self.dict_im_bg_chan2[key_app] = getBGImageChannel2FromFall(self, key_app)
            return True
        except Exception as e:
            return False
        
    # load tiff image data (for optional)
    def loadTifImage(self, key_app: str, path_image: str) -> bool:
        try:
            self.dict_im_bg_optional[key_app] = loadTifImage(path_image)
            return True
        except Exception as e:
            return False
        
    # load tiff stack data
    def loadTiffStack(self, key_app: str, path_tiff: str) -> bool:
        try:
            tiff = loadTiffStack(path_tiff)
            self.dict_im_dtype[key_app] = Extension.TIFF
            self.dict_tiff[key_app] = tiff
            return True
        except Exception as e:
            return False
        
    """
    get Functions
    """
    "Fall data"
    def getDictFall(self, key_app: str) -> Dict[str, Any]:
        return self.dict_Fall[key_app]
    
    # get F, Fneu, spks
    def getTraces(self, key_app: str) -> Dict[str, NDArray[np.float32]]: # 2d array
        dict_traces = {
            "F": self.dict_Fall[key_app]["F"],
            "Fneu": self.dict_Fall[key_app]["Fneu"],
            "spks": self.dict_Fall[key_app]["spks"]
        }
        return dict_traces
    def getTracesOfSelectedROI(self, key_app: str, roi_id: int) -> Dict[str, NDArray[np.float32]]: # 1d array
        dict_traces = {
            "F": self.dict_Fall[key_app]["F"][roi_id],
            "Fneu": self.dict_Fall[key_app]["Fneu"][roi_id],
            "spks": self.dict_Fall[key_app]["spks"][roi_id]
        }
        return dict_traces
    
    # get stat
    def getStat(self, key_app) -> Dict[int, Dict[str, Any]]:
        return self.dict_Fall[key_app]["stat"]
    
    # get fs
    def getFs(self, key_app: str) -> float:
        return self.dict_Fall[key_app]["ops"]["fs"].flatten()[0]

    # get data length
    def getLengthOfData(self, key_app: str) -> int:
        if self.dict_im_dtype[key_app] == Extension.MAT:
            return len(self.dict_Fall[key_app]["ops"]["xoff1"])
        
    # get nchannels
    def getNChannels(self, key_app: str) -> int:
        return self.dict_Fall[key_app]["ops"]["nchannels"].flatten()[0]
        
    "Tiff data"
    def getSizeOfX(self, key_app: str) -> int:
        return self.dict_tiff[key_app].shape[0]
    def getSizeOfY(self, key_app: str) -> int:
        return self.dict_tiff[key_app].shape[1]
    def getSizeOfC(self, key_app: str) -> int:
        return self.dict_tiff[key_app].shape[2]
    def getSizeOfZ(self, key_app: str) -> int:
        return self.dict_tiff[key_app].shape[3]
    def getSizeOfT(self, key_app: str) -> int:
        return self.dict_tiff[key_app].shape[4]

    # get attibutes
    def getImageDataType(self, key_app: str) -> str:
        return self.dict_im_dtype.get(key_app)

    # get image size, change return with dtype
    def getImageSize(self, key_app: str) -> Tuple[int, int]:
        if self.dict_im_dtype[key_app] == Extension.MAT:
            return (self.dict_Fall[key_app]["ops"]["Lx"].item(), self.dict_Fall[key_app]["ops"]["Ly"].item())
        elif self.dict_im_dtype[key_app] == Extension.TIFF:
            return (self.dict_tiff[key_app].shape[0], self.dict_tiff[key_app].shape[1])
        
    def getImageFromXYCZTTiffStack(self, key_app: str, plane_z: int, plane_t: int, channel: int) -> np.ndarray[np.uint8, Tuple[int, int]]:
        try:
            return self.dict_tiff[key_app][:, :, channel, plane_z, plane_t]
        except IndexError:
            # out of index, return black image
            return np.zeros(self.dict_tiff[key_app].shape[:2], dtype=np.uint8)
    
    def getDictBackgroundImage(self, key_app: str) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]: # 2d array
        return self.dict_im_bg.get(key_app)
    
    def getDictBackgroundImageChannel2(self, key_app: str) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2.get(key_app)
    
    def getBackgroundImageOptional(self, key_app: str) -> np.ndarray[np.uint8, Tuple[int, int]]:
        return self.dict_im_bg_optional.get(key_app)
    
    def getEventfile(self, key_app: str) -> np.array:
        return self.dict_eventfile.get(key_app)
    
    # clear attributes
    def clearEventfile(self, key_app: str) -> None:
        if key_app in self.dict_eventfile:
            del self.dict_eventfile[key_app]
    