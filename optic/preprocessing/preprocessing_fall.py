from __future__ import annotations
from ..type_definitions import *
import numpy as np

# preprocessing for Fall.mat data

# Fall.matをdict_Fallに変換
def convertMatToDictFall(Fall) -> Dict[str, Any]:
    Fall_stat = Fall["stat"]
    Fall_iscell = Fall["iscell"][:,0]
    
    dict_Fall_stat = {}

    list_ROI = []

    for cellid in range(len(Fall_iscell)):
        dict_Fall_stat_cell = {key:value for key, value in zip(Fall_stat[0][cellid][0].dtype.fields, Fall_stat[0][cellid][0][0])}
        # flatten
        for key, value in dict_Fall_stat_cell.items():
            dict_Fall_stat_cell[key] = value.flatten()
        xpix = dict_Fall_stat_cell["xpix"]
        ypix = dict_Fall_stat_cell["ypix"]
        center = (int(xpix.mean()), int(ypix.mean())) # ROIの中心
        dict_Fall_stat_cell["center"] = center
        dict_Fall_stat_cell["med"] = dict_Fall_stat_cell["med"][::-1] # yx -> xy
        dict_Fall_stat[cellid] = dict_Fall_stat_cell
        
    Fall_ops = Fall["ops"]
    dict_Fall_ops = {key: value for key, value in zip(Fall_ops[0].dtype.fields, Fall_ops[0][0])}

    dict_Fall = {"stat": dict_Fall_stat, "F": Fall["F"], "Fneu": Fall["Fneu"], "spks": Fall["spks"], "ops": dict_Fall_ops, "iscell": Fall["iscell"]}

    # add chan2 data
    if dict_Fall_ops["nchannels"].flatten()[0] == 2:
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
def getROICoordsFromDictFall(dict_Fall: Dict[str, Any]) -> Dict[int, Dict[Literal["xpix", "ypix"], np.ndarray[np.int32], Tuple[int]]]:
    dict_roi_coords = {}
    for roi_id in dict_Fall["stat"].keys():
        xpix = dict_Fall["stat"][roi_id]["xpix"]
        ypix = dict_Fall["stat"][roi_id]["ypix"]
        dict_roi_coords[roi_id] = {"xpix": xpix, "ypix": ypix}
    return dict_roi_coords