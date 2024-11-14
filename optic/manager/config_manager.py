from __future__ import annotations
from ..type_definitions import *
from ..config.app_settings import AppSettings
from ..config.table_columns import TableColumns
from ..config.key_function_map import KeyFunctionMap
from ..config.json_config import JsonConfig
from pathlib import Path
import json

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

JSON_DIR = ROOT_DIR / "config" / "json"

class ConfigManager:
    def __init__(self):
        self.current_app       : str = None
        self.gui_defaults      : GuiDefaults = None
        self.table_columns     : Dict[AppKeys: TableColumns] = {}
        self.key_function_maps : Dict[AppKeys: KeyFunctionMap] = {}
        self.json_config       : JsonConfig = JsonConfig()

    def setCurrentApp(self, app_name: str) -> None:
        self.current_app = app_name
        self.gui_defaults = AppSettings.getGuiDefaults(app_name)
        self.initializeConfigs()

    def initializeConfigs(self) -> None:
        for app_key, table_columns in self.gui_defaults["TABLE_COLUMNS"].items():
            self.table_columns[app_key] = TableColumns(table_columns)
        for app_key, key_map in self.gui_defaults["KEY_FUNCTION_MAP"].items():
            self.key_function_maps[app_key] = KeyFunctionMap(key_map)

    def getTableColumns(self, app_key: AppKeys) -> TableColumns:
        return self.table_columns[app_key]

    def getKeyFunctionMap(self, app_key: AppKeys) -> KeyFunctionMap:
        return self.key_function_maps.get(app_key)

    def setTableColumns(self, app_key: AppKeys, new_table_columns: TableColumns):
        self.table_columns[app_key] = TableColumns(new_table_columns)

    def setKeyFunctionMap(self, app_key: AppKeys, new_key_map: KeyFunctionMap):
        self.key_function_maps[app_key] = KeyFunctionMap(new_key_map)
