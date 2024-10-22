from __future__ import annotations
from ..type_definitions import *
from ..preprocessing.preprocessing_tiff import extractTIFFStack
import numpy as np

def calculateDFF0(data: np.ndarray, F0: float) -> np.ndarray:
    if F0 == 0:
        F0 = 1e-6 # to avoid division by zero
    dff0 = (data - F0) / F0
    return dff0

# normalize image stack with reference areas
def normalizeImageStackWithReferenceAreas(
        tiff_stack: np.ndarray, # XYCZT
        list_reference_areas: List[Tuple[int, int, int, int, int, int, int, int]], # XYZT
) -> np.ndarray:

    print("Normalizing...")
    reference_area = np.array([])
    channels = tiff_stack.shape[2]
    tiff_stack_norm = tiff_stack.copy().astype("float32")
    for reference_area in list_reference_areas:
        xmin, xmax, ymin, ymax, zmin, zmax, tmin, tmax = reference_area
        tiff_stack_extracted = extractTIFFStack(tiff_stack, x_min=xmin, x_max=xmax, y_min=ymin, y_max=ymax, z_min=zmin, z_max=zmax, t_min=tmin, t_max=tmax)
        reference_area = np.concatenate((reference_area, tiff_stack_extracted.flatten()), axis=0)
    
    f0 = np.mean(reference_area)

    for channel in range(channels):
        tiff_stack_norm[:, :, channel :, :] = calculateDFF0(tiff_stack_norm[:, :, channel :, :], f0)
    print(tiff_stack_norm.shape)
    print(np.mean(tiff_stack))
    print(np.mean(reference_area))
    print(np.mean(tiff_stack_norm))
    print("Finished Normalizing !")


    return tiff_stack_norm