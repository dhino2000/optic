from __future__ import annotations
from ..type_definitions import *
import random
import matplotlib.pyplot as plt
import numpy as np

# generate random color for ROI
def generateRandomColor(
    r_min :int = 100,
    r_max :int = 255,
    g_min :int = 100,
    g_max :int = 255,
    b_min :int = 100,
    b_max :int = 255
) -> Tuple[int, int, int]:
    return (random.randint(r_min, r_max), random.randint(g_min, g_max), random.randint(b_min, b_max))


"""
For CheckMultiSessionROICoordinates app
These functions are temporary. These should be refined !!!
"""
def generateSessionColors(num_sessions: int) -> list:
    """
    Generate distinct colors for each session using HSV colormap
    
    Parameters:
    -----------
    num_sessions : int
        Number of sessions
    
    Returns:
    --------
    list_colors : list[tuple]
        List of RGB tuples (0-255)
    """
    list_colors = []
    cmap = plt.cm.get_cmap('hsv')
    
    for i in range(num_sessions):
        hue = i / num_sessions
        rgba = cmap(hue)
        rgb = tuple(int(c * 255) for c in rgba[:3])
        list_colors.append(rgb)
    
    return list_colors

def colorizeGrayscale(grayscale_image: np.ndarray, color: tuple) -> np.ndarray:
    """
    Convert grayscale image to colored image
    
    Parameters:
    -----------
    grayscale_image : np.ndarray (H, W)
        Grayscale image 0-255
    color : tuple (R, G, B)
        Target color 0-255
    
    Returns:
    --------
    colored : np.ndarray (H, W, 3)
        Colored RGB image
    """
    normalized = grayscale_image.astype(np.float32) / 255.0
    colored = np.zeros((*grayscale_image.shape, 3), dtype=np.float32)
    
    for c in range(3):
        colored[:, :, c] = normalized * color[c]
    
    return colored.astype(np.uint8)

def alphaBlendImage(base_image: np.ndarray, overlay_image: np.ndarray, mask: np.ndarray, alpha: int = 128) -> np.ndarray:
    """
    Additive blend overlay image onto base image where mask is True
    Black pixels (0, 0, 0) in overlay are treated as transparent
    
    Parameters:
    -----------
    base_image : np.ndarray (H, W, 3)
        Base RGB image
    overlay_image : np.ndarray (H, W, 3)
        Overlay RGB image
    mask : np.ndarray (H, W)
        Binary mask (0 or 1) or boolean
    alpha : int
        Alpha value 0-255 (default: 128)
    
    Returns:
    --------
    result : np.ndarray (H, W, 3)
        Blended RGB image
    """
    result = base_image.copy().astype(np.float32)
    overlay = overlay_image.astype(np.float32)
    alpha_normalized = alpha / 255.0
    
    # Create mask excluding black pixels
    mask_bool = mask > 0
    black_mask = (overlay[:, :, 0] == 0) & (overlay[:, :, 1] == 0) & (overlay[:, :, 2] == 0)
    blend_mask = mask_bool & (~black_mask)
    
    for c in range(3):
        result[:, :, c] = np.where(
            blend_mask,
            np.clip(result[:, :, c] + alpha_normalized * overlay[:, :, c], 0, 255),
            result[:, :, c]
        )
    
    return result.astype(np.uint8)


def alphaBlend(base_image: np.ndarray, mask: np.ndarray, color: tuple, alpha: int = 128) -> np.ndarray:
    """
    Additive blend color onto base image where mask is True
    
    Parameters:
    -----------
    base_image : np.ndarray (H, W, 3)
        Base RGB image
    mask : np.ndarray (H, W)
        Binary mask (0 or 1) or boolean
    color : tuple (R, G, B)
        RGB color values 0-255
    alpha : int
        Alpha value 0-255 (default: 128)
    
    Returns:
    --------
    result : np.ndarray (H, W, 3)
        Blended RGB image
    """
    result = base_image.copy().astype(np.float32)
    alpha_normalized = alpha / 255.0
    mask_bool = mask > 0
    
    for c in range(3):
        result[:, :, c] = np.where(
            mask_bool,
            np.clip(result[:, :, c] + alpha_normalized * color[c], 0, 255),
            result[:, :, c]
        )
    
    return result.astype(np.uint8)

def getROIMask(dict_roi: dict, dict_visibility: dict, image_shape: tuple) -> np.ndarray:
    """
    Create ROI mask from ROI dictionary and visibility dictionary
    
    Parameters:
    -----------
    dict_roi : dict
        ROI dictionary where key is ROI index (int or str), 
        value is dict containing 'xpix' and 'ypix'
        e.g., {0: {'xpix': [...], 'ypix': [...]}, 1: {...}, ...}
    dict_visibility : dict
        Visibility dictionary where key is ROI index (int or str),
        value is bool (True = visible)
        e.g., {0: True, 1: False, 2: True, ...}
    image_shape : tuple (H, W)
        Shape of output mask
    
    Returns:
    --------
    mask : np.ndarray (H, W)
        Binary mask where visible ROIs are 1
    """
    mask = np.zeros(image_shape, dtype=np.uint8)
    
    for roi_idx, is_visible in dict_visibility.items():
        if is_visible:
            roi_data = dict_roi.get(roi_idx)
            if roi_data is not None:
                xpix = roi_data['xpix']
                ypix = roi_data['ypix']
                mask[ypix, xpix] = 1
    
    return mask