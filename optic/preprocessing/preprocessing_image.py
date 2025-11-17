from __future__ import annotations
from ..type_definitions import *
import numpy as np
from typing import Dict

# convert image dtype to uint8 or uint16
def convertImageDtypeToINT(
        img: np.ndarray, 
        dtype: str="uint8"
        ) -> np.ndarray:
    img = img.astype("float")
    img -= np.min(img)
    img /= np.max(img)
    img *= 255
    img = img.astype(dtype)
    return img

# resize image shape to target shape by centering
def resizeImageShape(
        img: np.ndarray, 
        shape_tgt: Tuple[int, int]
        ) -> np.ndarray:
    if img.shape == shape_tgt:
        return img
    new_img = np.zeros(shape_tgt, dtype=img.dtype)
    start_y = (shape_tgt[0] - img.shape[0]) // 2
    start_x = (shape_tgt[1] - img.shape[1]) // 2
    new_img[start_y:start_y+img.shape[0], start_x:start_x+img.shape[1]] = img
    return new_img

"""
preprocessing for Suite2p Fall.mat
"""
# get Background Images from Fall.mat
def getBGImageFromFall(
        data_manager: DataManager, 
        app_key: AppKeys, 
        dtype: str="uint8"
        ) -> Dict[str, np.ndarray]:
    # get image shape from meanImg
    from ..config.constants import BGImageTypeList
    dict_im_bg = {}
    base_shape = data_manager.dict_Fall[app_key]["ops"]["meanImg"].shape
    for key_im in BGImageTypeList.FALL:
        img = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"][key_im], dtype=dtype)
        img = resizeImageShape(img, base_shape)
        dict_im_bg[key_im] = img
    return dict_im_bg

# get chan2 Background Images from Fall.mat
# but chan2 background images are only "meanImg" and "meanImg corrected"
def getBGImageChannel2FromFall(
        data_manager: DataManager, 
        app_key: AppKeys, 
        dtype: str="uint8"
        ) -> Dict[str, np.ndarray]:
    # get image shape from meanImg
    dict_im_bg = {}
    dict_im_bg["meanImg"] = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"]["meanImg_chan2"], dtype=dtype)
    dict_im_bg["meanImg_corrected"] = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"]["meanImg_chan2_corrected"], dtype=dtype)
    return dict_im_bg

# make ROI Image from Fall.mat
def getROIImageFromFall(
        data_manager: DataManager, 
        app_key: AppKeys, 
        dtype: str="uint8", 
        value: int=50
        ) -> Dict[str, np.ndarray]:
    dict_im_roi = {}
    roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)
    for coords in data_manager.getDictROICoords(app_key).values():
        xpix, ypix = coords["xpix"], coords["ypix"]
        roi_img[ypix, xpix] = value
    dict_im_roi["all"] = roi_img
    return dict_im_roi

# make ROI Image from dict_roi_coords, Dict[roi_id, Dict["xpix", "ypix", "med"]]
def getROIImageFromDictROICoords(
        dict_roi_coords: Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]], 
        shape: Tuple[int, int],
        dtype: str="uint8", 
        value: int=50
        ) -> Dict[str, np.ndarray]:
    dict_im_roi = {}
    roi_img = np.zeros(shape, dtype=dtype)
    for coords in dict_roi_coords.values():
        xpix, ypix = coords["xpix"], coords["ypix"]
        roi_img[xpix, ypix] = value
    dict_im_roi["all"] = roi_img
    return dict_im_roi

# make dict_roi_im_xyct from dict_roi_coords_xyct, Dict[plane_t, Dict[roi_id, Dict["xpix", "ypix", "med"]]]
def getDictROIImageXYCTFromDictROICoords(
        dict_roi_coords_xyct: Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]], 
        shape: Tuple[int, int],
        dtype: str="uint8", 
        value: int=50
        ) -> Dict[str, np.ndarray]:
    dict_im_roi_xyct = {}
    for plane_t, dict_roi_coords in dict_roi_coords_xyct.items():
        dict_im_roi_xyct[plane_t] = getROIImageFromDictROICoords(dict_roi_coords, shape, dtype=dtype, value=value)
    return dict_im_roi_xyct

"""
preprocessing for Caiman HDF5
"""
# get Background Images from Caiman HDF5
def getBGImageFromCaimanHDF5(
        data_manager: DataManager, 
        app_key: AppKeys, 
        dtype: str="uint8"
        ) -> Dict[str, np.ndarray]:
    # get image shape from meanImg
    from ..config.constants import BGImageTypeList
    dict_im_bg = {}
    base_shape = data_manager.dict_Fall[app_key]["ops"]["meanImg"].shape
    for key_im in BGImageTypeList.CAIMAN:
        img = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"][key_im], dtype=dtype)
        img = resizeImageShape(img, base_shape)
        dict_im_bg[key_im] = img
    return dict_im_bg