# アプリごとに変わるconfig
from typing import Dict, Any, Tuple
from PyQt5.QtCore import Qt
from .constants import FileFilters, ProcessingDefaults, PlotColors, AppKeys, ChannelKeys, AxisKeys

# GUIに関する定数
class GuiDefaults:
    """
    Suite2pROICurationGUI
    """
    SUITE2P_ROI_CURATION = {
        "MIN_PLOT_RANGE": 30,
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1200,
            "HEIGHT": 200,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_TABLE_COLUMNS_CONFIG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 800,
            "HEIGHT": 600,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_ROI_CELLTYPE_SET": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 800,
            "HEIGHT": 600,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_DIALOG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 300,
            "HEIGHT": 200,
        },
        "SCROOLAREA_SETTINGS": {
            "MAX_HEIGHT": 200,
        },
        "TITLE": "Suite2pROICurationGUI",
        "APP_KEYS": [AppKeys.PRI],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2, ChannelKeys.CHAN3],
        "ROI_THRESHOLDS": {
            "npix": "(50, 200)",
            "radius": "(3, 12)",
            "aspect_ratio": "(0, 1.5)",
            "compact": "(0, 1.5)",
            "skew": "(1, 100)",
            "std": "(0, 100)",
        },
        "VIEW_SETTINGS": {
            "DEFAULT_CONTRAST_MIN": 0,
            "DEFAULT_CONTRAST_MAX": 255,
        },
        "ROI_VISUAL_SETTINGS": {
            "COLOR_MIN": 100,
            "COLOR_MAX": 255,
            "DEFAULT_ROI_OPACITY": 128,
            "DEFAULT_HIGHLIGHT_OPACITY": 255,
        },
        "CANVAS_SETTINGS": {
            "LIGHT_MODE_DOWNSAMPLE": 250,
            "MIN_PLOT_WIDTH_SEC": 30,
            "YLIM": (-0.1, 1.1),
            "YLIM_RECTANGLE": (-0.05, 1.05),
            "PLOT_POINTS": 10,
        },
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell_ID"   : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
                "Neuron"    : {"order": 1, "type": "celltype", "width": 80,  "removable": True,  "default": True},
                "Astrocyte" : {"order": 2, "type": "celltype", "width": 80,  "removable": True,  "default": False},
                "Not_Cell"  : {"order": 3, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
                "Check"     : {"order": 4, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Tracking"  : {"order": 5, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Memo"      : {"order": 6, "type": "string",   "width": 200, "removable": True, }
            },
            # # for takeda sensei
            # AppKeys.PRI: {
            #     "Cell_ID"   : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
            #     "W"    : {"order": 1, "type": "celltype", "width": 40,  "removable": True,  "default": True},
            #     "A" : {"order": 2, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "V" : {"order": 3, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WA" : {"order": 4, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WV" : {"order": 5, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "AV" : {"order": 6, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WAV" : {"order": 7, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "N" : {"order": 8, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "Not_Cell"  : {"order": 9, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
            #     "Check"     : {"order": 10, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Tracking"  : {"order": 11, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Memo"      : {"order": 12, "type": "string",   "width": 200, "removable": True, }
            # },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('toggle', 1),
                Qt.Key_X: ('toggle', 2),
                Qt.Key_C: ('toggle', 3),
                Qt.Key_V: ('toggle', 4),
                Qt.Key_B: ('toggle', 5),
                Qt.Key_N: ('toggle', 6),
                Qt.Key_M: ('toggle', 7),
                Qt.Key_Comma: ('toggle', 8),
                Qt.Key_Period: ('toggle', 9),
                Qt.Key_Slash: ('toggle', 10),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_I: ('move', 'skip_roi', -1),
                Qt.Key_K: ('move', 'skip_roi', 1),
            },
        },
    }

    """
    Suite2pROITrackingGUI
    """
    SUITE2P_ROI_TRACKING = {
        "MIN_PLOT_RANGE": 30,
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1200,
            "HEIGHT": 200,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_TABLE_COLUMNS_CONFIG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 800,
            "HEIGHT": 600,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_ELASTIX_CONFIG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1600,
            "HEIGHT": 900,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_ROI_MATCHING_TEST": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1000,
            "HEIGHT": 900,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_DIALOG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 300,
            "HEIGHT": 200,
        },
        "SCROOLAREA_SETTINGS": {
            "MAX_HEIGHT": 200,
        },
        "TITLE": "Suite2pROITrackingGUI",
        "APP_KEYS": [AppKeys.PRI, AppKeys.SEC],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2, ChannelKeys.CHAN3],
        "VIEW_SETTINGS": {
            "DEFAULT_CONTRAST_MIN": 0,
            "DEFAULT_CONTRAST_MAX": 255,
        },
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
        "ROI_MATCHING_METHOD": ["None", "affine", "bspline"],
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell_ID"       : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
                "Cell_ID_Match" : {"order": 1, "type": "id_match", "width": 80,  "removable": False, "name_fixed": True, "editable": False},
                "Neuron"        : {"order": 2, "type": "celltype", "width": 80,  "removable": True,  "default": True},
                "Astrocyte"     : {"order": 3, "type": "celltype", "width": 80,  "removable": True,  "default": False},
                "Not_Cell"      : {"order": 4, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
                "Check"         : {"order": 5, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Tracking"      : {"order": 6, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Memo"          : {"order": 7, "type": "string",   "width": 200, "removable": True, }
            },
            AppKeys.SEC: {
                "Cell_ID"   : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
                "Neuron"    : {"order": 1, "type": "celltype", "width": 80,  "removable": True,  "default": True},
                "Astrocyte" : {"order": 2, "type": "celltype", "width": 80,  "removable": True,  "default": False},
                "Not_Cell"  : {"order": 3, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
                "Check"     : {"order": 4, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Tracking"  : {"order": 5, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
                "Memo"      : {"order": 6, "type": "string",   "width": 200, "removable": True, }
            },
            # for takeda sensei
            # AppKeys.PRI: {
            #     "Cell_ID"       : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
            #     "Cell_ID_Match" : {"order": 1, "type": "id_match", "width": 80,  "removable": False, "name_fixed": True, "editable": False},
            #     "W"             : {"order": 2, "type": "celltype", "width": 40,  "removable": True,  "default": True},
            #     "A"             : {"order": 3, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "V"             : {"order": 4, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WA"            : {"order": 5, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WV"            : {"order": 6, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "AV"            : {"order": 7, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WAV"           : {"order": 8, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "N"             : {"order": 9, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "Not_Cell"      : {"order": 10, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
            #     "Check"         : {"order": 11, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Tracking"      : {"order": 12, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Memo"          : {"order": 13, "type": "string",   "width": 200, "removable": True, }
            # },
            # AppKeys.SEC: {
            #     "Cell_ID"       : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
            #     "W"             : {"order": 1, "type": "celltype", "width": 40,  "removable": True,  "default": True},
            #     "A"             : {"order": 2, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "V"             : {"order": 3, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WA"            : {"order": 4, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WV"            : {"order": 5, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "AV"            : {"order": 6, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "WAV"           : {"order": 7, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "N"             : {"order": 8, "type": "celltype", "width": 40,  "removable": True,  "default": False},
            #     "Not_Cell"      : {"order": 9, "type": "celltype", "width": 80,  "removable": False, "name_fixed": True, "default": False},
            #     "Check"         : {"order": 10, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Tracking"      : {"order": 11, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            #     "Memo"          : {"order": 12, "type": "string",   "width": 200, "removable": True, }
            # },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('toggle', 1),
                Qt.Key_X: ('toggle', 2),
                Qt.Key_C: ('toggle', 3),
                Qt.Key_V: ('toggle', 4),
                Qt.Key_B: ('toggle', 5),
                Qt.Key_N: ('toggle', 6),
                Qt.Key_M: ('toggle', 7),
                Qt.Key_Comma: ('toggle', 8),
                Qt.Key_Period: ('toggle', 9),
                Qt.Key_Slash: ('toggle', 10),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_I: ('move', 'skip_roi', -1),
                Qt.Key_K: ('move', 'skip_roi', 1),
                Qt.Key_S: ('roi_match', 'set', 1),
            },
            AppKeys.SEC: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_Z: ('toggle', 1),
                Qt.Key_X: ('toggle', 2),
                Qt.Key_C: ('toggle', 3),
                Qt.Key_V: ('toggle', 4),
                Qt.Key_B: ('toggle', 5),
                Qt.Key_N: ('toggle', 6),
                Qt.Key_M: ('toggle', 7),
                Qt.Key_Comma: ('toggle', 8),
                Qt.Key_Period: ('toggle', 9),
                Qt.Key_Slash: ('toggle', 10),
                Qt.Key_H: ('move', 'selected_type', 1),
                Qt.Key_Y: ('move', 'selected_type', -1),
                Qt.Key_U: ('move', 'cell_type', -1),
                Qt.Key_J: ('move', 'cell_type', 1),
                Qt.Key_I: ('move', 'skip_roi', -1),
                Qt.Key_K: ('move', 'skip_roi', 1),
                Qt.Key_S: ('roi_match', 'set', 1),
            },
        },
    }

    """
    MicrogliaTrackingGUI
    """
    MICROGLIA_TRACKING = {
        "MIN_PLOT_RANGE": 30,
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1200,
            "HEIGHT": 200,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_ELASTIX_CONFIG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1600,
            "HEIGHT": 900,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_DIALOG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 300,
            "HEIGHT": 200,
        },
        "TITLE": "MicrogliaTrackingGUI",
        "APP_KEYS": [AppKeys.PRI, AppKeys.SEC],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2, ChannelKeys.CHAN3],
        "VIEW_SETTINGS": {
            "DEFAULT_CONTRAST_MIN": 0,
            "DEFAULT_CONTRAST_MAX": 255,
        },
        "ROI_VISUAL_SETTINGS": {
            "COLOR_MIN": 100,
            "COLOR_MAX": 255,
            "DEFAULT_ROI_OPACITY": 128,
            "DEFAULT_HIGHLIGHT_OPACITY": 255,
        },
        "ROI_MATCHING_METHOD": ["None", "affine", "bspline"],
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell_ID"       : {"order": 0, "type": "id",       "width": 120,  "removable": False, "name_fixed": True, "editable": False},
                "Cell_ID_Match" : {"order": 1, "type": "id_match", "width": 120,  "removable": False, "name_fixed": True, "editable": False},
                # "Check"         : {"order": 2, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            },
            AppKeys.SEC: {
                "Cell_ID"   : {"order": 0, "type": "id",       "width": 120,  "removable": False, "name_fixed": True, "editable": False},
                # "Check"     : {"order": 1, "type": "checkbox", "width": 80,  "removable": True,  "default": False},
            },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_S: ('roi_match', 'set', 1),
            },
            AppKeys.SEC: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
                Qt.Key_S: ('roi_match', 'set', 1),
            },
        },
    }

    """
    TIFStackExplorerGUI
    """
    TIFSTACK_EXPLORER = {
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1200,
            "HEIGHT": 200,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_ELASTIX_CONFIG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1600,
            "HEIGHT": 1000,
            # "MAX_WIDTH": 1920,
            # "MAX_HEIGHT": 1080,
        },
        "WINDOW_SETTINGS_DIALOG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 600,
            "HEIGHT": 200,
        },
        "TITLE": "TIFStackExplorerGUI",
        "APP_KEYS": [AppKeys.PRI],
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2, ChannelKeys.CHAN3],
        "ROI_THRESHOLDS": {
        },
        "VIEW_SETTINGS": {
            "DEFAULT_CONTRAST_MIN": 0,
            "DEFAULT_CONTRAST_MAX": 255,
        },
        "ROI_VISUAL_SETTINGS": {
            "COLOR_MIN": 100,
            "COLOR_MAX": 255,
            "DEFAULT_ROI_OPACITY": 128,
            "DEFAULT_HIGHLIGHT_OPACITY": 255,
        },
        "CANVAS_SETTINGS": {
        },
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
            },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
            },
        },
        "REGISTRATION_METHOD": ["None", "affine", "bspline"],
    }

    SUITE2P_AUTO_RUN = {
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1300,
            "HEIGHT": 900,
        },
        "TITLE": "Suite2pAutoRunGUI",
        "APP_KEYS": [AppKeys.PRI],
    }

    """
    CASCADE GUI
    """
    CASCADE = {
        "MIN_PLOT_RANGE": 30,
        "WINDOW_SETTINGS": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1200,
            "HEIGHT": 200,
        },
        "WINDOW_SETTINGS_DIALOG_DATA_LOAD": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 1000,
            "HEIGHT": 200,
        },
        "WINDOW_SETTINGS_DIALOG": {
            "INIT_POSITION_X": 100, 
            "INIT_POSITION_Y": 100,
            "WIDTH": 300,
            "HEIGHT": 200,
        },
        "SCROOLAREA_SETTINGS": {
            "MAX_HEIGHT": 200,
        },
        "TITLE": "CascadeGUI",
        "APP_KEYS": [AppKeys.PRI],
        "CANVAS_SETTINGS": {
            "LIGHT_MODE_DOWNSAMPLE": 250,
            "MIN_PLOT_WIDTH_SEC": 30,
            "YLIM": (-0.1, 1.1),
            "YLIM_RECTANGLE": (-0.05, 1.05),
            "PLOT_POINTS": 10,
        },
        "TABLE_COLUMNS": {
            AppKeys.PRI: {
                "Cell_ID"   : {"order": 0, "type": "id",       "width": 80,  "removable": False, "name_fixed": True, "editable": False},
                "Memo"      : {"order": 1, "type": "string",   "width": 200, "removable": True, }
            },
        },
        "KEY_FUNCTION_MAP": {
            AppKeys.PRI: {
                Qt.Key_Up: ('move', 'up', 1),
                Qt.Key_Down: ('move', 'down', 1),
                Qt.Key_Left: ('move', 'left', 1),
                Qt.Key_Right: ('move', 'right', 1),
            },
        },
    }
    
    @classmethod
    def getROIDisplayOptions(cls, app_name, table_columns):
        if not hasattr(cls, app_name):
            raise ValueError(f"Invalid app name: {app_name}")
        
        options = getattr(cls, app_name).get("ROI_DISPLAY_OPTIONS", {})
        cell_types = [key for key, value in table_columns.items() if value['type'] == options.get("CELL_TYPES_COLUMN_TYPE", "radio")]
        return [options.get("ALL", "All ROI")] + cell_types + [options.get("NONE", "None")]



