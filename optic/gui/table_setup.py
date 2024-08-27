# TableWidget Setup
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QRadioButton, QButtonGroup

def setupWidgetROITable(q_table, len_row, dict_tablecol, width_col=80):
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
    for i in range(q_table.columnCount()):
        q_table.setColumnWidth(i, width_col)

    # セルの設定
    for cellid in range(len_row):
        for col_name, col_info in col_sorted:
            col_index = col_info['order']
            # Cell ID
            if col_info["type"] == "id":
                cellItem = QTableWidgetItem(f"{cellid}")
                cellItem.setFlags(cellItem.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_index, cellItem)
            # radiobutton
            elif col_info["type"] == "radio":
                radioButton = QRadioButton()
                if col_info.get("default", False):
                    radioButton.setChecked(True)
                q_table.setCellWidget(cellid, col_index, radioButton)
            # checkbox
            elif col_info["type"] == "checkbox":
                checkBox = QTableWidgetItem()
                checkBox.setCheckState(Qt.Unchecked)
                q_table.setItem(cellid, col_index, checkBox)
            # String
            elif col_info["type"] == "string":
                stringItem = QTableWidgetItem()
                # 編集可能か
                if not col_info.get("editable", True):
                    stringItem.setFlags(stringItem.flags() & ~Qt.ItemIsEditable)
                q_table.setItem(cellid, col_index, stringItem)

    # ラジオボタンのグループ化
    groups = {}
    for col_name, col_info in dict_tablecol.items():
        if col_info["type"] == "radio":
            group_name = col_info.get("group", "default")
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(col_info['order'])

    for row in range(q_table.rowCount()):
        for group_name, columns in groups.items():
            buttonGroup = QButtonGroup(q_table)
            for col in columns:
                radioButton = q_table.cellWidget(row, col)
                if radioButton:
                    buttonGroup.addButton(radioButton)

    return q_table