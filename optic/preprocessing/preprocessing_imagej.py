from __future__ import annotations
from ..type_definitions import *
from .preprocessing_roi import getROIContour, convertROIContourToFilled
from typing import Tuple, Dict, List, Optional, Literal
from roifile import ImagejRoi
import numpy as np
import cv2
import re


"""
Read Functions
"""

# convert imageJ roi.zip to dict_roi_coords_xyct, dict_roi_matching
"""
ROI format of roi.zip is XYCZT, convert to XYCT format

dict_roi_matching: initialized dict_roi_matching
dict_roi_coords_xyct: initialized dict_roi_coords_xyct
"""
def convertImagejRoiToDictROIMatchingAndDictROICoords(
        rois: List[ImagejRoi],
        dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]],
        dict_roi_coords_xyct: Dict[int, Dict],
        img_width: int,
        img_height: int
    ) -> Tuple[Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]], 
               Dict[int, Dict[int, Dict[Literal["x", "y", "med"], np.ndarray]]]]:
    """
    TEMPORARY WARNING !!!
    """
    dict_error = {}

    # anchor dict for dict_roi_matching["match"]
    # ex) {"m001": {0: 1, 1: 2, 2: 4, 3: 2}, "m002": {0: 3, 1: 4, 2: 5, 3: 6}}
    dict_roi_matching_anchor: Dict[str, Dict[int, int]] = {}

    # some roi.name are duplicated, so check and skip duplicated roi
    list_roi_name = [roi.name for roi in rois]
    list_duplicate_roi_name = [name for name in list_roi_name if list_roi_name.count(name) > 1]

    # get roi_matching["id"] and roi_coords_xyct
    for i, roi in enumerate(rois):
        # skip duplicated roi
        if roi.name in list_duplicate_roi_name:
            print("ROI load error: ", roi.name)
            print("DUPLICATED")
            dict_error[roi.name] = "DUPLICATED"
            continue
        roi_name = roi.name # MXXX_SXX
        roi_name = roi_name.replace(" ", "") # remove space
        roi_name = roi_name.upper() # mXXX_sXX -> MXXX_SXX
        roi_name = roi_name.replace("-", "_") # MXXX-SXX -> MXXX_SXX

        # only FREEHAND roi !
        if roi.roitype == 7 or roi.roitype == 8:
            try:
                roi_x_start = roi.left
                roi_y_start = roi.top
                roi_xy_coords = roi.integer_coordinates

                xpix_contour = roi_xy_coords[:, 0] + roi_x_start
                ypix_contour = roi_xy_coords[:, 1] + roi_y_start
                xpix_ypix_contour = np.column_stack((xpix_contour, ypix_contour))
                # convert contour to filled roi
                xpix_ypix = convertROIContourToFilled(xpix_ypix_contour, img_width, img_height)
                xpix, ypix = xpix_ypix[:, 0], xpix_ypix[:, 1]

                med = np.array([np.median(xpix).astype("uint16"), np.median(ypix).astype("uint16")])

                roi_z_plane = roi.z_position - 1
                roi_t_plane = roi.t_position - 1
                
                """
                WARNING !!!
                Current roi naming rule is "mXXX_sXX" or "MXXX_SXX", m,M : ROI ID, s,S : t_plane number
                But, this rule is not always correct.
                """
                # if naming rule is not correct, skip
                # MXXX_SXX
                if not re.match(r'^M\d+_S\d+$', roi_name):
                    print("ROI load error: ", roi.name)
                    print("WRONG NAMING")
                    dict_error[roi.name] = "WRONG NAMING"
                    continue
                        
                if not int(roi_name.split("_")[1].split("S")[1]) == roi_t_plane + 1:
                    print("ROI load error: ", roi.name)
                    print("WRONG NAMING AND WRONG T_PLANE")
                    dict_error[roi.name] = "WRONG NAMING AND WRONG T_PLANE"
                    continue

                name = roi_name.split("_")[0]
                roi_id = int(name.split("M")[1]) - 1
                
                # Some ROI's z_position and t_position are 0, it's not correct.
                if roi.t_position == 0:
                    print("ROI load error: ", roi.name)
                    print("NOT CONTAIN t_position")
                    dict_error[roi.name] = "NOT CONTAIN t_position"
                    continue
                
                dict_roi_matching["id"][roi_t_plane].append(roi_id)
                dict_roi_coords_xyct[roi_t_plane][roi_id] = {
                    "xpix": xpix,
                    "ypix": ypix,
                    "med": med,
                }

                # store roi name, t_plane number and roi_id
                if name not in dict_roi_matching_anchor:
                    dict_roi_matching_anchor[name] = {}
                dict_roi_matching_anchor[name][roi_t_plane] = roi_id
            except IndexError:
                print("ROI load error: ", roi.name)
                print("INDEX ERROR")
                dict_error[roi.name] = "INDEX ERROR"
        else:
            print("ROI load error: ", roi.name)
            print(f"INVALID ROI TYPE {roi.roitype.name}")
            dict_error[roi.name] = f"INVALID ROI TYPE {roi.roitype.name}"

    """
    TEMPORARY WARNING !!!
    """
    import pandas as pd
    df_error = pd.DataFrame(dict_error.items(), columns=["roi_name", "error"])
    df_error.to_csv("ROIManager_load_error.csv", index=False, header=None)


    # initialize roi_matching["match"]
    for t_plane_pri in list(dict_roi_matching["id"].keys())[:-1]: # except last t_plane 
        for t_plane_sec in dict_roi_matching["match"][t_plane_pri].keys():
            dict_roi_matching["match"][t_plane_pri][t_plane_sec] = {roi_id: None for roi_id in dict_roi_matching["id"][t_plane_pri]}

    # get roi_matching["match"]
    for roi in rois:
        roi_name = roi.name # MXXX_SXX
        roi_name = roi_name.replace(" ", "") # remove space
        roi_name = roi_name.upper() # mXXX_sXX -> MXXX_SXX
        roi_name = roi_name.replace("-", "_") # MXXX-SXX -> MXXX_SXX
        name = roi_name.split("_")[0]
        # single ROI existing multi planes
        for t_plane_pri in dict_roi_matching["match"].keys():
            for t_plane_sec in dict_roi_matching["match"][t_plane_pri].keys():
                try:
                    roi_id_pri = dict_roi_matching_anchor[name][t_plane_pri]
                    roi_id_sec = dict_roi_matching_anchor[name][t_plane_sec]
                    dict_roi_matching["match"][t_plane_pri][t_plane_sec][roi_id_pri] = roi_id_sec
                except KeyError:
                    pass

    return dict_roi_matching, dict_roi_coords_xyct


