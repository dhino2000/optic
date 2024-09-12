from PyQt5.QtWidgets import QTableWidget

def deleteSelectedRows(q_table):
    selected_rows = sorted(set(index.row() for index in q_table.selectedIndexes()), reverse=True)
    for row in selected_rows:
        q_table.removeRow(row)

def addRow(q_table):
    selected_rows = sorted(set(index.row() for index in q_table.selectedIndexes()))
    if selected_rows:
        insert_position = selected_rows[-1] + 1
    else:
        insert_position = q_table.rowCount()
    
    q_table.insertRow(insert_position)
    return insert_position