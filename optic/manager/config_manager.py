# アプリのconfigをまとめたManagerクラス
from ..config.app_settings import AppSettings
from ..config.table_columns import TableColumns
from ..config.key_function_map import KeyFunctionMap

class ConfigManager:
    def __init__(self):
        self.current_app = None
        self.gui_defaults = None
        self.table_columns = {}
        self.key_function_maps = {}

    def setCurrentApp(self, app_name):
        self.current_app = app_name
        self.gui_defaults = AppSettings.getGuiDefaults(app_name)
        self.initializeConfigs()

    def initializeConfigs(self):
        for key_app, table_columns in self.gui_defaults["TABLE_COLUMNS"].items():
            self.table_columns[key_app] = TableColumns(table_columns)
        for key_app, key_map in self.gui_defaults["KEY_FUNCTION_MAP"].items():
            self.key_function_maps[key_app] = KeyFunctionMap(key_map)

    def getTableColumns(self, key_app):
        return self.table_columns[key_app]

    def getKeyFunctionMap(self, key_app):
        return self.key_function_maps.get(key_app)

    def setTableColumns(self, key_app, new_table_columns):
        self.table_columns[key_app] = TableColumns(new_table_columns)

    def setKeyFunctionMap(self, key_app, new_key_map):
        self.key_function_maps[key_app] = KeyFunctionMap(new_key_map)