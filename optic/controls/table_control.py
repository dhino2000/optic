from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QRadioButton, QButtonGroup, QMessageBox, QAbstractItemView, QTableWidget
from PyQt5.QtCore import Qt
from ..visualization.info_visual import updateROIPropertyDisplay, updateROICountDisplay
from ..utils.dialog_utils import showConfirmationDialog
from ..utils.info_utils import extractRangeValues

class TableControl:
    def __init__(
            self, 
            app_key         : str, 
            q_table         : QTableWidget,             
            data_manager    : DataManager, 
            widget_manager  : WidgetManager, 
            config_manager  : ConfigManager, 
            control_manager : ControlManager,
        ):
        self.app_key                                    = app_key
        self.q_table                                    = q_table
        self.data_manager                               = data_manager
        self.widget_manager                             = widget_manager
        self.config_manager                             = config_manager
        self.control_manager                            = control_manager
        self.table_columns:                TableColumns = self.config_manager.getTableColumns(self.app_key)
        self.key_function_map:        Dict[Qt.Key, Any] = self.config_manager.getKeyFunctionMap(self.app_key).getAllMappings()
        self.groups_celltype:   Dict[int, QButtonGroup] = {}
        self.selected_row:                          int = 0
        self.selected_column:                       int = 0
        self.len_row:                               int = 0

    def setupWidgetROITable(self, app_key: str) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.setLenRow(len(self.data_manager.getStat(self.app_key))) # for Suite2p
        self.q_table, self.groups_celltype = setupWidgetROITable(self.q_table, self.len_row, self.table_columns.getColumns(), key_event_ignore=True)
        self.setKeyPressEvent()
        self.initalizeSharedAttr_ROIDisplay()
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def updateWidgetROITable(self) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.q_table.clear()
        self.q_table = setupWidgetROITable(self.q_table, self.len_row, self.table_columns.getColumns(), key_event_ignore=True)

    # change table cell selection
    def onSelectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        if selected.indexes():
            row: int = self.q_table.currentRow()
            column: int = self.q_table.currentColumn()
            
            self.setSelectedRow(row)
            self.setSelectedColumn(column)
            self.setSharedAttr_ROISelected(row)
    """
    get Functions
    """
    def getSelectedRow(self) -> int:
        return self.selected_row

    def getSelectedColumn(self) -> int:
        return self.selected_column
    
    def getLenRow(self) -> int:
        return self.len_row

    """
    set Functions
    """
    def setSelectedRow(self, row: int) -> None:
        self.selected_row = row

    def setSelectedColumn(self, column: int) -> None:
        self.selected_column = column

    def setLenRow(self, len_row: int) -> None:
        self.len_row = len_row

    def setKeyPressEvent(self) -> None:
        self.q_table.keyPressEvent = self.keyPressEvent

    def setTableColumns(self, table_columns: TableColumns) -> None:
        self.table_columns = table_columns
    """
    shared_attr Functions
    roi_selected_id: Current selected ROI ID
    roi_display: Which ROIs should be displayed
    display_celltype: Which celltype should be displayed
    """
    def setSharedAttr_ROISelected(self, roi_id: int) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', roi_id)
        updateROIPropertyDisplay(self.control_manager, self.data_manager, self.widget_manager, self.app_key)

    def getSharedAttr_ROISelected(self) -> int:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')
    
    def setSharedAttr_ROIDisplay(self, roi_display: Dict[int, bool]) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'roi_display', roi_display)

    def getSharedAttr_ROIDisplay(self) -> Dict[int, bool]:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_display')

    def initalizeSharedAttr_ROIDisplay(self) -> None:
        roi_display = {roi_id: True for roi_id in range(self.len_row)}
        self.control_manager.setSharedAttr(self.app_key, 'roi_display', roi_display)

    def setSharedAttr_DisplayCelltype(self, roi_display_type: str) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'display_celltype', roi_display_type)

    def getSharedAttr_DisplayCelltype(self) -> str:
        return self.control_manager.getSharedAttr(self.app_key, 'display_celltype')

    # with dict_buttongroup["{app_key}_display_celltype"] change
    def updateROIDisplayWithCelltype(self, roi_display_type: str) -> None:
        roi_display = self.getSharedAttr_ROIDisplay()
        for roi_id in roi_display.keys():
            if roi_display_type == 'All ROI':
                roi_display[roi_id] = True
            elif roi_display_type == 'None':
                roi_display[roi_id] = False
            else:
                roi_display[roi_id] = (self.getCurrentCellType(roi_id) == roi_display_type)
        self.setSharedAttr_DisplayCelltype(roi_display_type)
        self.setSharedAttr_ROIDisplay(roi_display)

    # with table's "celltype" radiobutton change
    def changeRadiobuttonOfTable(self, row: int) -> None:
        roi_display = self.getSharedAttr_ROIDisplay()
        current_display_type = self.getSharedAttr_DisplayCelltype()
        
        if current_display_type not in ['All ROI', 'None']:
            new_cell_type = self.getCurrentCellType(row)
            roi_display[row] = (new_cell_type == current_display_type)
            self.setSharedAttr_ROIDisplay(roi_display)

    # with View mousePressEvent
    def updateSelectedROI(self, roi_id: int) -> None:
        if roi_id is not None:
            self.q_table.selectRow(roi_id)
            self.setSelectedRow(roi_id)
            self.setSharedAttr_ROISelected(roi_id)
            self.q_table.scrollToItem(self.q_table.item(roi_id, 0), QAbstractItemView.PositionAtTop)
            self.q_table.setCurrentCell(roi_id, 0)

    """
    KeyPressEvent
    """
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.selected_row is not None and event.key() in self.key_function_map:
            action = self.key_function_map[event.key()]
            self.executeAction(action)
            self.q_table.setCurrentCell(self.selected_row, self.selected_column)
            self.q_table.scrollToItem(self.q_table.item(self.selected_row, self.selected_column))

    def executeAction(self, action: Tuple) -> None:
        action_type = action[0] # radio, checkbox, move
        if action_type == 'move':
            move_type = action[1] # cell_type, skip_checked, skip_unchecked, selected_type
            step = action[2]
            self.moveCell(move_type, step) 
        elif action_type == 'toggle':
            col_order = action[1]
            self.toggleColumn(self.selected_row, col_order)
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    """
    Function of executeAction
    """
    # move table cell
    def moveCell(self, move_type: str, step: Literal[-1, 1]) -> None:
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
    def toggleColumn(self, row: int, col_order: int) -> None:
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['order'] == col_order:
                if col_info['type'] == 'celltype':
                    button_group = self.groups_celltype.get(row)
                    if button_group:
                        for button in button_group.buttons():
                            if self.q_table.cellWidget(row, col_order) == button:
                                button.setChecked(True)
                                self.changeRadiobuttonOfTable(row)
                                break
                elif col_info['type'] == 'checkbox':
                    check_box_item = self.q_table.item(row, col_order)
                    if check_box_item:
                        check_box_item.setCheckState(Qt.Unchecked if check_box_item.checkState() == Qt.Checked else Qt.Checked)
                break

    # move Neuron->Neuron, Astrocyte->Astrocyte
    def moveToSameCellType(self, start_row: int, direction: Literal[-1, 1]) -> None:
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
    def moveSkippingChecked(self, start_row: int, direction: Literal[-1, 1], skip_checked: bool) -> None:
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
            
    # get celltype of radiobutton, Neruon/Astrocyte/...
    def getCurrentCellType(self, row: int) -> str:
        button_group = self.groups_celltype.get(row)
        if button_group:
            checked_button = button_group.checkedButton()
            if checked_button:
                for col_name, col_info in self.table_columns.getColumns().items():
                    if col_info['type'] == 'celltype' and self.q_table.cellWidget(row, col_info['order']) == checked_button:
                        return col_name
        return None

    # detect "Check" is checked or not
    def getRowChecked(self, row: int) -> bool:
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['type'] == 'checkbox' and col_name == 'Check':
                check_box_item = self.q_table.item(row, col_info['order'])
                return check_box_item.checkState() == Qt.Checked if check_box_item else False
        return False
    
    """
    Button-binding Function
    """
    # set All ROIs same celltype (Neuron, Not Cell, ...)
    def setAllROISameCelltype(self, celltype: str) -> None:
        checkbox_columns = self.getCheckboxColumns()
        skip_states = {}
        
        for column in checkbox_columns:
            result = showConfirmationDialog(
                self.q_table,
                'Confirmation',
                f"Skip {column} checked ROI?"
            )
            if result == QMessageBox.Yes:
                skip_states[column] = self.getCheckboxStates(column)
            elif result == QMessageBox.Cancel:
                return  # 処理を中断
            else:  # No の場合
                skip_states[column] = [False] * self.len_row
            
        col_order: int = self.table_columns.getColumns()[celltype]["order"]
        for row in range(self.len_row):
            if all(not skip_states[col][row] for col in checkbox_columns):
                button_group = self.groups_celltype.get(row)
                if button_group:
                    button = self.q_table.cellWidget(row, col_order)
                    if isinstance(button, QRadioButton):
                        button.setChecked(True)
                        self.changeRadiobuttonOfTable(row)
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def getCheckboxColumns(self) -> List[str]:
        return [col_name for col_name, col_info in self.table_columns.getColumns().items() if col_info['type'] == 'checkbox']

    def getCheckboxStates(self, column_name: str) -> List[bool]:
        col_info = self.table_columns.getColumns()[column_name]
        if col_info['type'] != 'checkbox':
            return []
        
        states = []
        for row in range(self.len_row):
            item = self.q_table.item(row, col_info['order'])
            if item:
                states.append(item.checkState() == Qt.Checked)
            else:
                states.append(False)
        return states
    
    # toggle "Checkbox" of All ROIs
    def toggleAllROICheckbox(self, checkbox: str, toggle: bool) -> None:
        dict_text = {True: "Check", False: "Uncheck"}
        result = showConfirmationDialog(
            self.q_table,
            'Confirmation',
            f"{dict_text[toggle]} All {checkbox} ?"
        )
        if result == QMessageBox.Yes:
            col_index = self.table_columns.getColumns()[checkbox]['order']
            check_state = Qt.Checked if toggle else Qt.Unchecked

            for row in range(self.len_row):
                item = self.q_table.item(row, col_index)
                if item:
                    item.setCheckState(check_state)
        else:
            return
        
    # Filter ROIs, set celltype radiobutton "Not Cell" (column with the highest order)
    def filterROI(self, thresholds: Dict[str, Tuple[float, float]]) -> None:
        result = showConfirmationDialog(
            self.q_table,
            'Confirmation',
            f"Filter ROIs ?",
        )
        if result == QMessageBox.Yes:
            celltype_columns = [col for col, info in self.table_columns.getColumns().items() if info['type'] == 'celltype']
            target_celltype = max(celltype_columns, key=lambda col: self.table_columns.getColumns()[col]['order'])
            target_column = self.table_columns.getColumns()[target_celltype]['order']

            for row in range(self.q_table.rowCount()):
                roi_stat = self.data_manager.getStat(self.app_key)[row]
                if not all(min_val <= roi_stat[param] <= max_val for param, (min_val, max_val) in thresholds.items()):
                    radio_button: QRadioButton = self.q_table.cellWidget(row, target_column)
                    if radio_button:
                        radio_button.setChecked(True)
                        self.changeRadiobuttonOfTable(row)
            updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)
        else:
            return
    # get thresholds of ROI filter
    def getThresholdsOfROIFilter(self) -> Dict[str, Tuple[float, float]]:
        thresholds = {}
        q_lineedits = {key: self.widget_manager.dict_lineedit[f"{self.app_key}_roi_filter_{key}"] for key in self.config_manager.gui_defaults["ROI_THRESHOLDS"].keys()}
        for key, q_lineedit in q_lineedits.items():
            thresholds[key] = extractRangeValues(q_lineedit.text())
        return thresholds