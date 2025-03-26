from __future__ import annotations
from ..type_definitions import *
import datetime
import numpy as np
from PyQt5.QtCore import Qt

# convert contents of QTableWidget into dict_roicheck
def convertTableDataToDictROICheck(
        q_table: QTableWidget, 
        table_columns: TableColumns, 
        local_var: bool=False
        ) -> Dict[str, Any]:
    if local_var:
        from ..config.constants_local import ROICheckMatKeysLocal
        cell_type_keys = ROICheckMatKeysLocal.cell_type_keys # local variables
    
    dict_roicheck = {}
    row_count = q_table.rowCount()
    # process each column
    for col_name, col_info in table_columns.getColumns().items():
        if col_info['type'] == 'celltype':
            selected_rows = []
            for row in range(row_count):
                radio_button = q_table.cellWidget(row, col_info['order'])
                if radio_button and radio_button.isChecked():
                    selected_rows.append([row])

            dict_roicheck[col_name] = np.array(selected_rows, dtype=np.int32)

            if local_var:
                if col_name in cell_type_keys:
                    dict_roicheck[cell_type_keys[col_name]] = np.array(selected_rows, dtype=np.int32)
        
        elif col_info['type'] == 'checkbox':
            dict_roicheck[col_name] = np.zeros((row_count, 1), dtype=np.bool_)
            for row in range(row_count):
                item = q_table.item(row, col_info['order'])
                dict_roicheck[col_name][row] = item.checkState() == Qt.Checked if item else False
        
        elif col_info['type'] == 'string':
            dict_roicheck[col_name] = np.empty((row_count, 1), dtype=object)
            for row in range(row_count):
                item = q_table.item(row, col_info['order'])
                dict_roicheck[col_name][row] = item.text() if item else ''

    return dict_roicheck

# dict_roicheck -> mat_roicheck
def convertDictROICheckToMatROICheck(
        dict_roicheck   : Dict[str, Any], 
        mat_roicheck    : Dict[str, Any]=None, 
        date            : str="",
        user            : str="",
        n_roi           : int=0, 
        path_fall       : str=""
        )-> Dict[str, Any]:

    if mat_roicheck is None:
        mat_roicheck = {
            "NumberOfROI": n_roi,
            "path_Fall": path_fall,
            "name_Fall": path_fall.split("/")[-1],
            "manualROIcheck": {},
        }
    else:
        if path_fall: # rewrite Fall.mat path
            mat_roicheck["path_Fall"] = path_fall
            mat_roicheck["name_Fall"] = path_fall.split("/")[-1]

    mat_roicheck["manualROIcheck"][date] = {
        "user": user,
        **dict_roicheck,
    }

    return mat_roicheck

# mat_roicheck -> dict_roicheck
def convertMatROICheckToDictROICheck(mat_roicheck: Dict[str, Any]) -> Dict[str, Any]:
    mat_roicheck = mat_roicheck["manualROIcheck"]
    mat_dtype = list(mat_roicheck[0].dtype.fields)
    dict_roicheck = {}
    for key_, value_ in zip(mat_dtype, list(mat_roicheck[0][0])):
        if value_.dtype=="object":
            value_ = np.array([[x[0].item() if x[0].size > 0 else ""] for x in value_])
        dict_roicheck[key_] = value_
    return dict_roicheck

# convert contents of QTableWidget into dict_roitracking
def convertTableDataToDictROITracking(
        q_table_pri: QTableWidget, 
        q_table_sec: QTableWidget, 
        table_columns: TableColumns, 
        local_var: bool=False
        ) -> Dict[str, np.ndarray]:
    # celltype, checkbox, string
    dict_roi_tracking = convertTableDataToDictROICheck(q_table_pri, table_columns, local_var)
    row_count_pri = q_table_pri.rowCount()
    row_count_sec = q_table_sec.rowCount()
    for col_name, col_info in table_columns.getColumns().items():        
        # Cell ID
        if col_info['type'] == 'id':
            values = []
            for row in range(row_count_pri):
                item = q_table_pri.item(row, col_info['order'])
                value = int(item.text()) if item else np.nan
                values.append([value])
            dict_roi_tracking[col_name] = np.array(values)
        # Cell ID Match
        elif col_info['type'] == 'id_match':
            values = []
            for row in range(row_count_pri):
                item = q_table_pri.item(row, col_info['order'])
                try:
                    value = int(item.text()) if item else np.nan
                    if value >= 0 and value < row_count_sec: # check if the value is valid
                        values.append([value])
                    else:
                        values.append([np.nan])
                except (ValueError, AttributeError):
                    values.append([np.nan])
            dict_roi_tracking[col_name] = np.array(values)
    return dict_roi_tracking

