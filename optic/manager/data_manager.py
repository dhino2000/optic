from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict
from scipy.io import loadmat
import numpy as np
from numpy.typing import NDArray
import tifffile
from ..preprocessing.preprocessing_fall import convertMatToDictFall
from ..preprocessing.preprocessing_image import getBGImageFromFall
from ..config.constants import Extension
from ..io.data_io import loadTiffStack, loadTifImage

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

    # load Fall.mat data
    def loadFallMAT(self, key_app: str, path_fall: str, preprocessing: bool=True) -> bool:
        try:
            Fall = loadmat(path_fall)
            self.dict_im_dtype[key_app] = Extension.MAT
            if preprocessing:
                dict_Fall = convertMatToDictFall(Fall)
                self.dict_Fall[key_app] = dict_Fall
                getBGImageFromFall(self, key_app, key_app)
            else:
                self.dict_Fall[key_app] = Fall
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
            tiff = tifffile.imread(path_tiff)
            self.dict_im_dtype[key_app] = Extension.TIFF
            self.dict_tiff[key_app] = tiff
            return True
        except Exception as e:
            return False
        
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
        elif self.dict_im_dtype[key_app] == Extension.TIFF:
            return len(self.dict_tiff[key_app])

    # get attibutes
    def getImageDataType(self, key_app: str) -> str:
        return self.dict_im_dtype.get(key_app)

    def getImageSize(self, key_app: str) -> Tuple[int, int]:
        return (self.dict_Fall[key_app]["ops"]["Lx"].item(), self.dict_Fall[key_app]["ops"]["Ly"].item())
    
    def getDictBackgroundImage(self, key_app: str) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]: # 2d array
        return self.dict_im_bg.get(key_app)
    
    def getBackgroundChan2Image(self, key_app: str) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2.get(key_app)
    
    def getBackgroundOptionalImage(self, key_app: str) -> np.ndarray[np.uint8, Tuple[int, int]]:
        return self.dict_im_bg_optional.get(key_app)
    
    def getEventfile(self, key_app: str) -> np.array:
        return self.dict_eventfile.get(key_app)
    
    # clear attributes
    def clearEventfile(self, key_app: str) -> None:
        if key_app in self.dict_eventfile:
            del self.dict_eventfile[key_app]
    