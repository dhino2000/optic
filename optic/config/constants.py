from PyQt5.QtCore import Qt
from enum import Enum
import json
from pathlib import Path

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

# canvas plot color
class PlotColors:
    F = 'cyan'
    FNEU = 'red'
    SPKS = 'gray'
    F_CHAN2 = 'dodgerblue'
    FNEU_CHAN2 = 'darkorange'
    EVENT = 'green'
    RECTANGLE = "purple"

# canvas plot labels
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

# view channel key
class ChannelKeys:
    CHAN1 = "Green"
    CHAN2 = "Red"
    CHAN3 = "Blue"

# view painter's pen color
class PenColors:
    ROI_PAIR = Qt.white
    RECTANGLE_DRAG = Qt.yellow
    RECTANGLE_HIGHLIGHT = Qt.cyan

# view painter's pen width
class PenWidth:
    RECTANGLE = 2
    ROI_PAIR = 4

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