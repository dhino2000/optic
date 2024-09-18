import numpy as np

# Downsample data to target length
def downSample(data: np.ndarray, target_length: int):
    if len(data) > target_length:
        return data[::len(data)//target_length]
    return data