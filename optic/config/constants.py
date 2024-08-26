# アプリ間で共有する定数

# ファイル選択時の拡張子
class FileFilters:
    MAT = "mat Files (*.mat);;All Files (*)"
    TIFF = "tiff Files (*.tif *.tiff);;All Files (*)"
    NPY = "npy Files (*.npy);;All Files (*)"

# BackGroungImage Type
# FALL: Suite2p
class BGImageTypeList:
    FALL = ["meanImg", "meanImgE", "max_proj", "Vcorr"]

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