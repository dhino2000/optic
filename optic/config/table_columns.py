from typing import Dict, Any, List
from copy import deepcopy

class TableColumns:
    def __init__(self, columns_config: Dict[str, Dict[str, Any]]):
        self._columns = deepcopy(columns_config)

    def getColumns(self) -> Dict[str, Dict[str, Any]]:
        return deepcopy(self._columns)
    
    def setColumns(self, new_columns: Dict[str, Dict[str, Any]]):
        self._columns = new_columns
        self._column_order = sorted(self._columns.keys(), key=lambda x: self._columns[x]['order'])
    
    def openConfigWindow(self, parent, gui_defaults):
        from ..dialog.table_columns_config import TableColumnConfigDialog
        config_window = TableColumnConfigDialog(parent, self, gui_defaults)
        config_window.exec_()