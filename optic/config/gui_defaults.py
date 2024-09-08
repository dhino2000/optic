# アプリごとに変わるconfig
from typing import Dict, Any, Tuple
from PyQt5.QtCore import Qt
from .constants import FileFilters, ProcessingDefaults, PlotColors, AppKeys, ChannelKeys, AxisKeys
from .table_columns import TableColumns
from .key_function_map import KeyFunctionMap
import random

# GUIに関する定数
class GuiDefaults:
    SUITE2P_ROI_CHECK = {
        "ROI_OPACITY": 50,
        "SELECTED_ROI_OPACITY": 255,
        "MIN_PLOT_RANGE": 30,
        "INIT_POSITION_X": 100, 
        "INIT_POSITION_Y": 100,
        "WIDTH": 1200,
        "HEIGHT": 200,
        "TITLE": "Suite2pROICheckGUI",
        "APP_KEYS": [AppKeys.PRI],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2],
        "DEFAULT_CONTRAST_MIN": 0,
        "DEFAULT_CONTRAST_MAX": 255,
        "ROI_THRESHOLDS": {
            "npix": "(50, 200)",
            "radius": "(3, 12)",
            "aspect_ratio": "(0, 1.5)",
            "compact": "(0, 1.5)",
            "skew": "(1, 100)",
            "std": "(0, 100)",
        },
        "ROI_VISUAL_SETTINGS": {
            "COLOR_MIN": 100,
            "COLOR_MAX": 255,
            "DEFAULT_ROI_OPACITY": 128,
            "DEFAULT_HIGHLIGHT_OPACITY": 255,
        },
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell ID"   : {"order": 0, "type": "id",       "width": 100, "editable": False},
                "Astrocyte" : {"order": 1, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Neuron"    : {"order": 2, "type": "radio",    "width": 100, "group": "celltype", "default": True},
                "Not Cell"  : {"order": 3, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Check"     : {"order": 4, "type": "checkbox", "width": 100, "default": False},
                "Tracking"  : {"order": 5, "type": "checkbox", "width": 100, "default": False},
                "Memo"      : {"order": 6, "type": "string",   "width": 200, "editable": True}
            },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('radio', 1),
                Qt.Key_X: ('radio', 2),
                Qt.Key_C: ('radio', 3),
                Qt.Key_V: ('checkbox', 4),
                Qt.Key_B: ('checkbox', 5),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_I: ('move', 'skip_checked', -1),
                Qt.Key_O: ('move', 'skip_unchecked', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_K: ('move', 'skip_checked', 1),
                Qt.Key_L: ('move', 'skip_unchecked', 1),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
            },
        },
    },

    SUITE2P_ROI_TRACKING = {
        "ROI_OPACITY": 50,
        "SELECTED_ROI_OPACITY": 255,
        "MIN_PLOT_RANGE": 30,
        "INIT_POSITION_X": 100, 
        "INIT_POSITION_Y": 100,
        "WIDTH": 1200,
        "HEIGHT": 200,
        "TITLE": "Suite2pROICheckGUI",
        "APP_KEYS": [AppKeys.PRI, AppKeys.SEC],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2, ChannelKeys.CHAN3],
        "DEFAULT_CONTRAST_MIN": 0,
        "DEFAULT_CONTRAST_MAX": 255,
        "ROI_THRESHOLDS": {
            "npix": "(50, 200)",
            "radius": "(3, 12)",
            "aspect_ratio": "(0, 1.5)",
            "compact": "(0, 1.5)",
            "skew": "(1, 100)",
            "std": "(0, 100)",
        },
        "ROI_VISUAL_SETTINGS": {
            "COLOR_MIN": 100,
            "COLOR_MAX": 255,
            "DEFAULT_ROI_OPACITY": 128,
            "DEFAULT_HIGHLIGHT_OPACITY": 255,
        },
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell ID"   : {"order": 0, "type": "id",       "width": 100, "editable": False},
                "Astrocyte" : {"order": 1, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Neuron"    : {"order": 2, "type": "radio",    "width": 100, "group": "celltype", "default": True},
                "Not Cell"  : {"order": 3, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Check"     : {"order": 4, "type": "checkbox", "width": 100, "default": False},
                "Tracking"  : {"order": 5, "type": "checkbox", "width": 100, "default": False},
                "Memo"      : {"order": 6, "type": "string",   "width": 200, "editable": True}
            },
            AppKeys.SEC: {
                "Cell ID"   : {"order": 0, "type": "id",       "width": 100, "editable": False},
                "Astrocyte" : {"order": 1, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Neuron"    : {"order": 2, "type": "radio",    "width": 100, "group": "celltype", "default": True},
                "Not Cell"  : {"order": 3, "type": "radio",    "width": 100, "group": "celltype", "default": False},
                "Check"     : {"order": 4, "type": "checkbox", "width": 100, "default": False},
                "Tracking"  : {"order": 5, "type": "checkbox", "width": 100, "default": False},
                "Memo"      : {"order": 6, "type": "string",   "width": 200, "editable": True}
            },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('radio', 1),
                Qt.Key_X: ('radio', 2),
                Qt.Key_C: ('radio', 3),
                Qt.Key_V: ('checkbox', 4),
                Qt.Key_B: ('checkbox', 5),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_I: ('move', 'skip_checked', -1),
                Qt.Key_O: ('move', 'skip_unchecked', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_K: ('move', 'skip_checked', 1),
                Qt.Key_L: ('move', 'skip_unchecked', 1),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
            },
            AppKeys.SEC: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('radio', 1),
                Qt.Key_X: ('radio', 2),
                Qt.Key_C: ('radio', 3),
                Qt.Key_V: ('checkbox', 4),
                Qt.Key_B: ('checkbox', 5),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_I: ('move', 'skip_checked', -1),
                Qt.Key_O: ('move', 'skip_unchecked', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_K: ('move', 'skip_checked', 1),
                Qt.Key_L: ('move', 'skip_unchecked', 1),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
            },
        },
    }

    @classmethod
    def generateRandomColor(cls, app_name="SUITE2P_ROI_CHECK"):
        if not hasattr(cls, app_name):
            raise ValueError(f"Invalid app name: {app_name}")
        
        settings = getattr(cls, app_name).get("ROI_VISUAL_SETTINGS")
        if not settings:
            raise ValueError(f"ROI_VISUAL_SETTINGS not found for app: {app_name}")
        
        return (random.randint(settings["COLOR_MIN"], settings["COLOR_MAX"]),
                random.randint(settings["COLOR_MIN"], settings["COLOR_MAX"]),
                random.randint(settings["COLOR_MIN"], settings["COLOR_MAX"]))
    
    @classmethod
    def getROIDisplayOptions(cls, app_name, dict_tablecol):
        if not hasattr(cls, app_name):
            raise ValueError(f"Invalid app name: {app_name}")
        
        options = getattr(cls, app_name).get("ROI_DISPLAY_OPTIONS", {})
        cell_types = [key for key, value in dict_tablecol.items() if value['type'] == options.get("CELL_TYPES_COLUMN_TYPE", "radio")]
        return [options.get("ALL", "All ROI")] + cell_types + [options.get("NONE", "None")]



