# 画像データの前処理関数
import numpy as np
from ..config.constants import BGImageTypeList

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

# Fallからbackground image取得
def getBGImageFromFall(data_manager, key_dict_Fall, key_dict_im_bg, dtype="uint8"):
    # まず、meanImgのサイズを基準サイズとして取得
    base_shape = data_manager.dict_Fall[key_dict_Fall]["ops"]["meanImg"].shape
    for key_im in BGImageTypeList.FALL:
        img = convertImageDtypeToINT(data_manager.dict_Fall[key_dict_Fall]["ops"][key_im], dtype=dtype)
        img = resizeImageShape(img, base_shape)
        data_manager.dict_im_bg[key_dict_im_bg][key_im] = img