"""
Write Functions
"""
# convert dict_roi_coords_xyct, dict_roi_matching to imageJ roi.zip
def convertDictROIMatchingAndDictROICoordsToImagejRoi(
        dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]], 
        dict_roi_coords_xyct: Dict[int, Dict[int, Dict[Literal["x", "y", "med"], np.ndarray]]],
    ) -> List[ImagejRoi]:
    list_roi = []
    # create dict_roi_name from dict_roi_matching
    dict_roi_name = createDictROINameFromDictROIMatching(dict_roi_matching)

    for t_plane in dict_roi_matching["id"].keys():
        for id_roi in dict_roi_matching["id"][t_plane]:
            # make ImagejRoi from ROI's contour coordinates
            coords = np.array([dict_roi_coords_xyct[t_plane][id_roi]["xpix"], dict_roi_coords_xyct[t_plane][id_roi]["ypix"]]).T
            x_contour, y_contour = getROIContour(coords[:, 0], coords[:, 1], method='edge')
            coords_contour = np.array([x_contour, y_contour]).T
            roi = ImagejRoi.frompoints(coords_contour)
            # rename ROI's name
            roi.name = dict_roi_name[t_plane][id_roi]
            roi.t_position = t_plane + 1
            list_roi.append(roi)

    # sort with MXXX
    list_roi = sortRoisByName(list_roi)

    return list_roi

