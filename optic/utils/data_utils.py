import numpy as np

# Downsample trace data to target length with maintaining waveform shape
def downSampleTrace(data: np.ndarray, target_size: int):
    if len(data) <= target_size:
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