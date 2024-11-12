from __future__ import annotations
from ..type_definitions import *
import cv2
import numpy as np

# get ROI contour from the ROI's xpix array and ypix array
def getROIContour(xpix: np.ndarray, ypix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x_min, x_max = np.min(xpix), np.max(xpix)
    y_min, y_max = np.min(ypix), np.max(ypix)

    margin = 2
    mask = np.zeros((y_max - y_min + 1 + 2*margin, x_max - x_min + 1 + 2*margin), dtype=np.uint8)
    mask[ypix - y_min + margin, xpix - x_min + margin] = 255

    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = contours[0].squeeze()

    xpix_contour = contour[:, 0] + x_min - margin
    ypix_contour = contour[:, 1] + y_min - margin
    return xpix_contour, ypix_contour