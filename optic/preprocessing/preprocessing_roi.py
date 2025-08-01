from __future__ import annotations
from ..type_definitions import *
import cv2
import numpy as np

# get ROI contour from the ROI's xpix array and ypix array
# method = "dilate" : for displaying on view
# method = "edge" : for making ImageJ ROI zip file
def getROIContour(
        xpix: np.ndarray, 
        ypix: np.ndarray,
        method: Literal["dilate", "edge"] = 'dilate'
        ) -> Tuple[np.ndarray, np.ndarray]:
    x_min, x_max = np.min(xpix), np.max(xpix)
    y_min, y_max = np.min(ypix), np.max(ypix)

    margin = 2
    mask = np.zeros((y_max - y_min + 1 + 2*margin, x_max - x_min + 1 + 2*margin), dtype=np.uint8)
    mask[ypix - y_min + margin, xpix - x_min + margin] = 255

    if method == 'dilate':
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    if len(contours) == 0:
        return np.array([]), np.array([])
    
    contour = contours[0].squeeze()
    
    if len(contour.shape) == 1:
        contour = np.array([contour]).reshape(1, 2)
    
    xpix_contour = contour[:, 0] + x_min - margin
    ypix_contour = contour[:, 1] + y_min - margin
    return xpix_contour, ypix_contour

# convert ROI contour to filled ROI
def convertROIContourToFilled(
        roi_contour: np.ndarray[int, int], 
        width: int, 
        height: int
        ) -> np.ndarray[int, int]:
    img = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(img, [roi_contour], 1)
    y, x = np.where(img > 0)
    roi_filled = np.column_stack((x, y))
    return roi_filled

# convert ROI contour to filled ROI for ROI_TYPE.RECT
def convertROIContourToFilledForRECT(
        roi_contour: np.ndarray[int, int], 
        width: int, 
        height: int
        ) -> np.ndarray[int, int]:
    import rasterio.features
    from shapely.geometry import Polygon

    polygon = Polygon(roi_contour)
    mask = rasterio.features.rasterize(
        [(polygon, 1)],
        out_shape=(height, width)
    )
    y_indices, x_indices = np.where(mask > 0)
    roi_filled = np.column_stack((x_indices, y_indices))
    return roi_filled

# update ROI Image, show only choosed celltype, show registered ROI image or not
def updateROIImage(
        data_manager: DataManager, 
        control_manager: ControlManager, 
        app_key: AppKeys, 
        dtype: str="uint8", 
        value: int=50, 
        reg: bool=False
        ) -> Dict[str, np.ndarray]:
    dict_im_roi, dict_im_roi_reg = {}, {}
    dict_roi_display = control_manager.getSharedAttr(app_key, "dict_roi_display")

    roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)
    for roiId, coords in data_manager.getDictROICoords(app_key).items():
        if all(dict_roi_display[roiId].values()):
            xpix, ypix = coords["xpix"], coords["ypix"]
            roi_img[ypix, xpix] = value # XY reversed
    dict_im_roi["all"] = roi_img
    # for registered ROI image
    if reg:
        roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)
        for roiId, coords in data_manager.getDictROICoordsRegistered(app_key).items():
            if all(dict_roi_display[roiId].values()):
                xpix, ypix = coords["xpix"], coords["ypix"]
                roi_img[ypix, xpix] = value # XY reversed
        dict_im_roi_reg["all"] = roi_img
        return dict_im_roi, dict_im_roi_reg
    else:
        return dict_im_roi
    
# update ROI Image for MicrogliaTracking
def updateROIImageForXYCT(
    data_manager: DataManager, 
    control_manager: ControlManager, 
    app_key: AppKeys, 
    dtype: str="uint8", 
    value: int=50, 
    reg: bool=False,
    t_plane: int=0,
    ) -> Dict[str, np.ndarray]:
    dict_im_roi, dict_im_roi_reg = {}, {}
    dict_roi_coords_xyct = data_manager.getDictROICoordsXYCT()
    dict_roi_coords_xyct_reg = data_manager.getDictROICoordsXYCTRegistered()
    roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)

    dict_roi_coords_xyct_tplane = dict_roi_coords_xyct.get(t_plane, None)
    dict_roi_coords_xyct_reg_tplane = dict_roi_coords_xyct_reg.get(t_plane, None)

    if dict_roi_coords_xyct_tplane is not None:
        for roiId, coords in dict_roi_coords_xyct_tplane.items():
            xpix, ypix = coords["xpix"], coords["ypix"]
            roi_img[xpix, ypix] = value

    dict_im_roi["all"] = roi_img
    # for registered ROI image
    if reg:
        roi_img = np.zeros(data_manager.getImageSize(app_key), dtype=dtype)
        if dict_roi_coords_xyct_reg_tplane is not None:
            for roiId, coords in dict_roi_coords_xyct_reg_tplane.items():
                xpix, ypix = coords["xpix"], coords["ypix"]
                roi_img[xpix, ypix] = value

        dict_im_roi_reg["all"] = roi_img
        return dict_im_roi, dict_im_roi_reg
    else:
        return dict_im_roi