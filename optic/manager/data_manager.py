from collections import defaultdict

class DataManager:
    def __init__(self):
        self.dict_Fall                 = {}
        self.dict_im_bg                = defaultdict(dict)
        self.dict_im_chan2             = {}
        self.dict_im_bg_current_type   = {}
        self.dict_eventfile            = {}
        self.dict_roicheck             = {}
        self.dict_selected_roi         = {}

    # 選択中のROIの番号
    def setSelectedROI(self, key, roi_id):
        self.dict_selected_roi[key] = roi_id
    def getSelectedROI(self, key):
        return self.dict_selected_roi.get(key)
        
    # Background image type
    def setBGImageCurrentType(self, key_im_bg_current_type, im_bg_type):
        self.dict_im_bg_current_type[key_im_bg_current_type] = im_bg_type
    
    def getBGImage(self, key):
        return self.dict_im_bg[key][self.dict_im_bg_current_type[key]]