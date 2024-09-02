from collections import defaultdict
from scipy.io import loadmat
from ..preprocessing.preprocessing_fall import convertMatToDictFall
from ..preprocessing.preprocessing_image import getBGImageFromFall

class DataManager:
    def __init__(self):
        self.dict_Fall                 = {}
        self.dict_im_bg                = defaultdict(dict)
        self.dict_im_bg_chan2          = {}
        self.dict_im_bg_current_type   = {}
        self.dict_eventfile            = {}
        self.dict_roicheck             = {}
        self.dict_selected_roi         = {}

    # Fall.matの読み込み
    def loadFallMAT(self, key_app, path_fall, preprocessing=True):
        try:
            Fall = loadmat(path_fall)
            if preprocessing:
                dict_Fall = convertMatToDictFall(Fall)
                self.dict_Fall[key_app] = dict_Fall
                getBGImageFromFall(self, key_app, key_app)
                self.dict_im_bg_current_type[key_app] = "meanImg"  # デフォルト設定
            else:
                self.dict_Fall[key_app] = Fall
        except FileNotFoundError as e:
            return False
        
    def getImageSize(self, key_app):
        return self.dict_Fall[key_app]["ops"]["Lx"].item(), self.dict_Fall[key_app]["ops"]["Ly"].item()

    # 選択中のROIの番号
    def setSelectedROI(self, key_app, roi_id):
        self.dict_selected_roi[key_app] = roi_id
    def getSelectedROI(self, key_app):
        return self.dict_selected_roi.get(key_app)
        
    # Background image type
    def setBGImageCurrentType(self, key_app, im_bg_type):
        self.dict_im_bg_current_type[key_app] = im_bg_type
    
    def getBGImage(self, key_app):
        return self.dict_im_bg[key_app][self.dict_im_bg_current_type[key_app]]
    
    def getBGChan2Image(self, key_app):
        return self.dict_im_bg_chan2.get(key_app)
    