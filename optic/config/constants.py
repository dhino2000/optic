# アプリ間で共有する定数
from enum import Enum

# ファイル選択時の拡張子
class FileFilters:
    MAT = "mat Files (*.mat);;All Files (*)"
    TIFF = "tiff Files (*.tif *.tiff);;All Files (*)"
    NPY = "npy Files (*.npy);;All Files (*)"

FILE_FILTERS = {
    "mat": "mat Files (*.mat);;All Files (*)",
    "tiff": "tiff Files (*.tif *.tiff);;All Files (*)",
    "npy": "npy Files (*.npy);;All Files (*)"
}

# BackGroungImage Type
class BGImageType:
    MEAN_IMG = "meanImg"
    MEAN_IMG_E = "meanImgE"
    MAX_PROJ = "max_proj"
    VCORR = "Vcorr"

# FALL: Suite2p
class BGImageTypeList:
    FALL = [BGImageType.MEAN_IMG, BGImageType.MEAN_IMG_E, BGImageType.MAX_PROJ, BGImageType.VCORR]

class ProcessingDefaults:
    RESPONSE_THRESHOLD = 30

# プロットの色
class PlotColors:
    F = 'cyan'
    FNEU = 'red'
    SPKS = 'gray'
    EVENT = 'green'

# widget管理の総合key
class AppKeys:
    PRI = "pri"
    SEC = "sec"
    TER = "ter"
    QUA = "qua"
    QUI = "qui"
    SEN = "sen"
    SEP = "sep"

# canvasのchannel key
class ChannelKeys:
    CHAN1 = "Green"
    CHAN2 = "Red"
    CHAN3 = "Blue"

# canvasのplot位置のkey
class AxisKeys:
    TOP = "top"
    MID = "mid"
    BOT = "bot"

# Table Columns Config
class TableColumnConfigWindow_Config:
    COLUMNS = ['Column Name', 'Type', 'Width']
    COMBO_ITEMS = ['id', 'celltype', 'checkbox', 'string']
    DEFAULT_PARAMS = ["new cell type", "celltype", "80"]