# dict_roitracking -> mat_roitracking
def convertDictROITrackingToMatROITracking(
        dict_roi_tracking_pri : Dict[str, Any], 
        dict_roi_check_sec    : Dict[str, Any],
        mat_roi_tracking      : Dict[str, Any]=None, 
        date                  : str="",
        user                  : str="",
        n_roi_pri             : int=0, 
        n_roi_sec             : int=0,
        path_fall_pri         : str="",
        path_fall_sec         : str="",
        )-> Dict[str, Any]:

    if mat_roi_tracking is None:
        mat_roi_tracking = {
            "NumberOfROI_pri": n_roi_pri,
            "NumberOfROI_sec": n_roi_sec,
            "path_Fall_pri": path_fall_pri,
            "path_Fall_sec": path_fall_sec,
            "name_Fall_pri": path_fall_pri.split("/")[-1],
            "name_Fall_sec": path_fall_sec.split("/")[-1],
            "ROITracking": {},
        }
    else: # rewrite Fall.mat path
        if path_fall_pri:
            mat_roi_tracking["path_Fall_pri"] = path_fall_pri
            mat_roi_tracking["name_Fall_pri"] = path_fall_pri.split("/")[-1]
        if path_fall_sec:
            mat_roi_tracking["path_Fall_sec"] = path_fall_sec
            mat_roi_tracking["name_Fall_sec"] = path_fall_sec.split("/")[-1]    

    mat_roi_tracking["ROITracking"][date] = {
        **{"user": user},
        **{"pri": dict_roi_tracking_pri},
        **{"sec": dict_roi_check_sec}
    }

    return mat_roi_tracking


"""
Save Microglia Tracking
"""
# convert dict_roi_matching and dict_roi_coords_xyct to save appropriately as .mat file
"""
-- WARNING --
With savemat, if the key of dict is number (ex. 0, 1, 2, ...), the value convert to empty automatically.
To prevent this, convert contents of dict to array.
"""
# convert dict_roi_coords to arr_roi_coords for saving as mat file
def convertDictROICoordsToArrayROICoords(dict_roi_coords: Dict[int, Dict[Literal["x", "y", "med"], np.ndarray]]) -> np.ndarray:
    arr_roi_coords = []

    idx_roi_max = max(dict_roi_coords.keys())
    for idx_roi in range(idx_roi_max + 1): # check ROIs
        try:
            dict_roi_coords_roi = dict_roi_coords[idx_roi]
            arr_roi_coords.append(dict_roi_coords_roi)
        except KeyError: # if dict_roi_coords does not have {idx_roi} key
            arr_roi_coords.append(np.array([]))

    arr_roi_coords = np.array(arr_roi_coords, dtype=object)
    return arr_roi_coords

# multi t-plane
# convert dict_roi_coords_xyct to arr_roi_coords_xyct for saving as mat file
def convertDictROICoordsXYCTToArrayROICoordsXYCT(dict_roi_coords_xyct: Dict[int, Dict[int, Dict[Literal["x", "y", "med"], np.ndarray]]]) -> np.ndarray:
    arr_roi_coords_xyct = []
    for t_plane in dict_roi_coords_xyct.keys():
        try:
            dict_roi_coords = dict_roi_coords_xyct[t_plane]
            arr_roi_coords_xyct.append(convertDictROICoordsToArrayROICoords(dict_roi_coords))
        except ValueError: # no ROI in the plane
            arr_roi_coords_xyct.append(np.array([[]]))

    arr_roi_coords_xyct = np.array(arr_roi_coords_xyct, dtype=object)
    return arr_roi_coords_xyct

