from __future__ import annotations
from ..type_definitions import *
import numpy as np
from itertools import combinations

# convert Cellpose's mask into dict of ROI coordinates
"""
Caution !!!
ROI management system of cellpose and optic is different.
In cellpose, the ROI IDs of the identical ROI in different time points are same,
but in optic, each timepoint has its own ROI IDs.
the matching relationship is managed by the "cell_id_match" column.
"""
def convertCellposeMaskToDictROICoords(
    masks       : np.ndarray[np.uint16, Tuple[int, int]], 
    ) -> Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]:
    dict_roi_coords = {}

    list_roi_id_cellpose = np.delete(np.unique(masks), 0)
    for roi_id, roi_id_cellpose in enumerate(list_roi_id_cellpose):
        ypix, xpix = np.where(masks == roi_id_cellpose) # XY reversed
        xpix, ypix = xpix.astype("uint16"), ypix.astype("uint16")

        med = (int(np.median(ypix)), int(np.median(xpix))) # XY reversed, follow Suite2p format
        dict_roi_coords[roi_id] = {"xpix": xpix, "ypix": ypix, "med": med}
    return dict_roi_coords

def convertCellposeMaskToDictROICoordsXYCT(
    masks       : np.ndarray[np.uint16, Tuple[int, int, int]], 
    ) -> Dict[int, Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32]]]]:
    dict_roi_coords_xyct = {}
    for t_plane, mask in enumerate(masks):
        dict_roi_coords_xyct[t_plane] = {}
        list_roi_id_cellpose = np.delete(np.unique(mask), 0)
        for roi_id, roi_id_cellpose in enumerate(list_roi_id_cellpose):
            ypix, xpix = np.where(mask == roi_id_cellpose) # XY reversed
            xpix, ypix = xpix.astype("uint16"), ypix.astype("uint16")

            med = (int(np.median(ypix)), int(np.median(xpix))) # XY reversed, follow Suite2p format
            dict_roi_coords_xyct[t_plane][roi_id] = {"xpix": xpix, "ypix": ypix, "med": med}
    return dict_roi_coords_xyct

# convert Cellpose's mask into dict of ROI matching
def convertCellposeMaskToDictROIMatching(
    masks       : np.ndarray[np.uint16, Tuple[int, int, int]], 
) -> Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]]:
    """
    Convert a Cellpose mask array into a dict_roi_matching structure.
    Dict["id", Dict[plane_t, List[roi_id]]], "match", Dict[plane_t_pri, Dict[plane_t_sec, Dict[roi_id, Optional[roi_id]]]]
    """
    dict_roi_matching = {"id": {}, "match": {}}
    list_plane_combi = list(combinations(range(len(masks)), 2))

    # ROI ID
    for plane_t, mask in enumerate(masks):
        dict_roi_matching["id"][plane_t] = list(np.arange(len(np.delete(np.unique(mask), 0))))

    # ROI Matching
    for plane_pri, plane_sec in list_plane_combi:
        # Initialize the nested dictionaries if not already present
        if plane_pri not in dict_roi_matching["match"]:
            dict_roi_matching["match"][plane_pri] = {}
        if plane_sec not in dict_roi_matching["match"][plane_pri]:
            dict_roi_matching["match"][plane_pri][plane_sec] = {}

        # Extract the masks for the primary and secondary planes
        mask_pri, mask_sec = masks[plane_pri], masks[plane_sec]

        # Get unique ROI IDs, excluding 0 (background)
        list_roi_id_cellpose_pri = np.delete(np.unique(mask_pri), 0)
        list_roi_id_cellpose_sec = np.delete(np.unique(mask_sec), 0)

        # Perform ROI matching
        for roi_id_pri, roi_id_cellpose_pri in enumerate(list_roi_id_cellpose_pri):
            matched = False
            for roi_id_sec, roi_id_cellpose_sec in enumerate(list_roi_id_cellpose_sec):
                if roi_id_cellpose_sec == roi_id_cellpose_pri:
                    dict_roi_matching["match"][plane_pri][plane_sec][roi_id_pri] = roi_id_sec
                    matched = True
                    break
            if not matched:
                dict_roi_matching["match"][plane_pri][plane_sec][roi_id_pri] = None

    return dict_roi_matching
