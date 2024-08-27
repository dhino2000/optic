# TableWidget Setup
from PyQt5.QtWidgets import QAbstractItemView

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
    return q_table