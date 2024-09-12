from typing import Dict, Any, List
from copy import deepcopy


class TableColumns:
    def __init__(self, columns_config: Dict[str, Dict[str, Any]]):
        self._columns = deepcopy(columns_config)

    def getColumns(self) -> Dict[str, Dict[str, Any]]:
        return deepcopy(self._columns)
    
    def openConfigWindow(self, parent, gui_defaults):
        from .table_columns_config import TableColumnConfigWindow
        config_window = TableColumnConfigWindow(parent, self, gui_defaults)
        config_window.exec_()