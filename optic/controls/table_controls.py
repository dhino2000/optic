# キーボードでtableを操作
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import Qt

class TableControls:
    def __init__(self, q_table, dict_tablecol, key_function_map):
        """
        q_table          : QTableWidget 
        dict_tablecol    : config.app_config.TableColumns
        key_function_map : config.app_config.KeyFunctionMap
        """
        self.q_table = q_table
        self.dict_tablecol = dict_tablecol
        self.selected_row = 0
        self.selected_column = 0
        self.key_function_map = key_function_map
        # 選択を変更したときの関数
        self.q_table.selectionModel().selectionChanged.connect(self.onSelectionChanged)


    def onSelectionChanged(self, selected, deselected):
        if selected.indexes():
            self.selected_row = selected.indexes()[0].row()
            self.selected_column = selected.indexes()[0].column()
    