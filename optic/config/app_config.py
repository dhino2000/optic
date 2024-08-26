# アプリごとに変わるconfig
from typing import Dict, Any, Tuple
from PyQt5.QtCore import Qt
from .constants import FileFilters, ProcessingDefaults, PlotColors, AppKeys, ChannelKeys, AxisKeys

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
        "APP_KEYS": AppKeys.PRI,
        "CHANNELS": [ChannelKeys.CHAN1, ChannelKeys.CHAN2]
    }

# Tableに設定する列名とそのプロパティ
class TableColumns:
    SUITE2P_ROI_CHECK: Dict[str, Dict[str, Any]] = {
        "Cell ID": {"order": 0, "type": "id", "editable": False},
        "Astrocyte": {"order": 1, "type": "radio", "group": "celltype"},
        "Neuron": {"order": 2, "type": "radio", "group": "celltype", "default": True},
        "Not Cell": {"order": 3, "type": "radio", "group": "celltype"},
        "Check": {"order": 4, "type": "checkbox"},
        "Tracking": {"order": 5, "type": "checkbox"},
        "Memo": {"order": 6, "type": "string", "editable": True}
    }


# キーボードに対応する操作
class KeyFunctionMap:
    SUITE2P_ROI_CHECK: Dict[int, Tuple[str, Any]] = {
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
    }


# 上記のconfigをアプリ名で設定
class AppSettings:
    CURRENT_APP = "SUITE2P_ROI_CHECK"

    @classmethod
    def getTableColumns(cls) -> Dict[str, Dict[str, Any]]:
        return getattr(TableColumns, cls.current_app, {})

    @classmethod
    def getKeyFunctionMap(cls) -> Dict[int, Tuple[str, Any]]:
        return getattr(KeyFunctionMap, cls.current_app, {})

    @classmethod
    def getGuiDefaults(cls) -> Dict[str, int]:
        return getattr(GuiDefaults, cls.current_app)

    @classmethod
    def setCurrentApp(cls, app_name: str):
        if hasattr(TableColumns, app_name) and hasattr(KeyFunctionMap, app_name):
            cls.current_app = app_name
        else:
            raise ValueError(f"Invalid app name: {app_name}")
