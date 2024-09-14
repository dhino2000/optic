# キーボードでtableを操作
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import Qt
from ..gui.table_setup import setupWidgetROITable
from ..visualization.info_visual import updateROIPropertyDisplay, updateROICountDisplay

class TableControl:
    def __init__(self, key_app, q_table, data_manager, widget_manager, config_manager, control_manager):
        """
        key_app          : str
        q_table          : QTableWidget 
        table_columns    : config.app_config.TableColumns
        key_function_map : config.app_config.KeyFunctionMap
        """
        self.key_app:           str = key_app
        self.q_table                = q_table
        self.data_manager           = data_manager
        self.widget_manager         = widget_manager
        self.config_manager         = config_manager
        self.control_manager        = control_manager
        self.table_columns          = self.config_manager.getTableColumns(self.key_app)
        self.key_function_map       = self.config_manager.getKeyFunctionMap(self.key_app).getAllMappings()
        self.selected_row:      int = 0
        self.selected_column:   int = 0
        self.len_row:           int = 0

    def setupWidgetROITable(self, key_app):
        self.setLenRow(len(self.data_manager.dict_Fall[key_app]["stat"])) # for Suite2p
        self.q_table = setupWidgetROITable(self.q_table, self.len_row, self.table_columns.getColumns(), key_event_ignore=True)
        self.setKeyPressEvent()

    def updateWidgetROITable(self):
        self.q_table.clear()
        self.q_table = setupWidgetROITable(self.q_table, self.len_row, self.table_columns.getColumns(), key_event_ignore=True)

    """
    get Functions
    """
    def getSelectedRow(self):
        return self.selected_row

    def getSelectedColumn(self):
        return self.selected_column
    
    def getLenRow(self):
        return self.len_row

    """
    set Functions
    """
    def setSelectedRow(self, row):
        self.selected_row = row

    def setSelectedColumn(self, column):
        self.selected_column = column

    def setLenRow(self, len_row):
        self.len_row = len_row

    def setKeyPressEvent(self):
        self.q_table.keyPressEvent = self.keyPressEvent

    def setTableColumns(self, table_columns):
        self.table_columns = table_columns
    """
    shared_attr Functions
    """
    def setSharedAttr_SelectedROI(self, roi_id):
        self.control_manager.setSharedAttr(self.key_app, 'selected_roi_id', roi_id)
        updateROIPropertyDisplay(self.control_manager, self.data_manager, self.widget_manager, self.key_app)

    def getSharedAttr_SelectedROI(self):
        return self.control_manager.getSharedAttr(self.key_app, 'selected_roi_id')
    
    def keyPressEvent(self, event):
        if self.selected_row is not None and event.key() in self.key_function_map:
            action = self.key_function_map[event.key()]
            self.executeAction(action)
            self.q_table.setCurrentCell(self.selected_row, self.selected_column)
            self.q_table.scrollToItem(self.q_table.item(self.selected_row, self.selected_column))

    def executeAction(self, action):
        action_type = action[0] # radio, checkbox, move
        if action_type == 'move':
            move_type = action[1] # cell_type, skip_checked, skip_unchecked, selected_type
            step = action[2]
            self.moveCell(move_type, step) 
        elif action_type == 'toggle':
            col_order = action[1]
            self.toggleColumn(self.selected_row, col_order)
        updateROICountDisplay(self.widget_manager, self.config_manager, self.key_app)

    """
    Function of executeAction
    """
    # move table cell
    def moveCell(self, move_type, step):
        if move_type == 'up':
            self.selected_row = max(0, self.selected_row - step)
        elif move_type == 'down':
            self.selected_row = min(self.q_table.rowCount() - 1, self.selected_row + step)
        elif move_type == 'left':
            self.selected_column = max(0, self.selected_column - step)
        elif move_type == 'right':
            self.selected_column = min(self.q_table.columnCount() - 1, self.selected_column + step)
        elif move_type == 'cell_type':
            self.moveToSameCellType(self.selected_row, step)
        elif move_type == 'skip_checked':
            self.moveSkippingChecked(self.selected_row, step, True)
        elif move_type == 'skip_unchecked':
            self.moveSkippingChecked(self.selected_row, step, False)
        # elif move_type == 'selected_type':
            # self.moveToSelectedType(self.selected_row, step)

    # toggle radiobutton, checkbox
    def toggleColumn(self, row, col_order):
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['order'] == col_order:
                if col_info['type'] == 'celltype':
                    radio_button = self.q_table.cellWidget(row, col_order)
                    if isinstance(radio_button, QRadioButton):
                        radio_button.setChecked(True)
                elif col_info['type'] == 'checkbox':
                    check_box_item = self.q_table.item(row, col_order)
                    if check_box_item:
                        check_box_item.setCheckState(Qt.Unchecked if check_box_item.checkState() == Qt.Checked else Qt.Checked)
                break

    # move Neuron->Neuron, Astrocyte->Astrocyte
    def moveToSameCellType(self, start_row, direction):
        current_cell_type = self.getCurrentCellType(start_row)
        total_rows = self.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break
            if self.getCurrentCellType(new_row) == current_cell_type:
                self.selected_row = new_row
                return
            
    # move row with skipping "Check checked" or "Check unchecked"
    def moveSkippingChecked(self, start_row, direction, skip_checked):
        total_rows = self.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break
            if self.getRowChecked(new_row) != skip_checked:
                self.selected_row = new_row
                return
            
    """
    Sub Function
    """
            
    # get celltype of current row, Neruon/Astrocyte/...
    def getCurrentCellType(self, row):
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['type'] == 'celltype':
                radio_button = self.q_table.cellWidget(row, col_info['order'])
                if radio_button and radio_button.isChecked():
                    return col_name
        return None

    # detect "Check" is checked or not
    def getRowChecked(self, row):
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['type'] == 'checkbox' and col_name == 'Check':
                check_box_item = self.q_table.item(row, col_info['order'])
                return check_box_item.checkState() == Qt.Checked if check_box_item else False
        return False