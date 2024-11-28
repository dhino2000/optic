from __future__ import annotations
from ..type_definitions import *

def deleteSelectedRows(q_table: QTableWidget) -> None:
    selected_rows = sorted(set(index.row() for index in q_table.selectedIndexes()), reverse=True)
    for row in selected_rows:
        q_table.removeRow(row)

def addRow(q_table: QTableWidget) -> int:
    selected_rows = sorted(set(index.row() for index in q_table.selectedIndexes()))
    if selected_rows:
        insert_position = selected_rows[-1] + 1
    else:
        insert_position = q_table.rowCount()
    
    q_table.insertRow(insert_position)
    return insert_position

# Clear all cells in the column
def clearColumnCells(
    q_table: 'QTableWidget',
    idx_col: int
) -> None:
    for row in range(q_table.rowCount()):
        cell_widget = q_table.cellWidget(row, idx_col)
        if cell_widget:
            q_table.removeCellWidget(row, idx_col)
            q_table.setItem(row, idx_col, QTableWidgetItem())
        else:
            item = q_table.item(row, idx_col)
            if item:
                item.setText("")