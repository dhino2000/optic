from typing import List
import numpy as np

# Downsample trace data to target length with maintaining waveform shape
def downSampleTrace(data: np.ndarray, target_size: int):
    if len(data) <= target_size * 4:
        return data

    # 各ビンのサイズを計算
    bin_size = len(data) // target_size

    # 余りを処理するためのパディング
    pad_size = (bin_size - len(data) % bin_size) % bin_size
    padded_data = np.pad(data, (0, pad_size), mode='edge')

    # データをビンに分割
    bins = padded_data.reshape(-1, bin_size)

    # 各ビンから4つの特徴的な点を抽出
    downsampled = np.column_stack([
        bins[:, 0],          # 各ビンの開始値
        bins.min(axis=1),    # 各ビンの最小値
        bins.max(axis=1),    # 各ビンの最大値
        bins[:, -1]          # 各ビンの終了値
    ]).reshape(-1)

    return downsampled

def extractEventOnsetIndices(eventfile: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """
    Extracts indices where the eventfile crosses the specified threshold from below.

    Args:
    eventfile (np.ndarray): The event file array.
    threshold (float): The threshold value to detect crossings. Default is 0.5.

    Returns:
    np.ndarray: An array of indices where the eventfile crosses the threshold.
    """
    eventfile = np.array(eventfile)
    above_threshold = eventfile > threshold
    crossings = np.diff(above_threshold.astype(int)) > 0
    onset_indices = np.where(crossings)[0] + 1
    
    return onset_indices

def extractEventAlignedData(data: np.ndarray, 
                            event_indices: np.ndarray, 
                            pre_frames: int, 
                            post_frames: int) -> List[np.ndarray]:
    """
    Extracts data segments aligned to event onset indices.

    Args:
    data (np.ndarray): The full data array to extract segments from.
    event_indices (np.ndarray): Array of event onset indices.
    pre_frames (int): Number of frames to include before each event.
    post_frames (int): Number of frames to include after each event.

    Returns:
    List[np.ndarray]: List of extracted data segments.
    """
    extracted_segments = []
    for idx in event_indices:
        start = idx - pre_frames
        end = idx + post_frames + 1  # +1 to include the post_frames-th frame
        if start >= 0 and end <= len(data):
            segment = data[start:end]
            extracted_segments.append(segment)
    return extracted_segments