# データの読み込み用関数
from PyQt5.QtWidgets import QMessageBox
from scipy.io import loadmat
import tifffile
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck
from ..preprocessing.preprocessing_image import convertImageDtypeToINT, resizeImageShape

# Fallの読み込み, メッセージ付き
def loadFallMAT(q_window, data_manager, key_dict_Fall, path_fall, preprocessing=True):
    try:
        Fall = loadmat(path_fall)
        if preprocessing:
            dict_Fall = convertMatToDictFall(Fall)
            data_manager.dict_Fall[key_dict_Fall] = dict_Fall
        else:
            data_manager.dict_Fall[key_dict_Fall] = Fall
        QMessageBox.information(q_window, "File load", "File loaded!")
        return data_manager.dict_Fall[key_dict_Fall]
    except FileNotFoundError as e:
        QMessageBox.warning(q_window, "File Not Found", str(e))
        return False

# tif imageの読み込み
def loadTIFImage(data_manager, key_dict_im, path_image, preprocessing=True):
    im = tifffile.imread(path_image)
    data_manager.dict_im[key_dict_im] = im
    return data_manager.dict_im[key_dict_im]

# EventFile npyの読み込み, 初期化
def loadEventFileNPY(widget_manager, path_npy):
    pass

def clearEventFileNPY(widget_manager):
    pass