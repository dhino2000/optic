from typing import Dict, Any, List
from copy import deepcopy 

class TableColumns:
    def __init__(self, columns_config: Dict[str, Dict[str, Any]]):
        self._columns = deepcopy(columns_config)
        self._column_order = sorted(self._columns.keys(), key=lambda x: self._columns[x]['order'])

    def getColumns(self) -> Dict[str, Dict[str, Any]]:
        return deepcopy(self._columns)

    def getColumnOrder(self) -> List[str]:
        return self._column_order

    def getCellTypeColumns(self) -> List[str]:
        return [col for col, config in self._columns.items() 
                if config.get('type') == 'radio' and config.get('group') == 'celltype']