from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict
import numpy as np
from ..preprocessing.preprocessing_image import getBGImageFromFall, getBGImageChannel2FromFall, getROIImageFromFall, getBGImageFromCaimanHDF5
from ..preprocessing.preprocessing_fall import getROICoordsFromDictFall
from ..config.constants import Extension, ImportPackages
from ..io.data_io import loadFallMat, loadCaimanHDF5, loadTiffStack, loadTifImage
from ..utils.custom_dict import CustomDict

from typing import TYPE_CHECKING
if TYPE_CHECKING: # for type checking
    from itk.elxParameterObjectPython import elastixParameterObject, mapstringvectorstring
    from roifile import ImagejRoi

class DataManager:
    def __init__(self):
        self.dict_data_dtype:           Dict[AppKeys, str] = {}
        self.dict_Fall:                 Dict[AppKeys, Any] = {}
        self.dict_tiff:                 Dict[AppKeys, np.ndarray[Tuple[int, int, int, int, int]]] = {}
        self.dict_tiff_metadata:        Dict[AppKeys, Dict[str, Any]] = {}
        self.dict_tiff_reg:             Dict[AppKeys, np.ndarray[Tuple[int, int, int, int, int]]] = {}

        # ROI celltype
        self.dict_roi_celltype:         Dict[AppKeys, Dict[str, str]] = {}
        # ROI coordinates (key changed from int to str)
        self.dict_roi_coords:           Dict[AppKeys, Dict[str, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = {}
        self.dict_roi_coords_reg:       Dict[AppKeys, Dict[str, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]] = {}
        # background image
        self.dict_im_bg:                Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_chan2:          Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_optional:       Dict[AppKeys, np.ndarray[np.uint8, Tuple[int, int]]] = defaultdict(dict)
        # for ROI tracking
        self.dict_im_bg_reg:            Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_bg_chan2_reg:      Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        # ROI image
        self.dict_im_roi:               Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        self.dict_im_roi_reg:           Dict[AppKeys, Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]] = defaultdict(dict)
        # ROI mask, coordinates
        self.dict_roi_mask:             Dict[AppKeys, np.ndarray[np.uint16, Tuple[int, int, int]]] = {}
        self.dict_roi_mask_reg:         Dict[AppKeys, np.ndarray[np.uint16, Tuple[int, int, int]]] = {}
        # Elastix
        self.dict_parameter_map:        Dict[AppKeys, mapstringvectorstring] = {}
        self.dict_transform_parameters: Dict[AppKeys, elastixParameterObject] = {}
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
        # Cascade
        self.dict_cascade:              Dict[AppKeys, Dict[str, np.ndarray[Tuple[int]]]] = defaultdict(dict)

        self.dict_eventfile:            Dict[AppKeys, Dict[str, np.ndarray[Tuple[int]]]] = defaultdict(dict)
        self.dict_roicheck:             Dict[AppKeys, Any] = {}

        # For second Fall.mat support
        self.dict_n_rois_chan1:         Dict[AppKeys, int] = {}
        self.dict_has_second_fall:      Dict[AppKeys, bool] = {}

    """
    IO Functions
    """
    # load Fall.mat data
    def loadFallMat(self, app_key: AppKeys, path_fall: str, preprocessing: bool=True, config_manager: ConfigManager=None) -> Tuple[bool, Optional[Exception]]:
        try:
            dict_Fall = loadFallMat(path_fall)
            self.dict_Fall[app_key] = dict_Fall
            self.dict_data_dtype[app_key] = Extension.MAT
            self.dict_im_bg[app_key] = getBGImageFromFall(self, app_key)
            self.dict_roi_coords[app_key] = self._convertRoiCoordsKeysToStr(getROICoordsFromDictFall(dict_Fall))
            self.dict_im_roi[app_key] = getROIImageFromFall(self, app_key)
            
            # Initialize second Fall.mat attributes
            self.dict_n_rois_chan1[app_key] = len(dict_Fall["stat"])
            self.dict_has_second_fall[app_key] = False
            
            if self.getNChannels(app_key) == 2:
                self.dict_im_bg_chan2[app_key] = getBGImageChannel2FromFall(self, app_key)
            # Suite2pROITracking add registered data dict
            if config_manager:
                if config_manager.current_app == "SUITE2P_ROI_TRACKING" or config_manager.current_app == "CHECK_MULTI_SESSION_ROI_COORDINATES":
                    self.dict_im_bg_reg[app_key] = getBGImageFromFall(self, app_key)
                    self.dict_roi_coords_reg[app_key] = self._convertRoiCoordsKeysToStr(getROICoordsFromDictFall(dict_Fall))
                    self.dict_im_roi_reg[app_key] = getROIImageFromFall(self, app_key)
                    if self.getNChannels(app_key) == 2:
                        self.dict_im_bg_chan2_reg[app_key] = getBGImageChannel2FromFall(self, app_key)
            return True, None
        except Exception as e:
            # raise e
            return False, e
    
    # load second Fall.mat data and merge with existing data
    def loadFallMatChan2(self, app_key: AppKeys, path_fall_chan2: str, config_manager: ConfigManager=None) -> Tuple[bool, Optional[Exception]]:
        """
        Load second Fall.mat and merge with existing chan1 data.
        Must be called after loadFallMat.
        
        Args:
            app_key: Application key
            path_fall_chan2: Path to second Fall.mat file
            config_manager: Config manager (optional)
        
        Returns:
            Tuple of (success, exception)
        """
        try:
            dict_Fall_chan2 = loadFallMat(path_fall_chan2)
            
            # Get number of ROIs in first Fall.mat
            n_rois_chan1 = self.dict_n_rois_chan1[app_key]
            n_rois_chan2 = len(dict_Fall_chan2["stat"])
            
            # Merge trace data (F, Fneu, spks)
            self.dict_Fall[app_key]["F"] = np.concatenate([
                self.dict_Fall[app_key]["F"],
                dict_Fall_chan2["F"]
            ], axis=0)
            self.dict_Fall[app_key]["Fneu"] = np.concatenate([
                self.dict_Fall[app_key]["Fneu"],
                dict_Fall_chan2["Fneu"]
            ], axis=0)
            self.dict_Fall[app_key]["spks"] = np.concatenate([
                self.dict_Fall[app_key]["spks"],
                dict_Fall_chan2["spks"]
            ], axis=0)
            
            # Merge iscell
            self.dict_Fall[app_key]["iscell"] = np.concatenate([
                self.dict_Fall[app_key]["iscell"],
                dict_Fall_chan2["iscell"]
            ], axis=0)
            
            # Merge F_chan2, Fneu_chan2 if both have 2 channels
            if self.getNChannels(app_key) == 2 and dict_Fall_chan2["ops"]["nchannels"] == 2:
                self.dict_Fall[app_key]["F_chan2"] = np.concatenate([
                    self.dict_Fall[app_key]["F_chan2"],
                    dict_Fall_chan2["F_chan2"]
                ], axis=0)
                self.dict_Fall[app_key]["Fneu_chan2"] = np.concatenate([
                    self.dict_Fall[app_key]["Fneu_chan2"],
                    dict_Fall_chan2["Fneu_chan2"]
                ], axis=0)
            
            # Merge stat with string keys
            for i, stat_data in dict_Fall_chan2["stat"].items():
                new_key = f"{i}_chan2"
                self.dict_Fall[app_key]["stat"][new_key] = stat_data
            
            # Merge ROI coordinates with string keys
            dict_roi_coords_chan2 = getROICoordsFromDictFall(dict_Fall_chan2)
            for roi_id, coords in dict_roi_coords_chan2.items():
                new_key = f"{roi_id}_chan2"
                self.dict_roi_coords[app_key][new_key] = coords
            
            # Update ROI image
            self.dict_im_roi[app_key] = getROIImageFromFall(self, app_key)
            
            # Mark that second Fall.mat exists
            self.dict_has_second_fall[app_key] = True
            
            # Suite2pROITracking add registered data dict
            if config_manager:
                if config_manager.current_app == "SUITE2P_ROI_TRACKING" or config_manager.current_app == "CHECK_MULTI_SESSION_ROI_COORDINATES":
                    for roi_id, coords in dict_roi_coords_chan2.items():
                        new_key = f"{roi_id}_chan2"
                        self.dict_roi_coords_reg[app_key][new_key] = coords
                    self.dict_im_roi_reg[app_key] = getROIImageFromFall(self, app_key)
            
            return True, None
        except Exception as e:
            return False, e
        
    # load Caiman HDF5 data
    def loadCaimanHDF5(self, app_key: AppKeys, path_hdf5: str, config_manager: ConfigManager=None, threshold_ratio: float=0.2) -> Tuple[bool, Optional[Exception]]:
        try:
            dict_Fall = loadCaimanHDF5(path_hdf5)
            self.dict_Fall[app_key] = dict_Fall
            self.dict_data_dtype[app_key] = Extension.HDF5
            self.dict_im_bg[app_key] = getBGImageFromCaimanHDF5(self, app_key)
            self.dict_roi_coords[app_key] = self._convertRoiCoordsKeysToStr(getROICoordsFromDictFall(dict_Fall))
            self.dict_im_roi[app_key] = getROIImageFromFall(self, app_key)
            
            # Initialize second Fall.mat attributes (no second file for HDF5)
            self.dict_n_rois_chan1[app_key] = len(dict_Fall["stat"])
            self.dict_has_second_fall[app_key] = False
            
            # Suite2pROITracking add registered data dict
            if config_manager:
                if config_manager.current_app == "SUITE2P_ROI_TRACKING":
                    self.dict_im_bg_reg[app_key] = getBGImageFromCaimanHDF5(self, app_key)
                    self.dict_roi_coords_reg[app_key] = self._convertRoiCoordsKeysToStr(getROICoordsFromDictFall(dict_Fall))
                    self.dict_im_roi_reg[app_key] = getROIImageFromFall(self, app_key)
            return True, None
        except Exception as e:
            raise e
            # return False, e
        
    # load tiff image data (for optional)
    def loadTifImage(self, app_key: AppKeys, path_image: str) -> Tuple[bool, Optional[Exception]]:
        try:
            self.dict_im_bg_optional[app_key] = loadTifImage(path_image)
            return True, None
        except Exception as e:
            return False, e
        
    # load tiff stack data
    def loadTiffStack(self, app_key: AppKeys, path_tiff: str) -> Tuple[bool, Optional[Exception]]:
        try:
            tiff, metadata = loadTiffStack(path_tiff)
            self.dict_data_dtype[app_key] = Extension.TIFF
            self.dict_tiff[app_key] = tiff
            self.dict_tiff_metadata[app_key] = metadata
            self.dict_tiff_reg[app_key] = tiff
            return True, None
        except Exception as e:
            return False, e
        
    # load calcium trace npy data
    def loadNpyCalciumTrace(self, app_key: AppKeys, path_npy: str) -> Tuple[bool, Optional[Exception]]:
        try:
            self.dict_data_dtype[app_key] = Extension.NPY
            # apply to Fall data structure
            arr_trace = np.load(path_npy, allow_pickle=True)
            self.dict_Fall[app_key] = {
                "F": arr_trace,
                "ops": {
                    "nchannels": 1,  # default to 1 channel
                }
            }
            # Initialize second Fall.mat attributes
            self.dict_n_rois_chan1[app_key] = arr_trace.shape[0]
            self.dict_has_second_fall[app_key] = False
            return True, None
        except Exception as e:
            return False, e

    """
    Helper Functions
    """
    def _convertRoiCoordsKeysToStr(self, dict_roi_coords: Dict[int, Any]) -> Dict[str, Any]:
        """
        Convert ROI coordinates dictionary keys from int to str.
        """
        return {str(k): v for k, v in dict_roi_coords.items()}

    """
    get Functions
    """
    "Fall data"
    def getDictFall(self, app_key: AppKeys) -> Dict[str, Any]:
        return self.dict_Fall[app_key]
    
    # get F, Fneu, spks
    def getTraces(self, app_key: AppKeys, n_channels: int=1) -> Dict[str, np.ndarray[np.float32]]: # 2d array
        # Fall.mat data
        if self.dict_data_dtype[app_key] == Extension.MAT: 
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"],
                "Fneu": self.dict_Fall[app_key]["Fneu"],
                "spks": self.dict_Fall[app_key]["spks"],
            }
            if n_channels == 2:
                dict_traces["F_chan2"] = self.dict_Fall[app_key]["F_chan2"]
                dict_traces["Fneu_chan2"] = self.dict_Fall[app_key]["Fneu_chan2"]
        # Caiman HDF5 data
        elif self.dict_data_dtype[app_key] == Extension.HDF5:
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"],
                "spks": self.dict_Fall[app_key]["spks"],
            }
        # calcium trace npy data
        elif self.dict_data_dtype[app_key] == Extension.NPY: 
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"],
            }
        return dict_traces
    
    def getTracesOfSelectedROI(self, app_key: AppKeys, roi_id: str, n_channels: int=1) -> Dict[str, np.ndarray[np.float32]]: # 1d array
        """
        Get traces for a selected ROI.
        
        Args:
            app_key: Application key
            roi_id: ROI ID as string (e.g., "0", "1", "0_chan2")
            n_channels: Number of channels
        
        Returns:
            Dictionary of trace arrays
        """
        from ..utils.roi_id_utils import roiIdToArrayIndex
        
        index = roiIdToArrayIndex(roi_id, self.getNROIsChan1(app_key))
        
        # Suite2p Fall.mat data
        if self.dict_data_dtype[app_key] == Extension.MAT:
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"][index],
                "Fneu": self.dict_Fall[app_key]["Fneu"][index],
                "spks": self.dict_Fall[app_key]["spks"][index]
            }
            if n_channels == 2:
                dict_traces["F_chan2"] = self.dict_Fall[app_key]["F_chan2"][index]
                dict_traces["Fneu_chan2"] = self.dict_Fall[app_key]["Fneu_chan2"][index]
        # Caiman HDF5 data
        elif self.dict_data_dtype[app_key] == Extension.HDF5:
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"][index],
                "spks": self.dict_Fall[app_key]["spks"][index]
            }        
        # calcium trace npy data
        elif self.dict_data_dtype[app_key] == Extension.NPY: 
            dict_traces = {
                "F": self.dict_Fall[app_key]["F"][index],
            }
        return dict_traces
    
    # get stat
    def getStat(self, app_key: AppKeys) -> Dict[str, Dict[str, Any]]:
        return self.dict_Fall[app_key]["stat"]
    # get fs
    def getFs(self, app_key: AppKeys) -> float:
        return self.dict_Fall[app_key]["ops"]["fs"]
    # get data length
    def getLengthOfData(self, app_key: AppKeys) -> int:
        if self.dict_data_dtype[app_key] == Extension.MAT:
            return len(self.dict_Fall[app_key]["ops"]["xoff1"])
        elif self.dict_data_dtype[app_key] == Extension.HDF5:
            return self.dict_Fall[app_key]["F"].shape[1]
        elif self.dict_data_dtype[app_key] == Extension.NPY:
            return self.dict_Fall[app_key]["F"].shape[1]
    # get nROIs
    def getNROIs(self, app_key: AppKeys) -> int:
        return len(self.dict_Fall[app_key]["stat"])
    # get nROIs with F 
    def getNROIswithF(self, app_key: AppKeys) -> int:
        return len(self.dict_Fall[app_key]["F"])
    # get nchannels
    def getNChannels(self, app_key: AppKeys) -> int:
        return self.dict_Fall[app_key]["ops"]["nchannels"]
    # get nROIs in first Fall.mat
    def getNROIsChan1(self, app_key: AppKeys) -> int:
        return self.dict_n_rois_chan1.get(app_key, self.getNROIs(app_key))
    # get whether second Fall.mat exists
    def getHasSecondFall(self, app_key: AppKeys) -> bool:
        return self.dict_has_second_fall.get(app_key, False)
    
    # get ROI celltype
    def getDictROICelltype(self, app_key: AppKeys, id_roi: str=None) -> Dict[str, str] | str:
        if not id_roi == None:
            return self.dict_roi_celltype.get(app_key).get(id_roi)
        return self.dict_roi_celltype.get(app_key)
    # get ROI coordinates
    def getDictROICoords(self, app_key: AppKeys) -> Dict[str, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
        return self.dict_roi_coords.get(app_key)
    def getDictROICoordsRegistered(self, app_key: AppKeys) -> Dict[str, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
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

    "ROI image"
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

    # Cascade
    def getCascadeSpikeProbability(self, app_key: AppKeys) -> np.ndarray[Tuple[int]]:
        return self.dict_cascade.get(app_key, {}).get("cascade_spike_prob", None)
    def getCascadeSpikeEvents(self, app_key: AppKeys) -> np.ndarray[Tuple[int]]:
        return self.dict_cascade.get(app_key, {}).get("cascade_spike_events", None)
    
    "Background image"
    def getDictBGImage(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg.get(app_key)
    def getDictBGImageOptional(self, app_key: AppKeys) -> np.ndarray[np.uint8, Tuple[int, int]]:
        return self.dict_im_bg_optional.get(app_key)
    def getDictBGImageChan2(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2.get(app_key)
    def getDictBGImageRegistered(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_reg.get(app_key)
    def getDictBGImageChan2Registered(self, app_key: AppKeys) -> Dict[str, np.ndarray[np.uint8, Tuple[int, int]]]:
        return self.dict_im_bg_chan2_reg.get(app_key)
    
    def getImageSize(self, app_key: AppKeys) -> Tuple[int, int]:
        return self.dict_im_bg[app_key]["meanImg"].shape