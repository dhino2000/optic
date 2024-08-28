# TableWidget Setup
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QRadioButton, QButtonGroup

def setupWidgetROITable(q_table, len_row, dict_tablecol):
    q_table.clearSelection() # テーブルの選択初期化

    q_table.setRowCount(len_row)
    # 列を順序に基づいてソート
    col_sorted = sorted(dict_tablecol.items(), key=lambda x: x[1]['order'])
    q_table.setColumnCount(len(col_sorted))

    # ヘッダーの設定
    q_table.setHorizontalHeaderLabels([col[0] for col in col_sorted])
    # テーブルの選択モードを単一行選択に設定
    q_table.setSelectionMode(QAbstractItemView.SingleSelection)

    # セルの横幅指定
    for col_name, col_info in col_sorted:
        q_table.setColumnWidth(col_info['order'], col_info['width'])

    radio_groups = {}
    # セルの設定
    for cellid in range(len_row):
        for col_name, col_info in col_sorted:
            cell_type = col_info["type"]
            
            if cell_type == "id":
                cell = QTableWidgetItem(str(cellid))
                cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "radio":
                cell = QRadioButton()
                if col_info["default"]:
                    cell.setChecked(True)
                group = col_info["group"]
                if not radio_groups.get(cellid):
                    radio_groups[cellid] = QButtonGroup(q_table)
                radio_groups[cellid].addButton(cell)
                q_table.setCellWidget(cellid, col_info['order'], cell)
            elif cell_type == "checkbox":
                cell = QTableWidgetItem()
                cell.setCheckState(Qt.Checked if col_info["default"] else Qt.Unchecked)
                q_table.setItem(cellid, col_info['order'], cell)
            elif cell_type == "string":
                cell = QTableWidgetItem()
                if not col_info["editable"]:
                    cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_info['order'], cell)

    return q_table

# dict_roicheckの内容をtableに反映
def applyDictROICheckToTable(q_table, dict_tablecol, dict_roicheck):
    row_count = q_table.rowCount()

    # ラジオボタンの設定
    for col_name, col_info in dict_tablecol.items():
        if col_info['type'] == 'radio':
            if col_name in dict_roicheck:
                selected_rows = dict_roicheck[col_name]
                for row in range(row_count):
                    radio_button = q_table.cellWidget(row, col_info['order'])
                    if radio_button:
                        radio_button.setChecked(any(row == sr[0] for sr in selected_rows))
            elif col_name in cell_type_keys.values():
                corresponding_key = [k for k, v in cell_type_keys.items() if v == col_name][0]
                if corresponding_key in dict_roicheck:
                    selected_rows = dict_roicheck[corresponding_key]
                    for row in range(row_count):
                        radio_button = q_table.cellWidget(row, col_info['order'])
                        if radio_button:
                            radio_button.setChecked(any(row == sr[0] for sr in selected_rows))

    # チェックボックスと文字列の設定
    for col_name, col_info in dict_tablecol.items():
        if col_info['type'] in ['checkbox', 'string']:
            if col_name in dict_roicheck:
                data = dict_roicheck[col_name]
                for row in range(min(row_count, len(data))):
                    item = q_table.item(row, col_info['order'])
                    if item:
                        if col_info['type'] == 'checkbox':
                            item.setCheckState(Qt.Checked if data[row][0] else Qt.Unchecked)
                        else:  # string
                            # 空のリストや空の文字列を空白として処理
                            value = str(data[row][0])
                            if value == '[]' or value == '':
                                value = ''
                            item.setText(value)
