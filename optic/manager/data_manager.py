from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict
import numpy as np
from itk.elxParameterObjectPython import elastixParameterObject, mapstringvectorstring
from roifile import ImagejRoi
from ..preprocessing.preprocessing_image import getBGImageFromFall, getBGImageChannel2FromFall, getROIImageFromFall
from ..preprocessing.preprocessing_fall import getROICoordsFromDictFall
from ..config.constants import Extension
from ..io.data_io import loadFallMat, loadTiffStack, loadTifImage
from ..utils.custom_dict import CustomDict

class DataManager:
    def __init__(self):
        self.dict_data_dtype:           Dict[AppKeys, str] = {}
        self.dict_Fall:                 Dict[AppKeys, Any] = {}
        self.dict_tiff:                 Dict[AppKeys, np.ndarray[Tuple[int, int, int, int, int]]] = {}
        self.dict_tiff_metadata:        Dict[AppKeys, Dict[str, Any]] = {}
        self.dict_tiff_reg:             Dict[AppKeys, np.ndarray[Tuple[int, int, int, int, int]]] = {}

        # ROI celltype
        self.dict_roi_celltype:         Dict[AppKeys, Dict[int, str]] = {}
        # ROI coordinates
        self.dict_roi_coords:           Dict[AppKeys, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = {}
        self.dict_roi_coords_reg:       Dict[AppKeys, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = {}
        # background image
        self.dict_im_bg:                Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_chan2:          Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_optional:       Dict[AppKeys, np.ndarray[np.uint8, Tuple[int, int]]] = defaultdict(dict)
        # for ROI tracking
        self.dict_im_bg_reg:            Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_chan2_reg:      Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        # Elastix
        self.dict_parameter_map:        Dict[AppKeys, mapstringvectorstring] = {}
        self.dict_transform_parameters: Dict[AppKeys, elastixParameterObject] = {}
        # ROI image
        self.dict_im_roi:               Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_roi_reg:           Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        # ROI mask, coordinates
        self.dict_roi_mask:             Dict[AppKeys, np.ndarray[np.uint16, Tuple[int, int, int]]] = {}
        self.dict_roi_mask_reg:         Dict[AppKeys, np.ndarray[np.uint16, Tuple[int, int, int]]] = {}
        # for ImageJ ROI Manager
        self.list_roi_imagej:           List[ImagejRoi] = []
        self.list_roi_imagej_reg:       List[ImagejRoi] = []
        # for MicrogliaTracking
        # ROI matching, XYCT
        self.dict_roi_matching:         Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]] = {"id": {}, "match": {}}
        self.dict_roi_coords_xyct:      Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = CustomDict()
        self.dict_roi_coords_xyct_reg:  Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = CustomDict()
        self.dict_im_roi_xyct:          Dict[int, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_roi_reg_xyct:      Dict[int, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)

        self.dict_eventfile:            Dict[AppKeys, Dict[str, np.ndarray[Tuple[int]]]] = defaultdict(dict)
        self.dict_roicheck:             Dict[AppKeys, Any] = {}

    """
    IO Functions
    """
    # load Fall.mat data
    def loadFallMat(self, app_key: AppKeys, path_fall: str, preprocessing: bool=True, config_manager: ConfigManager=None) -> bool:
        try:
            dict_Fall = loadFallMat(path_fall)
            self.dict_Fall[app_key] = dict_Fall
            self.dict_data_dtype[app_key] = Extension.MAT
            self.dict_im_bg[app_key] = getBGImageFromFall(self, app_key)
            self.dict_roi_coords[app_key] = getROICoordsFromDictFall(dict_Fall)
            self.dict_im_roi[app_key] = getROIImageFromFall(self, app_key)
            if self.getNChannels(app_key) == 2:
                self.dict_im_bg_chan2[app_key] = getBGImageChannel2FromFall(self, app_key)
            # Suite2pROITracking
            if config_manager:
                if config_manager.current_app == "SUITE2P_ROI_TRACKING":
                    self.dict_im_bg_reg[app_key] = getBGImageFromFall(self, app_key)
                    self.dict_roi_coords_reg[app_key] = getROICoordsFromDictFall(dict_Fall)
                    self.dict_im_roi_reg[app_key] = getROIImageFromFall(self, app_key)
                    if self.getNChannels(app_key) == 2:
                        self.dict_im_bg_chan2_reg[app_key] = getBGImageChannel2FromFall(self, app_key)
            return True
        except Exception as e:
            raise e
            return False
        
    # load tiff image data (for optional)
    def loadTifImage(self, app_key: AppKeys, path_image: str) -> bool:
        try:
            self.dict_im_bg_optional[app_key] = loadTifImage(path_image)
            return True
        except Exception as e:
            return False
        
    # load tiff stack data
    def loadTiffStack(self, app_key: AppKeys, path_tiff: str) -> bool:
        try:
            tiff, metadata = loadTiffStack(path_tiff)
            self.dict_data_dtype[app_key] = Extension.TIFF
            self.dict_tiff[app_key] = tiff
            self.dict_tiff_metadata[app_key] = metadata
            self.dict_tiff_reg[app_key] = tiff
            return True
        except Exception as e:
            return False
        
    # load calcium trace npy data
    def loadNpyCalciumTrace(self, app_key: AppKeys, path_npy: str) -> bool:
        try:
            # apply to Fall data structure
            arr_trace = np.load(path_npy, allow_pickle=True).item()
            self.dict_Fall[app_key] = {
                "F": arr_trace
            }
            return True
        except Exception as e:
            return False

    """
    get Functions
    """
    "Fall data"
    def getDictFall(self, app_key: AppKeys) -> Dict[str, Any]:
        return self.dict_Fall[app_key]
    
    # get F, Fneu, spks
    def getTraces(self, app_key: AppKeys, n_channels: int=1) -> Dict[str, np.ndarray[np.float32]]: # 2d array
        dict_traces = {
            "F": self.dict_Fall[app_key]["F"],
            "Fneu": self.dict_Fall[app_key]["Fneu"],
            "spks": self.dict_Fall[app_key]["spks"],
        }
        if n_channels == 2:
            dict_traces["F_chan2"] = self.dict_Fall[app_key]["F_chan2"]
            dict_traces["Fneu_chan2"] = self.dict_Fall[app_key]["Fneu_chan2"]
        return dict_traces
    def getTracesOfSelectedROI(self, app_key: AppKeys, roi_id: int, n_channels: int=1) -> Dict[str, np.ndarray[np.float32]]: # 1d array
        dict_traces = {
            "F": self.dict_Fall[app_key]["F"][roi_id],
            "Fneu": self.dict_Fall[app_key]["Fneu"][roi_id],
            "spks": self.dict_Fall[app_key]["spks"][roi_id]
        }
        if n_channels == 2:
            dict_traces["F_chan2"] = self.dict_Fall[app_key]["F_chan2"][roi_id]
            dict_traces["Fneu_chan2"] = self.dict_Fall[app_key]["Fneu_chan2"][roi_id]
        return dict_traces
    
    # get stat
    def getStat(self, app_key: AppKeys) -> Dict[int, Dict[str, Any]]:
        return self.dict_Fall[app_key]["stat"]
    # get fs
    def getFs(self, app_key: AppKeys) -> float:
        return self.dict_Fall[app_key]["ops"]["fs"]
    # get data length
    def getLengthOfData(self, app_key: AppKeys) -> int:
        if self.dict_data_dtype[app_key] == Extension.MAT:
            return len(self.dict_Fall[app_key]["ops"]["xoff1"])
    # get nROIs
    def getNROIs(self, app_key: AppKeys) -> int:
        return len(self.dict_Fall[app_key]["stat"])
    # get nchannels
    def getNChannels(self, app_key: AppKeys) -> int:
        return self.dict_Fall[app_key]["ops"]["nchannels"]
    
    # get ROI celltype
    def getDictROICelltype(self, app_key: AppKeys, id_roi: int=None) -> Dict[int, str] | str:
        if not id_roi == None:
            return self.dict_roi_celltype.get(app_key).get(id_roi)
        return self.dict_roi_celltype.get(app_key)
    # get ROI coordinates
    def getDictROICoords(self, app_key: AppKeys) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
        return self.dict_roi_coords.get(app_key)
    def getDictROICoordsRegistered(self, app_key: AppKeys) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
        return self.dict_roi_coords_reg.get(app_key)
        
    "Tiff data"
    def getTiffStack(self, app_key: AppKeys) -> np.ndarray[np.uint8, Tuple[int, int, int, int, int]]:
        return self.dict_tiff.get(app_key, None)
    def getTiffMetadata(self, app_key: AppKeys) -> Dict[str, Any]:
        return self.dict_tiff_metadata.get(app_key, None)
    def getTiffStackRegistered(self, app_key: AppKeys) -> np.ndarray[np.uint8, Tuple[int, int, int, int, int]]:
        return self.dict_tiff_reg.get(app_key, None)

    def getSizeOfX(self, app_key: AppKeys) -> int:
        return self.dict_tiff[app_key].shape[0]
    def getSizeOfY(self, app_key: AppKeys) -> int:
        return self.dict_tiff[app_key].shape[1]
    def getSizeOfC(self, app_key: AppKeys) -> int:
        return self.dict_tiff[app_key].shape[2]
    def getSizeOfZ(self, app_key: AppKeys) -> int:
        return self.dict_tiff[app_key].shape[3]
    def getSizeOfT(self, app_key: AppKeys) -> int:
        return self.dict_tiff[app_key].shape[4]

    # get attibutes
    def getDataType(self, app_key: AppKeys) -> str:
        return self.dict_data_dtype.get(app_key)
    
    def getDataTypeOfTiffStack(self, app_key: AppKeys) -> str:
        return self.dict_tiff[app_key].dtype

    # get image size, change return with dtype
    def getImageSize(self, app_key: AppKeys) -> Tuple[int, int]:
        if self.dict_data_dtype[app_key] == Extension.MAT:
            return (self.dict_Fall[app_key]["ops"]["Lx"], self.dict_Fall[app_key]["ops"]["Ly"])
        elif self.dict_data_dtype[app_key] == Extension.TIFF:
            return (self.dict_tiff[app_key].shape[0], self.dict_tiff[app_key].shape[1])
        
    def getImageFromXYCZTTiffStack(self, app_key: AppKeys, plane_z: int, plane_t: int, channel: int, get_reg: bool = False) -> np.ndarray[np.uint8, Tuple[int, int]]:
        # use registered image if get_reg is True
        if get_reg:
            img_stack = self.getTiffStackRegistered(app_key)
        else:
            img_stack = self.getTiffStack(app_key)
        try:
            return img_stack[:, :, channel, plane_z, plane_t]
        except IndexError:
            # out of index, return black image
            return np.zeros(img_stack.shape[:2], dtype=np.uint8)
    
    def getDictBackgroundImage(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]: # 2d array
        return self.dict_im_bg.get(app_key)
    
    def getDictBackgroundImageChannel2(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2.get(app_key)
    
    def getBackgroundImageOptional(self, app_key: AppKeys) -> np.ndarray[np.uint8, Tuple[int, int]]:
        return self.dict_im_bg_optional.get(app_key)
    
    def getDictBackgroundImageRegistered(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]: # 2d array
        return self.dict_im_bg_reg.get(app_key)
    
    def getDictBackgroundImageChannel2Registered(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2_reg.get(app_key)
    
    def getDictROIImage(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_roi.get(app_key)
    
    def getDictROIImageRegistered(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_roi_reg.get(app_key)
    
    def getROIMask(self, app_key: AppKeys) -> np.ndarray[np.uint16, Tuple[int, int, int]]:
        return self.dict_roi_mask.get(app_key)
    
    def getROIMaskRegistered(self, app_key: AppKeys) -> np.ndarray[np.uint16, Tuple[int, int, int]]:
        return self.dict_roi_mask_reg.get(app_key)
    
    def getDictROICoordsXYCT(self) -> Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]:
        return self.dict_roi_coords_xyct
    
    def getDictROICoordsXYCTRegistered(self) -> Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]:
        return self.dict_roi_coords_xyct_reg
    
    def getDictROIMatching(self) -> Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]]:
        return self.dict_roi_matching
    
    def getDictROIImageXYCT(self) -> Dict[int, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]]:
        return self.dict_im_roi_xyct
    
    def getDictROIImageRegisteredXYCT(self) -> Dict[int, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]]:
        return self.dict_im_roi_reg_xyct
    
    # Elastix
    def getParameterMap(self, app_key: AppKeys) -> mapstringvectorstring:
        return self.dict_parameter_map.get(app_key)
    def getTransformParameters(self, app_key: AppKeys) -> elastixParameterObject:
        return self.dict_transform_parameters.get(app_key)
    
    # eventfile
    def getDictEventfile(self, app_key: AppKeys) -> Dict[str, np.ndarray[Tuple[int]]]:
        return self.dict_eventfile.get(app_key)
    def clearDictEventfile(self, app_key: AppKeys, eventfile_name: str=None) -> None:
        if app_key in self.dict_eventfile:
            if eventfile_name and eventfile_name in self.dict_eventfile[app_key]:
                del self.dict_eventfile[app_key][eventfile_name]
            else:
                del self.dict_eventfile[app_key]
    