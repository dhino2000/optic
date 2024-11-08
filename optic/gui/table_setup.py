from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QRadioButton, QButtonGroup
from ..controls.event_filters import applyKeyPressEventIgnore

def setupWidgetROITable(q_table: QTableWidget, len_row: int, table_columns: TableColumns, key_event_ignore: bool=True):
    q_table.clearSelection() # テーブルの選択初期化

    q_table.setRowCount(len_row)
    # 列を順序に基づいてソート
    col_sorted = sorted(table_columns.items(), key=lambda x: x[1]['order'])
    q_table.setColumnCount(len(col_sorted))

    # ヘッダーの設定
    q_table.setHorizontalHeaderLabels([col[0] for col in col_sorted])
    # テーブルの選択モードを単一行選択に設定
    q_table.setSelectionMode(QAbstractItemView.SingleSelection)

    # セルの横幅指定
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

# dict_roicheckの内容をtableに反映
def applyDictROICheckToTable(q_table: QTableWidget, table_columns: TableColumns, dict_roicheck: Dict[str, List[Tuple[Any]]]):
    row_count = q_table.rowCount()

    for col_name, col_info in table_columns.items():
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