# 画像データの前処理関数
import numpy as np
from typing import Optional
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

# 白黒画像からカラー画像作成
def convertMonoImageToRGBImage(image_r: Optional[np.ndarray] = None, 
                               image_g: Optional[np.ndarray] = None, 
                               image_b: Optional[np.ndarray] = None) -> np.ndarray:
    """
    1~3チャンネルの画像を組み合わせてRGB画像を生成する。

    Args:
    image_r (np.ndarray, optional): 赤チャンネルの画像
    image_g (np.ndarray, optional): 緑チャンネルの画像
    image_b (np.ndarray, optional): 青チャンネルの画像

    Returns:
    np.ndarray: 生成されたRGB画像

    Raises:
    ValueError: どのチャンネルにも画像が提供されていない場合
    """
    # 少なくとも1つのチャンネルに画像があることを確認
    if image_r is None and image_g is None and image_b is None:
        raise ValueError("At least one channel image must be provided")

    # 非Noneの画像のリストを作成
    images = [img for img in [image_r, image_g, image_b] if img is not None]

    # すべての画像のサイズが同じであることを確認
    if len(set(img.shape for img in images)) != 1:
        raise ValueError("All provided images must have the same dimensions")

    # 画像サイズを取得
    height, width = images[0].shape[:2]

    # RGB画像を初期化
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

    # 各チャンネルを処理
    for i, img in enumerate([image_r, image_g, image_b]):
        if img is not None:
            rgb_image[:, :, i] = img

    return rgb_image