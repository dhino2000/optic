class DataManager:
    def __init__(self):
        self.dict_Fall         = {}
        self.dict_im_bg        = {}
        self.dict_im_chan2     = {}
        self.dict_eventfile    = {}
        self.dict_roicheck     = {}
        self.dict_selected_roi = {}

    def setSelectedROI(self, key, roi_id):
        self.dict_selected_roi[key] = roi_id

    def getSelectedROI(self, key):
        return self.dict_selected_roi.get(key)
        