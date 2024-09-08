# アプリのconfigをまとめたManagerクラス
from ..config.app_config import AppSettings

class ConfigManager:
    def __init__(self):
        self.current_app = None
        self.table_columns = None
        self.key_function_map = None
        self.gui_defaults = None

    def setCurrentApp(self, app_name):
        AppSettings.setCurrentApp(app_name)
        self.current_app = app_name
        self.table_columns = AppSettings.getTableColumns()
        self.key_function_map = AppSettings.getKeyFunctionMap()
        self.gui_defaults = AppSettings.getGuiDefaults()

    def getTableColumns(self):
        return self.table_columns

    def getKeyFunctionMap(self):
        return self.key_function_map

    def getGuiDefaults(self):
        return self.gui_defaults