# dict_roi_matching["id"], dict_roi_matching["match"] -> arr_roi_matching_id, arr_roi_matching_match
def convertDictROIMathingToArrayROIMatching(dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]]) -> np.ndarray:
    arr_roi_matching_id = []
    arr_roi_matching_match = []
    for t_plane in dict_roi_matching["id"].keys():
        arr_roi_matching_id.append(dict_roi_matching["id"][t_plane])
    for t_plane_pri in dict_roi_matching["match"].keys():
        arr_roi_matching_match_pri = []
        for t_plane_sec in dict_roi_matching["match"][t_plane_pri].keys():
            try:
                idx_roi_pri_max = max(dict_roi_matching["match"][t_plane_pri][t_plane_sec].keys())
                arr_roi_matching_match_pri_sec = []
                for idx_roi_pri in range(idx_roi_pri_max + 1): # check ROIs 
                    try:
                        if dict_roi_matching["match"][t_plane_pri][t_plane_sec][idx_roi_pri] == None:
                            # To distinguish ROI itself is empty or match ROI number is empty, 
                            # set -1 for the latter case
                            arr_roi_matching_match_pri_sec.append(-1)
                        else:
                            arr_roi_matching_match_pri_sec.append(dict_roi_matching["match"][t_plane_pri][t_plane_sec][idx_roi_pri])
                    except KeyError: # check the ROI number is empty or not. ex) 0, 1, 2, 4, 6, 7, 8, ...
                        arr_roi_matching_match_pri_sec.append(np.array([]))
                arr_roi_matching_match_pri.append(np.array(arr_roi_matching_match_pri_sec, dtype=object))
            except ValueError: # no ROI in the plane
                arr_roi_matching_match_pri.append(np.array([[]]))
        arr_roi_matching_match.append(np.array(arr_roi_matching_match_pri, dtype=object))

    arr_roi_matching_id = np.array(arr_roi_matching_id, dtype=object)
    arr_roi_matching_match = np.array(arr_roi_matching_match, dtype=object)
    return arr_roi_matching_id, arr_roi_matching_match

# convert dict_roi_matching and dict_roi_coords_xyct to save appropriately as .mat file
def convertContentsOfDictROIMatchingAndDictROICoordsToArray(
    dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]],
    dict_roi_coords_xyct: Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]],
    dict_roi_coords_xyct_reg: Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]],
) -> Tuple[np.ndarray, Dict]:
    # dict_roi_coords_xyct -> arr_roi_coords_xyct
    arr_roi_coords_xyct = convertDictROICoordsXYCTToArrayROICoordsXYCT(dict_roi_coords_xyct)
    # dict_roi_coords_xyct_reg -> arr_roi_coords_xyct_reg
    arr_roi_coords_xyct_reg = convertDictROICoordsXYCTToArrayROICoordsXYCT(dict_roi_coords_xyct_reg)
    # dict_roi_matching["id"], dict_roi_matching["match"] -> arr_roi_matching_id, arr_roi_matching_match
    arr_roi_matching_id, arr_roi_matching_match = convertDictROIMathingToArrayROIMatching(dict_roi_matching)

    dict_roi_matching_converted = {"id": arr_roi_matching_id, "match": arr_roi_matching_match}
    return dict_roi_matching_converted, arr_roi_coords_xyct, arr_roi_coords_xyct_reg

# convert dict_roi_matching and dict_roi_coords_xyct to mat_microglia_tracking 
def convertDictROIMatchingAndDictROICoordsToMatMicrogliaTracking(
    dict_roi_matching       : Dict[str, Any], 
    dict_roi_coords_xyct    : Dict[str, Any], 
    dict_roi_coords_xyct_reg: Dict[str, Any],
    dict_tiff_reg           : Dict[str, Any],
    mat_microglia_tracking  : Dict[str, Any]=None, 
    date                    : str="",
    user                    : str="",
    path_tif                : str=""
)-> Dict[str, Any]:

    if mat_microglia_tracking is None:
        mat_microglia_tracking = {
            "path_tif": path_tif,
            "name_tif": path_tif.split("/")[-1],
            "ROI": {},
        }
    else:
        if path_tif: # rewrite tif file path
            mat_microglia_tracking["path_tif"] = path_tif
            mat_microglia_tracking["name_tif"] = path_tif.split("/")[-1]

    # convert dict_roi_matching and dict_roi_coords_xyct to appropriate format
    dict_roi_matching_converted, arr_roi_coords_xyct, arr_roi_coords_xyct_reg = convertContentsOfDictROIMatchingAndDictROICoordsToArray(
        dict_roi_matching, dict_roi_coords_xyct, dict_roi_coords_xyct_reg
    )
    mat_microglia_tracking["ROI"][date] = {
        "user": user,
        "ROITracking": dict_roi_matching_converted,
        "ROICoords": arr_roi_coords_xyct,
        "ROICoordsRegistered": arr_roi_coords_xyct_reg,
        "BGImageRegistered": dict_tiff_reg,
    }

    return mat_microglia_tracking

