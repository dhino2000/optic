from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QRadioButton, QButtonGroup, QMessageBox, QAbstractItemView, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import numpy as np
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
        if not self.config_manager.getKeyFunctionMap(self.app_key) is None:
            self.key_function_map:    Dict[Qt.Key, Any] = self.config_manager.getKeyFunctionMap(self.app_key).getAllMappings()
        else:
            self.key_function_map                       = {}
        self.groups_celltype:   Dict[int, QButtonGroup] = {}
        self.selected_row:                          int = 0
        self.selected_column:                       int = 0
        self.len_row:                               int = 0
        # for Microglia Tracking
        self.plane_t:                               int = 0

    def setupWidgetROITable(self, app_key: str) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.setLenRow(len(self.data_manager.getStat(self.app_key))) # for Suite2p
        self.q_table, self.groups_celltype = setupWidgetROITable(self.q_table, self.len_row, self.table_columns, key_event_ignore=True)
        self.setKeyPressEvent()
        self.initalizeSharedAttr_ROIDisplay()
        self.setROICellTypeFromArray(self.data_manager.getDictFall("pri")["iscell"][:,0], "Neuron", "Not_Cell") # set celltype with "iscell" array
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def setupWidgetDynamicTable(self, app_key: str) -> None:
        from ..gui.table_setup import setupWidgetDynamicTable
        self.q_table, self.groups_celltype = setupWidgetDynamicTable(self.q_table, self.table_columns, self.len_row)

    def updateWidgetROITable(self) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.q_table.clear()
        self.q_table = setupWidgetROITable(self.q_table, self.len_row, self.table_columns, key_event_ignore=True)

    def updateWidgetDynamicTableWithT(self, dict_roi_matching: Dict[int, Optional[int]], row_count:int, has_roi_id_match: bool) -> None:
        from ..gui.table_setup import applyDictROIMatchingToTable
        self.q_table.setRowCount(0) # initialize table
        applyDictROIMatchingToTable(self.q_table, self.table_columns, dict_roi_matching, row_count, has_roi_id_match)

    # change table cell selection
    def onSelectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        if selected.indexes():
            row: int = self.q_table.currentRow()
            column: int = self.q_table.currentColumn()
            
            self.setSelectedRow(row)
            self.setSelectedColumn(column)
            self.setSharedAttr_ROISelected(row)

    def onSelectionChangedWithTracking(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        if selected.indexes():
            row: int = self.q_table.currentRow()
            column: int = self.q_table.currentColumn()
            
            self.setSelectedRow(row)
            self.setSelectedColumn(column)
            self.setSharedAttr_ROISelected(row)
            # for ROI tracking
            id_roi_match = self.getMatchId(row)
            self.setSharedAttr_ROIMatch(id_roi_match)

    """
    get Functions
    """
    def getSelectedRow(self) -> int:
        return self.selected_row

    def getSelectedColumn(self) -> int:
        return self.selected_column
    
    def getLenRow(self) -> int:
        return self.len_row
    
    # if "Cell ID Match" column is empty, return None
    def getMatchId(self, roi_id: int) -> Optional[int]:
        try:
            col_id_match = self.table_columns.getColumns()['Cell_ID_Match']['order'] # hardcoded !!!
            id = int(self.q_table.item(roi_id, col_id_match).text())
            return id
        except (KeyError, AttributeError, ValueError):
            return None
        
    def getPlaneT(self) -> int:
        return self.plane_t
    """
    set Functions
    """
    def setSelectedRow(self, row: int) -> None:
        if not isinstance(row, int) or row < 0 or row >= self.len_row:
            return
        else:
            self.selected_row = row

    def setSelectedColumn(self, column: int) -> None:
        self.selected_column = column

    def setLenRow(self, len_row: int) -> None:
        self.len_row = len_row

    def setKeyPressEvent(self) -> None:
        self.q_table.keyPressEvent = self.keyPressEvent

    def setTableColumns(self, table_columns: TableColumns) -> None:
        self.table_columns = table_columns

    def setPlaneT(self, plane_t: int) -> None:
        self.plane_t = plane_t
    """
    shared_attr Functions
    roi_selected_id: Current selected ROI ID
    roi_match_id: Current matched ROI ID
    roi_display: Which ROIs should be displayed
    display_celltype: Which celltype should be displayed
    """
    def setSharedAttr_ROISelected(self, roi_id: int) -> None:
        if not isinstance(roi_id, int) or roi_id < 0 or roi_id >= self.len_row:
            return
        else:
            self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', roi_id)
            updateROIPropertyDisplay(self.control_manager, self.data_manager, self.widget_manager, self.app_key)

    def getSharedAttr_ROISelected(self) -> int:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')
    
    def setSharedAttr_ROIMatch(self, roi_id: int) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'roi_match_id', roi_id)

    def getSharedAttr_ROIMatch(self) -> int:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_match_id')
    
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
        elif move_type == 'selected_type':
            self.moveToSelectedType(self.selected_row, step)

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
            
    # if "Neuron" radiobutton is checked, move to next "Neuron"
    def moveToSelectedType(self, start_row: int, direction: Literal[-1, 1]) -> None:
        roi_display = self.getSharedAttr_ROIDisplay()
        total_rows = self.q_table.rowCount()
        new_row = start_row

        while True:
            new_row = (new_row + direction) % total_rows
            if new_row == start_row:
                break
            if roi_display[new_row]:
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
            if col_info['type'] == 'checkbox' and col_name == 'Check': # hardcoded !!!
                check_box_item = self.q_table.item(row, col_info['order'])
                return check_box_item.checkState() == Qt.Checked if check_box_item else False
        return False
    
    """
    Button-binding Function
    """
    # set Selected ROIs same celltype (Neuron, Not Cell, ...)
    def setSelectedROISameCelltype(
            self, 
            celltype: str,
            idx_min: Optional[int] = None,
            idx_max: Optional[int] = None
        ) -> None:
        checkbox_columns = self.getCheckboxColumns()
        skip_states = {}
        
        # Check if user wants to skip checked ROIs for each checkbox column
        for column in checkbox_columns:
            result = showConfirmationDialog(
                self.q_table,
                'Confirmation',
                f"Skip {column} checked ROI ? (ROI {idx_min} to {idx_max})"
            )
            if result == QMessageBox.Yes:
                skip_states[column] = self.getCheckboxStates(column)
            elif result == QMessageBox.Cancel:
                return  # 処理を中断
            else:  # No の場合
                skip_states[column] = [False] * self.len_row
                
        col_order: int = self.table_columns.getColumns()[celltype]["order"]
        for row in range(idx_min, idx_max+1):
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
    def toggleSelectedROICheckbox(
            self, 
            checkbox: str, 
            toggle: bool,
            idx_min: Optional[int] = None,
            idx_max: Optional[int] = None
        ) -> None:
        dict_text = {True: "Check", False: "Uncheck"}
        result = showConfirmationDialog(
            self.q_table,
            'Confirmation',
            f"{dict_text[toggle]} {checkbox} for ROI {idx_min} to {idx_max} ?"
        )
        if result == QMessageBox.Yes:
            col_index = self.table_columns.getColumns()[checkbox]['order']
            check_state = Qt.Checked if toggle else Qt.Unchecked

            for row in range(idx_min, idx_max+1):
                item = self.q_table.item(row, col_index)
                if item:
                    item.setCheckState(check_state)
        
    # Filter ROIs, set celltype radiobutton "Not Cell" (column with the highest order)
    def filterROI(self, thresholds: Dict[str, Tuple[float, float]]) -> None:
        result = showConfirmationDialog(
            self.q_table,
            'Confirmation',
            f"Filter ROIs ?",
        )
        if result == QMessageBox.Yes:
            celltype_columns = [col for col, info in self.table_columns.getColumns().items() if info['type'] == 'celltype']
            target_celltype = max(celltype_columns, key=lambda col: self.table_columns.getColumns()[col]['order']) # Not_Cell column should be the last column of "celltype" columns
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
    """
    Other Functions
    """
    # set ROI celltype with 0/1 array
    def setROICellTypeFromArray(
        self,
        array_bool: np.ndarray[bool],
        celltype_pos: str = "Neuron",
        celltype_neg: str = "Not_Cell"
    ) -> None:
        # Get column indices
        columns = self.table_columns.getColumns()
        pos_col_idx = columns.get(celltype_pos, {}).get('order')
        neg_col_idx = columns.get(celltype_neg, {}).get('order')

        # Update classifications
        for row, is_positive in enumerate(array_bool):
            target_col = pos_col_idx if is_positive else neg_col_idx
            radio_button = self.q_table.cellWidget(row, target_col)
            if radio_button:
                radio_button.setChecked(True)
                self.changeRadiobuttonOfTable(row)
                
        # Update display
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    # update Cell ID Match column values based on matching dictionary
    def updateMatchedROIPairs(self, matches: Dict[int, int]) -> None:
        col_id = self.table_columns.getColumns()['Cell_ID']['order'] # hardcoded !!!
        col_id_match = self.table_columns.getColumns()['Cell_ID_Match']['order'] # hardcoded !!!
        
        for row in range(self.q_table.rowCount()):
            try:
                cell_id = int(self.q_table.item(row, col_id).text())
                if cell_id in matches:
                    # Create new item with the matching ID
                    match_item = QTableWidgetItem(str(matches[cell_id]))
                    self.q_table.setItem(row, col_id_match, match_item)
                else:
                    # Clear the match if no matching exists
                    self.q_table.setItem(row, col_id_match, QTableWidgetItem(""))
            except (ValueError, AttributeError):
                continue

    # if "Match Cell ID" is filled, get ROI pair
    def getMatchedROIPairs(self, table_control_sec: TableControl) -> List[Tuple[int, int]]:
        matched_pairs = []

        col_id = self.table_columns.getColumns()['Cell_ID']['order'] # hardcoded !!!
        col_id_match = self.table_columns.getColumns()['Cell_ID_Match']['order'] # hardcoded !!!
        
        for row in range(self.len_row):
            try:
                cell_id = int(self.q_table.item(row, col_id).text())
                cell_id_match_item = self.q_table.item(row, col_id_match)
                
                if not cell_id_match_item or not cell_id_match_item.text().strip():
                    continue
                    
                cell_id_match = int(cell_id_match_item.text())
                # Skip invalid values, below 0 or above the number of "sec" ROIs
                if (cell_id_match < 0 or cell_id_match >= table_control_sec.len_row):
                    continue
                
                matched_pairs.append((cell_id, cell_id_match))
            except (ValueError, AttributeError):
                continue
                
        return matched_pairs