# データの読み込み用関数
from scipy.io import loadmat
from ..preprocessing.preprocessing_fall import convertMatToDictFall, convertMatToDictROICheck

# Fallの読み込み
def loadFallMAT(data_manager, path_fall, preprocessing=True):
    Fall = loadmat(path_fall)
    if preprocessing:
        dict_Fall = convertMatToDictFall(Fall)
        return dict_Fall
    return Fall

# EventFile npyの読み込み, 初期化
def loadEventFileNPY(widget_manager, path_npy):
    pass

def clearEventFileNPY(widget_manager):
    pass