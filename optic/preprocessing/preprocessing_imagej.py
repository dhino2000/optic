from __future__ import annotations
from ..type_definitions import *
from typing import Tuple, Dict, List, Optional, Literal
from roifile import ImagejRoi
import numpy as np
import cv2
import re

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
    # anchor dict for dict_roi_matching["match"]
    # ex) {"m001": {0: 1, 1: 2, 2: 4, 3: 2}, "m002": {0: 3, 1: 4, 2: 5, 3: 6}}
    dict_roi_matching_anchor: Dict[str, Dict[int, int]] = {}

    # get roi_matching["id"] and roi_coords_xyct
    for i, roi in enumerate(rois):
        roi_name = roi.name # mXXX-sXX

        # only FREEHAND roi !
        if roi.roitype == 7:
            try:
                roi_x_start = roi.left
                roi_y_start = roi.top
                roi_xy_coords = roi.integer_coordinates

                xpix_contour = roi_xy_coords[:, 0] + roi_x_start
                ypix_contour = roi_xy_coords[:, 1] + roi_y_start
                xpix_ypix_contour = np.column_stack((xpix_contour, ypix_contour))
                # convert contour to filled roi
                xpix_ypix = convertContourToFilled(xpix_ypix_contour, img_width, img_height)
                xpix, ypix = xpix_ypix[:, 0], xpix_ypix[:, 1]

                med = np.array([np.median(xpix).astype("uint16"), np.median(ypix).astype("uint16")])

                roi_z_plane = roi.z_position - 1
                roi_t_plane = roi.t_position - 1
                
                """
                WARNING !!!
                Current roi naming rule is "mXXX-sXX" or "MXXX-SXX", m,M : ROI ID, s,S : t_plane number
                But, this rule is not always correct.
                """
                # if naming rule is not correct, skip
                # mXXX-sXX
                if not re.match(r'^m\d+-s\d+$', roi_name):
                    # MXXX-SXX
                    if not re.match(r'^M\d+-S\d+$', roi_name):
                        print("ROI load error: ", roi_name)
                        print("WRONG NAMING")
                        continue
                    else:
                        roi_name = roi_name.lower() # MXXX-SXX -> mXXX-sXX

                if not int(roi_name.split("-")[1].split("s")[1]) == roi_t_plane + 1:
                    print("ROI load error: ", roi_name)
                    print("WRONG NAMING")
                    continue

                name = roi_name.split("-")[0]
                roi_id = int(name.split("m")[1]) - 1
                
                # Some ROI's z_position and t_position are 0, it's not correct.
                if roi.t_position == 0:
                    print("ROI load error: ", roi_name)
                    print("NOT CONTAIN t_position")
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
                print("ROI load error: ", roi_name)
                print("INDEX ERROR")
        else:
            print("ROI load error: ", roi_name)
            print("NOT FREEHAND ROI")

    # initialize roi_matching["match"]
    for t_plane_pri in list(dict_roi_matching["id"].keys())[:-1]: # except last t_plane 
        for t_plane_sec in dict_roi_matching["match"][t_plane_pri].keys():
            dict_roi_matching["match"][t_plane_pri][t_plane_sec] = {roi_id: None for roi_id in dict_roi_matching["id"][t_plane_pri]}

    # get roi_matching["match"]
    for roi in rois:
        roi_name = roi.name
        name = roi_name.split("-")[0]
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

# convert ROI contour to filled ROI
def convertContourToFilled(
        roi_contour: np.ndarray[int, int], 
        width: int, 
        height: int
        ) -> np.ndarray[int, int]:
    img = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(img, [roi_contour], 1)
    y, x = np.where(img > 0)
    roi_filled = np.column_stack((x, y))
    return roi_filled