"""
Load Microglia Tracking
"""
# mat_microglia_tracking -> dict_roi_matching, dict_roi_coords_xyct
def convertMatMicrogliaTrackingToDictROIMatchingAndDictROICoords(
    mat_microglia_tracking: Dict[str, Any],
) -> Tuple[Dict[Literal["id", "match"], Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]], Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]], Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]]:
    mat_roi_matching = mat_microglia_tracking["ROITracking"]
    mat_roi_coords = mat_microglia_tracking["ROICoords"]
    mat_roi_coords_reg = mat_microglia_tracking["ROICoordsRegistered"]

    # convert dict_roi_matching for the GUI
    dict_roi_matching = convertMatROIMatchingToDictROIMatching(mat_roi_matching)
    # convert dict_roi_coords for the GUI
    dict_roi_coords_xyct = convertMatROICoordsXYCTToDictROICoordsXYCT(mat_roi_coords)
    # convert dict_roi_coords_reg for the GUI
    dict_roi_coords_xyct_reg = convertMatROICoordsXYCTToDictROICoordsXYCT(mat_roi_coords_reg)

    return dict_roi_matching, dict_roi_coords_xyct, dict_roi_coords_xyct_reg

# convert mat_roi_coords to dict_roi_coords
def convertMatROICoordsToDictROICoords(mat_roi_coords: Dict[int, Any]) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]:
    dict_roi_coords = {}
    for roi in range(len(mat_roi_coords)):
        if not isinstance(mat_roi_coords[roi], np.ndarray): # if roi itself is empty, the value is np.array([])
            dict_roi_coords[roi] = {}
            for fieldname in mat_roi_coords[roi]._fieldnames: # convert mat_struct to dict
                attr = getattr(mat_roi_coords[roi], fieldname)
                if fieldname in ["xpix", "ypix"] and isinstance(attr, int): # if npix of ROI is 1, the value is int
                    attr = np.array([attr]) # convert int to np.array
                dict_roi_coords[roi][fieldname] = attr
    return dict_roi_coords

# multi t_plane
# convert mat_roi_coords to dict_roi_coords
def convertMatROICoordsXYCTToDictROICoordsXYCT(mat_roi_coords_xyct: Dict[int, Dict[int, Any]]) -> Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]:
    dict_roi_coords_xyct = {}
    for t_plane in range(len(mat_roi_coords_xyct)):
        dict_roi_coords_xyct[t_plane] = convertMatROICoordsToDictROICoords(mat_roi_coords_xyct[t_plane])
    return dict_roi_coords_xyct

# convert mat_roi_matching to dict_roi_matching
def convertMatROIMatchingToDictROIMatching(mat_roi_matching: Dict[Literal["id", "match"], np.ndarray]) -> Dict[Literal["id", "match"], Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]]:
    dict_roi_matching_id = {t_plane: mat_roi_matching["id"][t_plane].tolist() for t_plane in range(len(mat_roi_matching["id"]))}
    dict_roi_matching_match = {}

    mat_roi_matching_match = mat_roi_matching["match"]
    # if the number of t_plane is only 2, the data shape is different
    if mat_roi_matching_match[0].ndim == 1:
        mat_roi_matching_match = np.array([mat_roi_matching_match])

    for t_plane_pri in range(len(mat_roi_matching_match)):
        dict_roi_matching_match[t_plane_pri] = {}
        mat_roi_matching_match_pri = mat_roi_matching_match[t_plane_pri]
        if mat_roi_matching_match_pri.ndim == 1: # length of last array is 1
            mat_roi_matching_match_pri = mat_roi_matching_match_pri.reshape(1, -1)
        for t_plane_sec in range(len(mat_roi_matching_match_pri)):
            dict_roi_matching_match[t_plane_pri][t_plane_sec + t_plane_pri + 1] = {}
            for roi_pri in range(len(mat_roi_matching_match_pri[t_plane_sec])):
                roi_sec = mat_roi_matching_match_pri[t_plane_sec][roi_pri]
                if isinstance(roi_sec, int): # if roi itself is empty, the valus is np.array([])
                    if roi_sec == -1: # if match roi id is None, the value is -1
                        roi_sec = None
                    dict_roi_matching_match[t_plane_pri][t_plane_sec + t_plane_pri + 1][roi_pri] = roi_sec
    dict_roi_matching = {"id": dict_roi_matching_id, "match": dict_roi_matching_match}
    return dict_roi_matching