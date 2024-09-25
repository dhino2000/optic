from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict
from scipy.io import loadmat
import numpy as np
from numpy.typing import NDArray
from ..preprocessing.preprocessing_fall import convertMatToDictFall
from ..preprocessing.preprocessing_image import getBGImageFromFall

class DataManager:
    def __init__(self):
        self.dict_Fall:                 Dict[str, Any] = {}
        self.dict_im_bg:           Dict[str, np.array] = defaultdict(dict)
        self.dict_im_bg_chan2:     Dict[str, np.array] = {}
        self.dict_eventfile:       Dict[str, np.array] = {}
        self.dict_roicheck:             Dict[str, Any] = {}

    # Fall.matの読み込み
    def loadFallMAT(self, key_app: str, path_fall: str, preprocessing: bool=True) -> bool:
        try:
            Fall = loadmat(path_fall)
            if preprocessing:
                dict_Fall = convertMatToDictFall(Fall)
                self.dict_Fall[key_app] = dict_Fall
                getBGImageFromFall(self, key_app, key_app)
            else:
                self.dict_Fall[key_app] = Fall
            return True
        except FileNotFoundError as e:
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
    
    # get fs
    def getFs(self, key_app: str) -> float:
        return self.dict_Fall[key_app]["ops"]["fs"].flatten()[0]

    # get data length
    def getLengthOfData(self, key_app: str) -> int:
        return len(self.dict_Fall[key_app]["ops"]["xoff1"])

    # get attibutes
    def getImageSize(self, key_app: str) -> Tuple[int, int]:
        return (self.dict_Fall[key_app]["ops"]["Lx"].item(), self.dict_Fall[key_app]["ops"]["Ly"].item())
    
    def getDictBackgroundImage(self, key_app: str) -> Dict[str, NDArray[np.uint8]]: # 2d array
        return self.dict_im_bg.get(key_app)
    
    def getBackgroundChan2Image(self, key_app: str) -> np.array:
        return self.dict_im_bg_chan2.get(key_app)
    
    def getEventfile(self, key_app: str) -> np.array:
        return self.dict_eventfile.get(key_app)
    
    # clear attributes
    def clearEventfile(self, key_app: str) -> None:
        if key_app in self.dict_eventfile:
            del self.dict_eventfile[key_app]
    