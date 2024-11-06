from PyQt5.QtCore import Qt
from enum import Enum
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
JSON_DIR = CURRENT_DIR / "json"

class Extension:
    MAT = ".mat"
    TIFF = ".tif"
    NPY = ".npy"
    HDF5 = ".h5"

# ファイル選択時の拡張子
class FileFilters:
    MAT = "mat Files (*.mat);;All Files (*)"
    TIFF = "tiff Files (*.tif *.tiff);;All Files (*)"
    NPY = "npy Files (*.npy);;All Files (*)"
    HDF5 = "h5 Files (*.h5);;All Files (*)"

FILE_FILTERS = {
    ".mat": "mat Files (*.mat);;All Files (*)",
    ".tif": "tiff Files (*.tif *.tiff);;All Files (*)",
    ".npy": "npy Files (*.npy);;All Files (*)",
    ".h5": "h5 Files (*.h5);;All Files (*)",
}

# Default items of dialogs
# In the future, user json file for default settings
with open(f"{JSON_DIR}/user.json") as f:
    USERS = json.load(f)["user"]


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
    F_CHAN2 = 'dodgerblue'
    FNEU_CHAN2 = 'darkorange'
    EVENT = 'green'
    RECTANGLE = "purple"

class PlotLabels:
    F = "F"
    FNEU = "Fneu"
    SPKS = "spks"
    F_CHAN2 = "F_chan2"
    FNEU_CHAN2 = "Fneu_chan2"
    EVENT = "event"

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
class TableColumnConfigDialog_Config:
    COLUMNS = ['Column Name', 'Type', 'Width']
    COMBO_ITEMS = ['id', 'celltype', 'checkbox', 'string']
    DEFAULT_PARAMS = ["new cell type", "celltype", "80"]

# Rectangle Color
class RectangleColors:
    DRAG = Qt.yellow
    HIGHLIGHT = Qt.cyan

class DrawingWidth:
    RECTANGLE = 2