from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QRadioButton, QButtonGroup, QMessageBox, QAbstractItemView, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import numpy as np
from ..handlers.table_handler import TableHandler
from ..visualization.info_visual import updateROIPropertyDisplay, updateROICountDisplay
from ..utils.dialog_utils import showConfirmationDialog
from ..utils.info_utils import extractRangeValues
from ..visualization.view_visual_roi import shouldSkipROI
from ..config.constants import Extension


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
            self.key_function_map   : Dict[Qt.Key, Any] = self.config_manager.getKeyFunctionMap(self.app_key).getAllMappings()
        else:
            self.key_function_map                       = {}
        self.groups_celltype        : Dict[int, QButtonGroup] = {}
        self.selected_row           : int = 0
        self.selected_column        : int = 0
        self.len_row                : int = 0
        # for Microglia Tracking
        self.plane_t                : int = 0

        # set TableHandler
        self.table_handler:                TableHandler = TableHandler(self)

    def setupWidgetROITable(self, app_key: str) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.setLenRow(len(self.data_manager.getStat(self.app_key)))
        self.q_table, self.groups_celltype = setupWidgetROITable(
            self.q_table, 
            self.len_row, 
            self.table_columns,
            data_manager=self.data_manager,
            app_key=self.app_key,
            key_event_ignore=True
        )
        self.setKeyPressEvent()
        self.initalizeSharedAttr_DictROIDisplay()
        self.initalizeSharedAttr_CelltypeVisibility()
        self.initalizeSharedAttr_CheckboxVisibility()
        # set celltype with TableColumns
        celltype_pos = [col_name for col_name in self.table_columns.getColumns().keys() if self.table_columns.getColumns()[col_name]["type"] == "celltype"][0]
        celltype_neg = [col_name for col_name in self.table_columns.getColumns().keys() if self.table_columns.getColumns()[col_name]["type"] == "celltype"][-1]
        self.setROICellTypeFromArray(self.data_manager.getDictFall("pri")["iscell"][:,0], celltype_pos, celltype_neg, app_key)
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def setupWidgetDynamicTable(self, app_key: str) -> None:
        from ..gui.table_setup import setupWidgetDynamicTable
        self.q_table, self.groups_celltype = setupWidgetDynamicTable(self.q_table, self.table_columns, self.len_row)
        self.setKeyPressEvent()

    def updateWidgetROITable(self) -> None:
        from ..gui.table_setup import setupWidgetROITable
        self.q_table.clear()
        self.q_table, groups_celltype = setupWidgetROITable(
            self.q_table, 
            self.len_row, 
            self.table_columns,
            data_manager=self.data_manager,
            app_key=self.app_key,
            key_event_ignore=True
        )

    def updateWidgetDynamicTableWithT(
        self, 
        dict_roi_matching: Dict[str, Dict[int, List[int] | Dict[int, Dict[int, Optional[int]]]]],
        t_plane_pri: int, 
        t_plane_sec: int, 
        use_match: bool = True
    ) -> None:
        from ..gui.table_setup import applyDictROIMatchingToTable
        self.q_table.setRowCount(0)
        applyDictROIMatchingToTable(
            self.q_table,
            self.table_columns,
            dict_roi_matching,
            t_plane_pri,
            t_plane_sec,
            use_match
        )
        self.setLenRow(self.q_table.rowCount())

    def onSelectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        if selected.indexes():
            row: int = self.q_table.currentRow()
            column: int = self.q_table.currentColumn()
            
            self.setSelectedRow(row)
            self.setSelectedColumn(column)

            cell_id = self.getCellIdFromRow(row)
            self.setSharedAttr_ROISelected(cell_id)
            celltype = self.getCelltypeFromColumn(column)
            if celltype is not None and cell_id is not None:
                self.data_manager.dict_roi_celltype[self.app_key][cell_id] = celltype

    def onSelectionChangedWithTracking(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        if selected.indexes():
            row: int = self.q_table.currentRow()
            column: int = self.q_table.currentColumn()
            
            self.setSelectedRow(row)
            self.setSelectedColumn(column)
            
            cell_id = self.getCellIdFromRow(row)
            self.setSharedAttr_ROISelected(cell_id)
            id_roi_match = self.getCellIdMatchFromRow(row)
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
    
    def getCellIdMatchFromRow(self, row: int) -> Optional[int]:
        try:
            id_match_columns = [(col_name, col_info) for col_name, col_info in self.table_columns.getColumns().items() 
                            if col_info['type'] == 'id_match']
            if not id_match_columns:
                return None
                
            col_name, col_info = id_match_columns[0]
            item = self.q_table.item(row, col_info['order'])
            if not item or not item.text().strip():
                return None
                
            return int(item.text())
        except (ValueError, AttributeError):
            return None
        
    def getPlaneT(self) -> int:
        return self.plane_t
    
    def getCellIdFromRow(self, row: int) -> Optional[str]:
        try:
            id_columns = [(col_name, col_info) for col_name, col_info in self.table_columns.getColumns().items() 
                        if col_info['type'] == 'id']
            if not id_columns:
                return None
                
            col_name, col_info = id_columns[0]
            item = self.q_table.item(row, col_info['order'])
            if item:
                return item.text()
            return None
        except (ValueError, AttributeError):
            return None
        
    def getTableColumnNameFromColumn(self, column: int) -> str:
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info["order"] == column:
                return col_name
            
    def getCelltypeFromColumn(self, column: int) -> Optional[str]:
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info["order"] == column:
                if col_info["type"] == "celltype": 
                    return col_name 
                else:
                    return None
                
    """
    set Functions
    """
    def setTableSize(self, width_min: int=0, width_max: int=0, height_min: int=0, height_max: int=0) -> None:
        from ..gui.table_setup import setTableSize
        setTableSize(self.q_table, width_min, width_max, height_min, height_max)

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
        self.q_table.keyPressEvent = self.table_handler.handleKeyPress

    def setTableColumns(self, table_columns: TableColumns) -> None:
        self.table_columns = table_columns

    def setPlaneT(self, plane_t: int) -> None:
        self.plane_t = plane_t

    """
    shared_attr Functions
    """
    def setSharedAttr_ROISelected(self, roi_id: Optional[str]) -> None:
        if roi_id is None:
            self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', None)
        else:
            self.control_manager.setSharedAttr(self.app_key, 'roi_selected_id', roi_id)
            if self.config_manager.current_app == "SUITE2P_ROI_CURATION" or self.config_manager.current_app == "SUITE2P_ROI_TRACKING":
                updateROIPropertyDisplay(
                    self.control_manager, 
                    self.data_manager, 
                    self.widget_manager, 
                    self.app_key,
                    load_caiman=self.data_manager.dict_data_dtype[self.app_key]==Extension.HDF5
                )

    def getSharedAttr_ROISelected(self) -> Optional[str]:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')
    
    def setSharedAttr_ROIMatch(self, roi_id: int) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'roi_match_id', roi_id)

    def getSharedAttr_ROIMatch(self) -> int:
        return self.control_manager.getSharedAttr(self.app_key, 'roi_match_id')
    
    def setSharedAttr_DictROIDisplay(self, dict_roi_display: Dict[str, Dict[str, bool]]) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'dict_roi_display', dict_roi_display)

    def getSharedAttr_DictROIDisplay(self) -> Dict[str, Dict[str, bool]]:
        return self.control_manager.getSharedAttr(self.app_key, 'dict_roi_display')

    def initalizeSharedAttr_DictROIDisplay(self) -> None:
        from ..utils.roi_id_utils import arrayIndexToRoiId
        n_rois_chan1 = self.data_manager.getNROIsChan1(self.app_key)
        dict_roi_display = {}
        for index in range(self.len_row):
            roi_id = arrayIndexToRoiId(index, n_rois_chan1)
            dict_roi_display[roi_id] = {
                "celltype": True,
                "checkbox": True,
            }
        self.control_manager.setSharedAttr(self.app_key, 'dict_roi_display', dict_roi_display)

    def getSharedAttr_CelltypeVisibility(self) -> Dict[str, bool]:
        return self.control_manager.getSharedAttr(self.app_key, 'celltype_visibility')

    def setSharedAttr_CelltypeVisibility(self, celltype_visibility: Dict[str, bool]) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'celltype_visibility', celltype_visibility)

    def getSharedAttr_CheckboxVisibility(self) -> Dict[str, bool]:
        return self.control_manager.getSharedAttr(self.app_key, 'checkbox_visibility')

    def setSharedAttr_CheckboxVisibility(self, checkbox_visibility: Dict[str, bool]) -> None:
        self.control_manager.setSharedAttr(self.app_key, 'checkbox_visibility', checkbox_visibility)

    def initalizeSharedAttr_CelltypeVisibility(self) -> None:
        list_celltype = [col_name for col_name in self.table_columns.getColumns().keys() if self.table_columns.getColumns()[col_name]["type"] == "celltype"]
        celltype_visibility = {celltype: True for celltype in list_celltype}
        self.setSharedAttr_CelltypeVisibility(celltype_visibility)

    def initalizeSharedAttr_CheckboxVisibility(self) -> None:
        list_checkbox = [col_name for col_name in self.table_columns.getColumns().keys() if self.table_columns.getColumns()[col_name]["type"] == "checkbox"]
        checkbox_visibility = {checkbox: False for checkbox in list_checkbox}
        self.setSharedAttr_CheckboxVisibility(checkbox_visibility)

    def updateROIDisplayWithCelltype(self, dict_celltype_visibility: Dict[str, bool]) -> None:
        dict_roi_display = self.getSharedAttr_DictROIDisplay()
        if not any(dict_celltype_visibility.values()):
            for roi_id in dict_roi_display.keys():
                dict_roi_display[roi_id]["celltype"] = False
        else:
            for roi_id in dict_roi_display.keys():
                row = self.getRowFromCellId(roi_id)
                if row is not None:
                    current_celltype = self.getCurrentCellTypeOfRow(row)
                    dict_roi_display[roi_id]["celltype"] = dict_celltype_visibility.get(current_celltype, False)
        
        self.setSharedAttr_DictROIDisplay(dict_roi_display)
        self.setSharedAttr_CelltypeVisibility(dict_celltype_visibility)

    def updateROIDisplayWithCheckbox(self, dict_checkbox_visibility: Dict[str, bool]) -> None:
        dict_roi_display = self.getSharedAttr_DictROIDisplay()
        if not any(dict_checkbox_visibility.values()):
            for roi_id in dict_roi_display.keys():
                dict_roi_display[roi_id]["checkbox"] = True
        else:
            for roi_id in dict_roi_display.keys():
                row = self.getRowFromCellId(roi_id)
                if row is not None:
                    checkbox_states = self.getCheckboxStatesOfRow(row)
                    is_visible = True
                    for checkbox, is_visible_checkbox in dict_checkbox_visibility.items():
                        if is_visible_checkbox and not checkbox_states.get(checkbox, False):
                            is_visible = False
                            break
                    dict_roi_display[roi_id]["checkbox"] = is_visible
        
        self.setSharedAttr_DictROIDisplay(dict_roi_display)
        self.setSharedAttr_CheckboxVisibility(dict_checkbox_visibility)

    def changeRadiobuttonOfTable(self, row: int) -> None:
        dict_roi_display = self.getSharedAttr_DictROIDisplay()
        roi_id = self.getCellIdFromRow(row)
        if roi_id is not None and roi_id in dict_roi_display:
            new_cell_type = self.getCurrentCellTypeOfRow(row)
            dict_celltype_visibility = self.getSharedAttr_CelltypeVisibility()
            dict_roi_display[roi_id]["celltype"] = dict_celltype_visibility.get(new_cell_type, False)
            self.setSharedAttr_DictROIDisplay(dict_roi_display)

    def changeCheckboxOfTable(self, row: int) -> None:
        dict_roi_display = self.getSharedAttr_DictROIDisplay()
        roi_id = self.getCellIdFromRow(row)
        if roi_id is None or roi_id not in dict_roi_display:
            return
        dict_checkbox_visibility: Dict[str, bool] = self.getSharedAttr_CheckboxVisibility()
        checkbox_states_row: Dict[str, bool] = self.getCheckboxStatesOfRow(row)
        is_visible = True
        for checkbox_name, check_checkbox in dict_checkbox_visibility.items():
            if check_checkbox:
                if not checkbox_states_row.get(checkbox_name, False):
                    is_visible = False
                    break
        dict_roi_display[roi_id]["checkbox"] = is_visible
        self.setSharedAttr_DictROIDisplay(dict_roi_display)

    def updateSelectedROI(self, roi_id: str) -> None:
        if roi_id is not None:
            row = self.getRowFromCellId(roi_id)
            if row is not None:
                self.q_table.selectRow(row)
                self.setSelectedRow(row)
                self.setSharedAttr_ROISelected(roi_id)
                self.q_table.scrollToItem(self.q_table.item(row, 0), QAbstractItemView.PositionAtTop)
                self.q_table.setCurrentCell(row, 0)
            
    """
    Sub Function
    """
    def getCurrentCellTypeOfRow(self, row: int) -> str:
        button_group = self.groups_celltype.get(row)
        if button_group:
            checked_button = button_group.checkedButton()
            if checked_button:
                for col_name, col_info in self.table_columns.getColumns().items():
                    if col_info['type'] == 'celltype' and self.q_table.cellWidget(row, col_info['order']) == checked_button:
                        return col_name
        return None
    
    def getCheckboxStatesOfRow(self, row: int) -> Dict[str, bool]:
        table_columns_ = self.table_columns.getColumns()
        dict_checkbox_state = {}
        for column_name in table_columns_.keys():
            if table_columns_[column_name]["type"] == "checkbox":
                dict_checkbox_state[column_name] = self.getCheckboxStatesOfColumn(column_name)[row]
        return dict_checkbox_state

    def getRowChecked(self, row: int) -> bool:
        for col_name, col_info in self.table_columns.getColumns().items():
            if col_info['type'] == 'checkbox' and col_name == 'Check':
                check_box_item = self.q_table.item(row, col_info['order'])
                return check_box_item.checkState() == Qt.Checked if check_box_item else False
        return False
    
    def getRowFromCellId(self, cell_id: str) -> Optional[int]:
        col_id = self.table_columns.getColumns()['Cell_ID']['order']
        for row in range(self.len_row):
            item = self.q_table.item(row, col_id)
            if item and item.text() == cell_id:
                return row
        return None
    
    """
    Button-binding Function
    """
    def setSelectedROISameCelltype(
            self, 
            celltype: str,
            idx_min: Optional[int] = None,
            idx_max: Optional[int] = None
        ) -> None:
        checkbox_columns = self.getCheckboxColumns()
        skip_states = {}
        
        for column in checkbox_columns:
            result = showConfirmationDialog(
                self.q_table,
                'Confirmation',
                f"Skip {column} checked ROI ? (ROI {idx_min} to {idx_max})"
            )
            if result == QMessageBox.Yes:
                skip_states[column] = self.getCheckboxStatesOfColumn(column)
            elif result == QMessageBox.Cancel:
                return
            else:
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

    def getCheckboxStatesOfColumn(self, column_name: str) -> List[bool]:
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
        
    def filterROI(self, thresholds: Dict[str, Tuple[float, float]]) -> None:
        result = showConfirmationDialog(
            self.q_table,
            'Confirmation',
            f"Filter ROIs ?"
        )
        if result == QMessageBox.Yes:
            celltype_columns = [col for col, info in self.table_columns.getColumns().items() if info['type'] == 'celltype']
            target_celltype = max(celltype_columns, key=lambda col: self.table_columns.getColumns()[col]['order'])
            target_column = self.table_columns.getColumns()[target_celltype]['order']

            for row in range(self.q_table.rowCount()):
                roi_id = self.getCellIdFromRow(row)
                roi_stat = self.data_manager.getStat(self.app_key)[roi_id]
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
    def setROICellTypeFromArray(
        self,
        array_bool: np.ndarray[bool],
        celltype_pos: str = "Neuron",
        celltype_neg: str = "Not_Cell",
        app_key: AppKeys = "pri"
    ) -> None:
        from ..utils.roi_id_utils import arrayIndexToRoiId
        
        columns = self.table_columns.getColumns()
        pos_col_idx = columns.get(celltype_pos, {}).get('order')
        neg_col_idx = columns.get(celltype_neg, {}).get('order')

        n_rois_chan1 = self.data_manager.getNROIsChan1(app_key)

        self.data_manager.dict_roi_celltype[app_key] = {}
        for row, is_positive in enumerate(array_bool):
            roi_id = arrayIndexToRoiId(row, n_rois_chan1)
            self.data_manager.dict_roi_celltype[app_key][roi_id] = celltype_pos if is_positive else celltype_neg
            target_col = pos_col_idx if is_positive else neg_col_idx
            radio_button = self.q_table.cellWidget(row, target_col)
            if radio_button:
                radio_button.setChecked(True)
                self.changeRadiobuttonOfTable(row)
                
        updateROICountDisplay(self.widget_manager, self.config_manager, self.app_key)

    def updateMatchedROIPairs(self, matches: Dict[str, str]) -> None:
        col_id = self.table_columns.getColumns()['Cell_ID']['order']
        col_id_match = self.table_columns.getColumns()['Cell_ID_Match']['order']
        
        for row in range(self.q_table.rowCount()):
            try:
                cell_id = self.q_table.item(row, col_id).text()
                if cell_id in matches:
                    match_item = QTableWidgetItem(str(matches[cell_id]))
                    self.q_table.setItem(row, col_id_match, match_item)
                else:
                    self.q_table.setItem(row, col_id_match, QTableWidgetItem(""))
            except (ValueError, AttributeError):
                continue

    def getMatchedROIPairs(self, table_control_sec: TableControl) -> List[Tuple[str, str]]:
        matched_pairs = []

        col_id = self.table_columns.getColumns()['Cell_ID']['order']
        col_id_match = self.table_columns.getColumns()['Cell_ID_Match']['order']
        
        for row in range(self.len_row):
            try:
                cell_id = self.q_table.item(row, col_id).text()
                cell_id_match_item = self.q_table.item(row, col_id_match)
                
                if not cell_id_match_item or not cell_id_match_item.text().strip():
                    continue
                    
                cell_id_match = cell_id_match_item.text()
                matched_pairs.append((cell_id, cell_id_match))
            except (ValueError, AttributeError):
                continue
                
        return matched_pairs