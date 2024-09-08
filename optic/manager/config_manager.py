# アプリのconfigをまとめたManagerクラス
from ..config.app_settings import AppSettings

class ConfigManager:
    def __init__(self):
        self.current_app = None
        self.gui_defaults = None
        self.table_columns = None
        self.key_function_map = None

    def setCurrentApp(self, app_name):
        self.current_app = app_name
        self.gui_defaults = AppSettings.getGuiDefaults(app_name)
        self.table_columns = AppSettings.getTableColumns(app_name)
        self.key_function_map = AppSettings.getKeyFunctionMap(app_name)

    def getGuiDefaults(self):
        return self.gui_defaults

    def getTableColumns(self, app_key):
        return self.table_columns.get(app_key)

    def getKeyFunctionMap(self, app_key):
        return self.key_function_map.get(app_key)