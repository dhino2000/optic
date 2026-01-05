from __future__ import annotations


def roiIdToArrayIndex(roi_id: str, n_rois_chan1: int) -> int:
    """
    Convert ROI ID string to array index.
    
    Args:
        roi_id: ROI ID string (e.g., "0", "1", "0_chan2")
        n_rois_chan1: Number of ROIs in first Fall.mat
    
    Returns:
        Array index (int)
    """
    if "_chan2" in roi_id:
        return n_rois_chan1 + int(roi_id.replace("_chan2", ""))
    return int(roi_id)


def arrayIndexToRoiId(index: int, n_rois_chan1: int) -> str:
    """
    Convert array index to ROI ID string.
    
    Args:
        index: Array index
        n_rois_chan1: Number of ROIs in first Fall.mat
    
    Returns:
        ROI ID string (e.g., "0", "0_chan2")
    """
    if index >= n_rois_chan1:
        return f"{index - n_rois_chan1}_chan2"
    return str(index)


def isChan2Roi(roi_id: str) -> bool:
    """
    Check if ROI ID is from second Fall.mat file.
    
    Args:
        roi_id: ROI ID string
    
    Returns:
        True if ROI is from second Fall.mat
    """
    return "_chan2" in roi_id


def getRoiIdNumericPart(roi_id: str) -> int:
    """
    Get the numeric part of ROI ID.
    
    Args:
        roi_id: ROI ID string (e.g., "5", "5_chan2")
    
    Returns:
        Numeric part (e.g., 5)
    """
    return int(roi_id.replace("_chan2", ""))