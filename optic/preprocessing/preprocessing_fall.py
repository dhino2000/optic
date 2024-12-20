from __future__ import annotations
from ..type_definitions import *
import numpy as np

# preprocessing for Fall.mat data

# convert Fall.mat to dict
def convertMatToDictFall(Fall: Dict[str, Any]) -> Dict[str, Any]:
    Fall_stat = Fall["stat"]
    
    dict_Fall_stat = {}
    for i, value in enumerate(Fall_stat):
        dict_Fall_stat[i] = value

    dict_Fall = {"stat": dict_Fall_stat, "F": Fall["F"], "Fneu": Fall["Fneu"], "spks": Fall["spks"], "ops": Fall["ops"], "iscell": Fall["iscell"]}

    # add chan2 data
    if Fall["ops"]["nchannels"] == 2:
        dict_Fall["F_chan2"] = Fall["F_chan2"]
        dict_Fall["Fneu_chan2"] = Fall["Fneu_chan2"]
        dict_Fall["redcell"] = Fall["redcell"]

    return dict_Fall

# ROICheckのmatを扱いやすいdictに変換
def convertMatToDictROICheck(mat):
    mat_dtype = list(mat[0].dtype.fields)
    dict_ = dict(zip(mat_dtype, list(mat[0][0])))
    return dict_

# get ROI coordination from dict_Fall
def getROICoordsFromDictFall(dict_Fall: Dict[str, Any]) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
    dict_roi_coords = {}
    for roi_id in dict_Fall["stat"].keys():
        xpix = dict_Fall["stat"][roi_id]["xpix"]
        ypix = dict_Fall["stat"][roi_id]["ypix"]
        med = dict_Fall["stat"][roi_id]["med"]
        dict_roi_coords[roi_id] = {"xpix": xpix, "ypix": ypix, "med": med}
    return dict_roi_coords

# concatenate bg_image and dict_roi_coords and export as FallLike.mat
def makeFallLikeFromBgImageAndDictROICoords(data_manager: DataManager) -> Dict[str, Any]:
    dict_roi_coords = data_manager.getDictROICoords("pri")
    img_bg = data_manager.getTiffStack("pri")[:, :, 0, 0, 0]

    Falllike = {
        "stat": {},
        "ops": {},
        "F": np.array([]),
        "Fneu": np.array([]),
        "spks": np.array([]),
        "iscell": np.array([]),
        "redcell": np.array([]),
        "F_chan2": np.array([]),
        "Fneu_chan2": np.array([]),
        "spks_chan2": np.array([]),
    }

    nROIs = len(dict_roi_coords)

    Falllike["iscell"] = np.zeros((nROIs, 2))
    Falllike["stat"] = [v for v in dict_roi_coords.values()]
    Falllike["ops"]["Lx"] = img_bg.shape[0]
    Falllike["ops"]["Ly"] = img_bg.shape[1]
    Falllike["ops"]["nchannels"] = 1
    Falllike["ops"]["nplanes"] = 1
    Falllike["ops"]["xoff1"] = np.zeros((100, 10)) # no meaning
    Falllike["ops"]["meanImg"] = img_bg
    Falllike["ops"]["meanImgE"] = img_bg
    Falllike["ops"]["max_proj"] = img_bg
    Falllike["ops"]["Vcorr"] = img_bg

    return Falllike