# アプリのconfigをまとめたManagerクラス
from .app_config import AppSettings

class ConfigManager:
    def __init__(self):
        self.dict_tablecol = {}
        self.key_function_map = {}
        self.gui_defaults = {}
        self.current_app = None

    def loadDefaultAppSettings(self):
        # AppSettingsからデフォルト設定を読み込む
        self.key_function_map = AppSettings.getKeyFunctionMap()
        self.gui_defaults = AppSettings.getGuiDefaults()

    def setCurrentApp(self, app_name):
        self.current_app = app_name
        # 現在のアプリに応じて設定を更新
        AppSettings.setCurrentApp(app_name)
        self.loadDefaultAppSettings()

    def setDictTableColumns(self, key_dict_tablecol):
        self.dict_tablecol[key_dict_tablecol] = AppSettings.getTableColumns()
        return self.dict_tablecol[key_dict_tablecol]