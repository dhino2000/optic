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
        self.selected_row = None
        self.key_function_map = key_function_map

    