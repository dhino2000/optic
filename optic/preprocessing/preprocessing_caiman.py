from __future__ import annotations
from ..type_definitions import *
import numpy as np
from typing import Dict, Tuple, Any


def convertCaimanHDF5ToDictFall(
        cnmf_result: Any,
        threshold_ratio: float = 0.2,
        ) -> Dict[str, Any]:
    """
    Convert CaImAn HDF5 results to Suite2p Fall.mat (dict_Fall) format.
    
    Args:
        cnmf_result: CaImAn CNMF result object
        threshold_ratio (float): Threshold ratio for spatial footprint (default: 0.2)
            
    Returns:
        Dict: dict_Fall format dictionary
    """
    # Get spatial components and dimensions
    estimates = cnmf_result.estimates
    params = cnmf_result.params
    A = estimates.A
    C = estimates.C
    S = estimates.S
    dims = estimates.dims
    height, width = dims

    """
    Fall; F, Fneu, spks
    """
    F = C
    spks = S

    """
    Fall; iscell
    """
    idx_components = estimates.idx_components
    iscell = np.zeros((A.shape[1], 2), dtype=np.int32)
    iscell[idx_components, 0] = 1  # Mark as cell

    """
    Fall; ops
    """
    meanImg = np.reshape(estimates.b.dot(estimates.f.mean(1)), dims, order='F')
    ops = {
        "meanImg": meanImg,
        "Lx": width,
        "Ly": height,
        "fs": params.data["fr"],
        "nchannels": 1, # assuming single channel
    }

    """
    Fall; stat
    """    
    stat = {}
    
    # Process each ROI

    for idx in np.arange(A.shape[1]):
        # Get spatial component for specific ROI
        roi_spatial = A[:, idx].toarray().flatten()
        
        # Reshape to 2D image
        roi_2d = roi_spatial.reshape(dims)
        
        # Apply threshold (CaImAn default: 20% of maximum value)
        threshold = roi_2d.max() * threshold_ratio
        
        # Get coordinates of pixels above threshold
        xpix, ypix = np.where(roi_2d > threshold)

        med = (np.median(xpix), np.median(ypix))
        
        # Create Suite2p format dictionary
        roi_dict = {
            'ypix': ypix,
            'xpix': xpix,
            'med': med,
            "npix": len(ypix),
        }
        
        stat[idx] = roi_dict
    
    dict_Fall = {
        "F": F,
        "spks": spks,
        "iscell": iscell,
        "ops": ops,
        "stat": stat,
    }
    return dict_Fall