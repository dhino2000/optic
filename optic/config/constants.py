from PyQt5.QtCore import Qt
from enum import Enum
import json
from pathlib import Path

class Extension:
    MAT = ".mat"
    TIFF = ".tif"
    NPY = ".npy"
    HDF5 = ".h5"
    PNG = ".png"
    PDF = ".pdf"
    JSON = ".json"
    MAT_NPY = ".mat_npy"

# ファイル選択時の拡張子
class FileFilters:
    MAT = "mat Files (*.mat);;All Files (*)"
    TIFF = "tiff Files (*.tif *.tiff);;All Files (*)"
    NPY = "npy Files (*.npy);;All Files (*)"
    HDF5 = "h5 Files (*.h5);;All Files (*)"
    PNG_PDF = "Image Files (*.png *.pdf);;PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
    MAT_NPY = "mat and npy Files (*.mat *.npy);;All Files (*)"

FILE_FILTERS = {
    ".mat": "mat Files (*.mat);;All Files (*)",
    ".tif": "tiff Files (*.tif *.tiff);;All Files (*)",
    ".npy": "npy Files (*.npy);;All Files (*)",
    ".h5": "h5 Files (*.h5);;All Files (*)",
    ".png_pdf": "Image Files (*.png *.pdf);;PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)",
    ".mat_npy": "mat and npy Files (*.mat *.npy);;All Files (*)"
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
    # cascade colors
    CASCADE_SPIKE_PROB = "orange"
    CASCADE_SPIKE_EVENTS = "green"

# canvas plot labels
class PlotLabels:
    F = "F"
    FNEU = "Fneu"
    SPKS = "spks"
    F_CHAN2 = "F_chan2"
    FNEU_CHAN2 = "Fneu_chan2"
    EVENT = "event"
    # cascade label
    CASCADE_SPIKE_PROB = "spike prob"
    CASCADE_SPIKE_EVENTS = "spike events"

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
    ROI_PAIR = 2

# canvasのplot位置のkey
class AxisKeys:
    TOP = "top"
    MID = "mid"
    BOT = "bot"

# Table Columns Config
class TableColumnConfigDialog_Config:
    COLUMNS = ['Column Name', 'Type', 'Width']
    COMBO_ITEMS = ['id', 'celltype', 'checkbox', 'string']
    DEFAULT_PARAMS = ["new_cell_type", "celltype", "80"]

# Optimal Transport Parameters
class OTParams:
    SHAPE = [
        "footprint", 
        "mrs", 
        "mrs0", 
        "compact", 
        "solidity", 
        "npix", 
        "npix_soma", 
        "radius", 
        "aspect_ratio", 
        "npix_norm_no_crop", 
        "npix_norm", 
        "skew", 
        "std"
            ]
    
# ROI Matching Test Dialog Config
class ROIMatchingTest_Config:
    COLOR_PRI = "red"
    COLOR_SEC = "blue"
    COLOR_PAIR = "green"
    LINEWIDTH_PAIR = 4
    ALPHA = 0.5
    FONTSIZE = 12
    LABEL_PRI = "Primary"
    LABEL_SEC = "Secondary"

# URL with button access
class AccessURL:
    HELP = {
        "SUITE2P_ROI_CURATION": "https://github.com/dhino2000/optic/blob/main/docs/Suite2pROICuration/tutorial.md",
        "SUITE2P_ROI_TRACKING": "https://github.com/dhino2000/optic/blob/main/docs/Suite2pROITracking/tutorial.md",
        "MICROGLIA_TRACKING": "https://github.com/dhino2000/optic/blob/main/docs/MicrogliaTracking/tutorial.md",
        "TIFSTACK_EXPLORER": "https://github.com/dhino2000/optic/blob/main/docs/TIFStackExplorer/tutorial.md",
    }
    
# import package config
class ImportPackages:
    SUITE2P = "suite2p"
    CELLPOSE = "cellpose"
    OT = "ot"
    ELASTIX = "itk"
    ROIFILE = "roifile"
    CASCADE = "cascade"