# create dict_roi_name for creating ImageJ ROI from dict_roi_matching
def createDictROINameFromDictROIMatching(
        dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]]
        ) -> Dict[int, Dict[int, str]]:
    # Set to track processed ROIs
    processed_rois = set()
    
    # List of cell groups (ROIs from the same cell)
    cell_groups = []
    
    # List of time frames
    t_planes = sorted(dict_roi_matching["id"].keys())
    
    # Process each ROI in each time frame
    for t_plane in t_planes:
        for roi_id in dict_roi_matching["id"][t_plane]:
            # Skip if already processed
            if (t_plane, roi_id) in processed_rois:
                continue
            
            # Collect ROIs related to current ROI
            related_rois = [(t_plane, roi_id)]
            processed_rois.add((t_plane, roi_id))
            
            # Find other ROIs related to this ROI
            for t1 in t_planes:
                if t1 == t_plane:
                    continue
                
                # Check matching from t_plane to t1
                if t_plane in dict_roi_matching["match"] and t1 in dict_roi_matching["match"][t_plane]:
                    matched_roi_id = dict_roi_matching["match"][t_plane][t1].get(roi_id)
                    if matched_roi_id is not None:
                        related_rois.append((t1, matched_roi_id))
                        processed_rois.add((t1, matched_roi_id))
            
            # Check consistency between related ROIs (complete graph)
            consistent = True
            for i, (t1, roi_id1) in enumerate(related_rois):
                for j, (t2, roi_id2) in enumerate(related_rois[i+1:], i+1):
                    # Check direct matching
                    if t1 in dict_roi_matching["match"] and t2 in dict_roi_matching["match"][t1]:
                        # Matching from t1 to t2
                        if dict_roi_matching["match"][t1][t2].get(roi_id1) != roi_id2:
                            consistent = False
                            break
                    elif t2 in dict_roi_matching["match"] and t1 in dict_roi_matching["match"][t2]:
                        # Matching from t2 to t1
                        if dict_roi_matching["match"][t2][t1].get(roi_id2) != roi_id1:
                            consistent = False
                            break
                    else:
                        # No direct matching means inconsistency
                        consistent = False
                        break
                
                if not consistent:
                    break
            
            # Add as one group if consistent
            if consistent:
                cell_groups.append(related_rois)
            else:
                # Process as separate ROIs if inconsistent
                for r in related_rois:
                    if r not in [item for group in cell_groups for item in group]:
                        cell_groups.append([r])
    
    # Initialize dictionary for ROI names
    dict_roi_name = {t: {} for t in t_planes}
    
    # Assign M number to each group
    for i, group in enumerate(cell_groups, 1):
        for t, roi_id in group:
            dict_roi_name[t][roi_id] = f"M{i:03d}_S{t+1:02d}"
    
    return dict_roi_name

# sort ImagejRois with name in format "Mxxx_Sxx"
def sortRoisByName(list_roi: List[ImagejRoi]) -> List[ImagejRoi]:
    def get_m_s_numbers(roi_name):
        # Extract M and S numbers from name
        name = roi_name.replace(" ", "").upper()
        
        # Handle possible format variations (M-S or M_S)
        if "-" in name:
            parts = name.split("-")
        else:
            parts = name.split("_")
            
        if len(parts) != 2 or not parts[0].startswith("M") or not parts[1].startswith("S"):
            return (float('inf'), float('inf'))  # Invalid format sorts to end
        
        try:
            m_num = int(parts[0][1:])  # Number after 'M'
            s_num = int(parts[1][1:])  # Number after 'S' 
            return (m_num, s_num)
        except ValueError:
            return (float('inf'), float('inf'))  # Invalid numbers sort to end
    
    # Sort using M number as primary key, S number as secondary key
    return sorted(list_roi, key=lambda roi: get_m_s_numbers(roi.name))