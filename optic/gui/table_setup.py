from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QRadioButton, QButtonGroup
from ..controls.event_filters import applyKeyPressEventIgnore
import numpy as np

# for Suite2pROICheck, Suite2pROITracking
def setupWidgetROITable(
        q_table: QTableWidget, 
        len_row: int, 
        table_columns: TableColumns, 
        key_event_ignore: bool=True
        ):
    # initialize table
    q_table.clearSelection()

    q_table.setRowCount(len_row)
    # sort columns by order
    col_sorted = sorted(table_columns.getColumns().items(), key=lambda x: x[1]['order'])
    q_table.setColumnCount(len(col_sorted))

    # set column names
    q_table.setHorizontalHeaderLabels([col[0] for col in col_sorted])
    # set selection mode
    q_table.setSelectionMode(QAbstractItemView.SingleSelection)

    # set column width
    for col_name, col_info in col_sorted:
        q_table.setColumnWidth(col_info['order'], col_info['width'])

    groups_celltype = {}

    for cellid in range(len_row):
        groups_celltype[cellid] = QButtonGroup(q_table)
        for col_name, col_info in col_sorted:
            cell_type = col_info["type"]
            
            if cell_type == "id":
                cell = QTableWidgetItem(str(cellid))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "id_match":
                cell = QTableWidgetItem()
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "celltype":
                cell = QRadioButton()
                if col_info.get("default", False):
                    cell.setChecked(True)
                if key_event_ignore:
                    cell = applyKeyPressEventIgnore(cell)
                groups_celltype[cellid].addButton(cell)
                q_table.setCellWidget(cellid, col_info['order'], cell)
            elif cell_type == "checkbox":
                cell = QTableWidgetItem()
                cell.setCheckState(Qt.Checked if col_info.get("default", False) else Qt.Unchecked)
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "string":
                cell = QTableWidgetItem()
                q_table.setItem(cellid, col_info['order'], cell)

    return q_table, groups_celltype

# for MicrogliaTracking, empty table
def setupWidgetDynamicTable(
        q_table: QTableWidget, 
        table_columns: TableColumns,
        len_row: int=None,  
        ):
    q_table.clearSelection()

    if len_row:
        q_table.setRowCount(len_row)
    col_sorted = sorted(table_columns.getColumns().items(), key=lambda x: x[1]['order'])
    q_table.setColumnCount(len(col_sorted))

    q_table.setHorizontalHeaderLabels([col[0] for col in col_sorted])
    q_table.setSelectionMode(QAbstractItemView.SingleSelection)

    for col_name, col_info in col_sorted:
        q_table.setColumnWidth(col_info['order'], col_info['width'])

    groups_celltype = {}

    for cellid in range(len_row):
        groups_celltype[cellid] = QButtonGroup(q_table)
        for col_name, col_info in col_sorted:
            cell_type = col_info["type"]
            
            if cell_type == "id":
                cell = QTableWidgetItem(str(cellid))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "id_match":
                cell = QTableWidgetItem()
                q_table.setItem(cellid, col_info['order'], cell)

    return q_table, groups_celltype

# dict_roicheckの内容をtableに反映
def applyDictROICheckToTable(
        q_table: QTableWidget, 
        table_columns: TableColumns, 
        dict_roicheck: Dict[str, Any]
        ):
    row_count = q_table.rowCount()

    for col_name, col_info in table_columns.getColumns().items():
        # radio button
        if col_info['type'] == 'celltype':
            if col_name in dict_roicheck:
                selected_rows = dict_roicheck[col_name]
                for row in range(row_count):
                    radio_button = q_table.cellWidget(row, col_info['order'])
                    if radio_button:
                        radio_button.setChecked(any(row == sr for sr in selected_rows))

        # checkbox or string
        elif col_info['type'] in ['checkbox', 'string']:
            if col_name in dict_roicheck:
                data = dict_roicheck[col_name]
                for row in range(min(row_count, len(data))):
                    item = q_table.item(row, col_info['order'])
                    if item:
                        if col_info['type'] == 'checkbox':
                            item.setCheckState(Qt.Checked if data[row] else Qt.Unchecked)
                        else:  # string
                            value = str(data[row])
                            if value == '[]' or value == '':
                                value = ''
                            item.setText(value)

# apply dict_roi_tracking to table
def applyDictROITrackingToTable(
        q_table: QTableWidget, 
        table_columns: TableColumns, 
        dict_roi_tracking: Dict[str, Any]
        ):
    applyDictROICheckToTable(q_table, table_columns, dict_roi_tracking)
    row_count = q_table.rowCount()

    # Cell_ID_Match
    for col_name, col_info in table_columns.getColumns().items():
        if col_info['type'] == 'id_match':
            if col_name in dict_roi_tracking:
                data = dict_roi_tracking[col_name]
                for row in range(min(row_count, len(data))):
                    item = q_table.item(row, col_info['order'])
                    if item:
                        value = data[row]
                        if not np.isnan(value):
                            item.setText(str(int(value)))

# apply dict_roi_matching to table
def applyDictROIMatchingToTable(
        q_table: QTableWidget, 
        table_columns: TableColumns,
        dict_roi_matching: Dict[int, Optional[int]],
        row_count: int,
        has_roi_id_match: bool = False
        ) -> None:
    if q_table.rowCount() < row_count:
        q_table.setRowCount(row_count)

    if has_roi_id_match:
        for col_name, col_info in table_columns.getColumns().items():
            if col_info['type'] == 'id':
                col_index = col_info['order']
                for row in range(row_count):
                    item = QTableWidgetItem(str(row))
                    q_table.setItem(row, col_index, item)
            if col_info['type'] == 'id_match':
                col_index = col_info['order']
                for row in range(row_count):
                    matched_id = dict_roi_matching.get(row)
                    item = QTableWidgetItem()
                    if matched_id is not None:
                        item.setText(str(matched_id))
                    q_table.setItem(row, col_index, item)
    else:
        for col_name, col_info in table_columns.getColumns().items():
            if col_info['type'] == 'id':
                col_index = col_info['order']
                for row in range(row_count):
                    item = QTableWidgetItem(str(row))
                    q_table.setItem(row, col_index, item)