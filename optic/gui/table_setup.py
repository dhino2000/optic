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