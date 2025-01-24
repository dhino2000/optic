from __future__ import annotations
from ..type_definitions import *
from cellpose import denoise
import numpy as np

# run cellpose with denoising for a single channel image
def runCellposeDenoiseForMonoImage(
    img: np.ndarray[Tuple[int, int]],
    diam: int,
    model_type: str,
    restore_type: str,
):
    model = denoise.CellposeDenoiseModel(gpu=True, model_type=model_type, restore_type=restore_type)
    mask, flow, style, img_dn = model.eval(img, diameter=diam, channels=[0, 0])
    return mask, flow, style, img_dn