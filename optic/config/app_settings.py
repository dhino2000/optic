from .gui_defaults import GuiDefaults
from .table_columns import TableColumns
from .key_function_map import KeyFunctionMap

class AppSettings:
    CURRENT_APP = "SUITE2P_ROI_CHECK"

    @classmethod
    def getTableColumns(cls, app_name=None, app_key=None):
        app_name = app_name or cls.CURRENT_APP
        columns_config = getattr(GuiDefaults, app_name)["TABLE_COLUMNS"]
        if app_key:
            return TableColumns(columns_config.get(app_key, {}))
        return {k: TableColumns(v) for k, v in columns_config.items()}

    @classmethod
    def getKeyFunctionMap(cls, app_name=None, app_key=None):
        app_name = app_name or cls.CURRENT_APP
        key_function_config = getattr(GuiDefaults, app_name)["KEY_FUNCTION_MAP"]
        if app_key:
            return KeyFunctionMap(key_function_config.get(app_key, {}))
        return {k: KeyFunctionMap(v) for k, v in key_function_config.items()}

    @classmethod
    def getGuiDefaults(cls, app_name=None):
        app_name = app_name or cls.CURRENT_APP
        return getattr(GuiDefaults, app_name)

    @classmethod
    def setCurrentApp(cls, app_name):
        if hasattr(GuiDefaults, app_name):
            cls.CURRENT_APP = app_name
        else:
            raise ValueError(f"Invalid app name: {app_name}")