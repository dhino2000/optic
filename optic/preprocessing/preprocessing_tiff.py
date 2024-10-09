from __future__ import annotations
import numpy as np

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