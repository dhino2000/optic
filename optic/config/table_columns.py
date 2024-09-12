from typing import Dict, Any, List
from copy import deepcopy
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

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
    
    def openConfigWindow(self, parent=None):
        config_window = TableColumnConfigWindow(parent, self)
        config_window.exec_()
    
# Table Columns Config
class TableColumnConfigWindow(QDialog):
    def __init__(self, parent=None, table_columns=None):
        super().__init__(parent)
        self.table_columns = table_columns
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Table Column Configuration')
        layout = QVBoxLayout()
        
        label = QLabel("This is the Table Column Configuration window.")
        layout.addWidget(label)

        self.setLayout(layout)