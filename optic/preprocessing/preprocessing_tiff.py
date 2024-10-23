from __future__ import annotations
from ..type_definitions import *
import numpy as np
import tifffile

def standardizeTIFFStack(
        data: np.ndarray, 
        axes_src: str, 
        axes_tgt: str='XYCZT'
        ) -> np.ndarray:
    """
    standardize the TIFF stack's axes order and implement missing axes
    """
    axes_src = axes_src.upper()
    axes_tgt = axes_tgt.upper()

    for ax in axes_tgt:
        if ax not in axes_src:
            axes_src += ax
            data = np.expand_dims(data, axis=-1)

    trans_order = [axes_src.index(ax) for ax in axes_tgt]

    new_data = np.transpose(data, trans_order)

    return new_data

def extractTIFFStack(
    tiff_stack: np.ndarray,
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    z_min: Optional[int] = None,
    z_max: Optional[int] = None,
    t_min: Optional[int] = None,
    t_max: Optional[int] = None,
    c_min: Optional[int] = None,
    c_max: Optional[int] = None
) -> np.ndarray:
    """
    create TIFF stack from range list

    :param tiff_stack: original 5D tiff stack (dim: X, Y, C, Z, T)
    :param range_list: x_min, x_max, y_min, y_max, c_min, c_max, z_min, z_max, t_min, t_max
    """
    if not tiff_stack.ndim == 5:
        raise ValueError("tiff_stack should have 5 dimensions")
    
    x_slice = slice(x_min, x_max + 1 if x_max is not None else None)
    y_slice = slice(y_min, y_max + 1 if y_max is not None else None)
    c_slice = slice(c_min, c_max + 1 if c_max is not None else None)
    z_slice = slice(z_min, z_max + 1 if z_max is not None else None)
    t_slice = slice(t_min, t_max + 1 if t_max is not None else None)

    tiff_stack_extracted = tiff_stack[t_slice, z_slice, c_slice, y_slice, x_slice]
    return tiff_stack_extracted

def getTiffStackShape(path: str) -> Tuple[int, int, int, int, int]:
    """
    get shape of tiff stack and return as XYCZT format
    """
    with tifffile.TiffFile(path) as tif:
        shape = tif.series[0].shape
        axes = tif.series[0].axes
        dims = {'X': 1, 'Y': 1, 'C': 1, 'Z': 1, 'T': 1}
        
        for size, axis in zip(shape, axes):
            if axis in dims:
                dims[axis] = size
   
    return (dims['X'], dims['Y'], dims['C'], dims['Z'], dims['T'])