# 画像データの前処理関数
import numpy as np

# 画像をint型に変換 型は指定可能
def convertImageDtypeToINT(img, dtype="uint8"):
    img = img.astype("float")
    img -= np.min(img)
    img /= np.max(img)
    img *= 255
    img = img.astype(dtype)
    return img

# 大きさが異なる画像をそろえる, max_proj, Vcorr用
def resizeImageShape(img, shape_tgt):
    if img.shape == shape_tgt:
        return img
    # 新しい黒い画像を作成
    new_img = np.zeros(shape_tgt, dtype=img.dtype)
    # 中央に配置するための開始位置を計算
    start_y = (shape_tgt[0] - img.shape[0]) // 2
    start_x = (shape_tgt[1] - img.shape[1]) // 2
    # 小さい画像を中央に配置
    new_img[start_y:start_y+img.shape[0], start_x:start_x+img.shape[1]] = img
    return new_img