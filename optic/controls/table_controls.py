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

    def keyPressEvent(self, event):
        if self.selected_row is not None and event.key() in self.key_function_map:
            action = self.key_function_map[event.key()]
            self.executeAction(action)
            self.q_table.setCurrentCell(self.selected_row, 0)
            self.q_table.scrollToItem(self.q_table.item(self.selected_row, 0))

    def onSelectionChanged(self, selected, deselected):
        if selected.indexes():
            self.selected_row = selected.indexes()[0].row()
            self.selected_column = selected.indexes()[0].column()

    def executeAction(self, action):
        action_type = action[0] # radio, checkbox, move
        if action_type == 'radio':
            self.selectRadioButton(self.selected_row, action[1]) # row, column
        elif action_type == 'checkbox':
            self.toggleCheckBox(self.selected_row, action[1]) # row, column

    # select radiobutton
    def selectRadioButton(self, row, column):
        for col_name, col_info in self.dict_tablecol.items():
            if col_info['type'] == 'radio' and col_info['order'] == column:
                radio_button = self.q_table.cellWidget(row, column)
                if isinstance(radio_button, QRadioButton):
                    radio_button.setChecked(True)
                break
    
    # check/uncheck checkbox
    def toggleCheckBox(self, row, column):
        for col_name, col_info in self.dict_tablecol.items():
            if col_info['type'] == 'checkbox' and col_info['order'] == column:
                check_box_item = self.q_table.item(row, column)
                if check_box_item:
                    check_box_item.setCheckState(Qt.Unchecked if check_box_item.checkState() == Qt.Checked else Qt.Checked)
                break