from __future__ import annotations
from ..type_definitions import *
import numpy as np
from ..config.constants import BGImageTypeList
from typing import Dict

# 画像をint型に変換 型は指定可能
def convertImageDtypeToINT(img, dtype="uint8") -> np.ndarray:
    img = img.astype("float")
    img -= np.min(img)
    img /= np.max(img)
    img *= 255
    img = img.astype(dtype)
    return img

# 大きさが異なる画像をそろえる, max_proj, Vcorr用
def resizeImageShape(img, shape_tgt) -> np.ndarray:
    if img.shape == shape_tgt:
        return img
    # 新しい黒い画像を作成
    new_img = np.zeros(shape_tgt, dtype=img.dtype)
    # 中央に配置するための開始位置を計算
    start_y = (shape_tgt[0] - img.shape[0]) // 2
    start_x = (shape_tgt[1] - img.shape[1]) // 2
    # 小さい画像を中央に配置
    new_img[start_y:start_y+img.shape[0], start_x:start_x+img.shape[1]] = img
    return new_img

# get Background Images from Fall.mat
def getBGImageFromFall(data_manager: DataManager, app_key: str, dtype: str="uint8") -> Dict[str, np.ndarray]:
    # get image shape from meanImg
    dict_im_bg = {}
    base_shape = data_manager.dict_Fall[app_key]["ops"]["meanImg"].shape
    for key_im in BGImageTypeList.FALL:
        img = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"][key_im], dtype=dtype)
        img = resizeImageShape(img, base_shape)
        dict_im_bg[key_im] = img
    return dict_im_bg

# get chan2 Background Images from Fall.mat
# but chan2 background images are only "meanImg" and "meanImg corrected"
def getBGImageChannel2FromFall(data_manager: DataManager, app_key: str, dtype: str="uint8") -> Dict[str, np.ndarray]:
    # get image shape from meanImg
    dict_im_bg = {}
    dict_im_bg["meanImg"] = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"]["meanImg_chan2"], dtype=dtype)
    dict_im_bg["meanImg_corrected"] = convertImageDtypeToINT(data_manager.dict_Fall[app_key]["ops"]["meanImg_chan2_corrected"], dtype=dtype)
    return dict_im_bg

# make ROI Image from Fall.mat
def getROIImageFromFall(data_manager: DataManager, app_key: str, dtype: str="uint8", value: int=50) -> np.ndarray:
    roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)
    for roiId, roiStat in data_manager.getStat(app_key).items():
        xpix, ypix = roiStat["xpix"], roiStat["ypix"]
        roi_img[ypix, xpix] = value
    return roi_img