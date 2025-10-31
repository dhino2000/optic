from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ..config.constants import TableColumnConfigDialog_Config
from ..utils.table_utils import deleteSelectedRows, addRow
import copy

# Table Columns Config
class TableColumnConfigDialog(QDialog):
    def __init__(
            self, 
            parent: QMainWindow, 
            table_columns: TableColumns, 
            gui_defaults: GuiDefaults,
            ):
        super().__init__(parent)

        from ..manager.widget_manager import WidgetManager
        from ..manager.init_managers import initManagers
        self.widget_manager = initManagers(WidgetManager())
        self.table_columns_tmp = copy.copy(table_columns) # copy to prevent changing original table_columns
        self.table_columns = table_columns

        window_settings = gui_defaults.get("WINDOW_SETTINGS_TABLE_COLUMNS_CONFIG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Table Column Configuration')
        layout = QVBoxLayout()

        layout.addWidget(self.widget_manager.makeWidgetLabel(key="table_columns_config", label="Table Columns Config", font_size=12, bold=True, italic=True, use_global_style=False))
        layout.addWidget(self.widget_manager.makeWidgetTable(key="table_columns"))
        self.widget_manager.dict_table["table_columns"].setColumnCount(3)
        self.widget_manager.dict_table["table_columns"].setHorizontalHeaderLabels(TableColumnConfigDialog_Config.COLUMNS)
        self.setupConfigTable()

        layout_column = QHBoxLayout()
        layout_column.addWidget(self.widget_manager.makeWidgetButton(key="add_col", label="Add column"))
        layout_column.addWidget(self.widget_manager.makeWidgetButton(key="del_col", label="Delete column"))
        layout_update_exit = QHBoxLayout()
        layout_update_exit.addWidget(self.widget_manager.makeWidgetButton(key="update", label="Update"))
        layout_update_exit.addWidget(self.widget_manager.makeWidgetButton(key="exit", label="Exit"))

        layout.addLayout(layout_column)
        layout.addLayout(layout_update_exit)

        self.setLayout(layout)

        self.bindFuncAllWidget()

    # get table_columns info from the selected row
    def getTableColumnsInfo(self, row: int) -> Tuple[str, Dict[str, Any]]:
        col_name = self.widget_manager.dict_table["table_columns"].cellWidget(row, 0).text()
        col_info = self.table_columns.getColumns()[col_name]
        return col_name, col_info

    def setupConfigTable(self):
        columns = self.table_columns.getColumns()
        self.widget_manager.dict_table["table_columns"].setRowCount(len(columns))
        
        # i: row
        for i, (col_name, col_info) in enumerate(columns.items()):
            # Column Name
            self.widget_manager.makeWidgetLineEdit(key=f"col_name_{i}", text_set=col_name)
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 0, self.widget_manager.dict_lineedit[f"col_name_{i}"])
            if col_info.get("name_fixed", False): # uneditable
                self.widget_manager.dict_lineedit[f"col_name_{i}"].setReadOnly(True)

            # Type
            if col_info.get("name_fixed", False): # uneditable
                self.widget_manager.makeWidgetLineEdit(key=f"type_{i}", text_set=col_info[f'type'])
                self.widget_manager.dict_table["table_columns"].setCellWidget(i, 1, self.widget_manager.dict_lineedit[f"type_{i}"])
                self.widget_manager.dict_lineedit[f"type_{i}"].setReadOnly(True)
            else:
                self.widget_manager.makeWidgetComboBox(key=f"type_{i}")
                self.widget_manager.dict_combobox[f"type_{i}"].addItems(TableColumnConfigDialog_Config.COMBO_ITEMS)
                self.widget_manager.dict_combobox[f"type_{i}"].setCurrentText(col_info[f'type'])
                self.widget_manager.dict_table["table_columns"].setCellWidget(i, 1, self.widget_manager.dict_combobox[f"type_{i}"])
            
            # Width
            self.widget_manager.makeWidgetLineEdit(key=f"width_{i}", text_set=str(col_info['width']))
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 2, self.widget_manager.dict_lineedit[f"width_{i}"])

    def deleteSelectedTableColumns(self):
        selected_row = sorted(set(index.row() for index in self.widget_manager.dict_table["table_columns"].selectedIndexes()), reverse=True)[0]
        selected_col_name, selected_col_info = self.getTableColumnsInfo(selected_row)
        if not selected_col_info.get("removable", False):
            QMessageBox.warning(self, "Warning", f"{selected_col_name} is not removable !")
        else:
            deleteSelectedRows(self.widget_manager.dict_table["table_columns"])
            self.updateTableColumnsTmp()

    def addNewTableColumn(self):
        row = addRow(self.widget_manager.dict_table["table_columns"])
        
        # add new widgets
        self.widget_manager.makeWidgetLineEdit(key=f"col_name_{row}", text_set=TableColumnConfigDialog_Config.DEFAULT_PARAMS[0])
        self.widget_manager.dict_table["table_columns"].setCellWidget(row, 0, self.widget_manager.dict_lineedit[f"col_name_{row}"])
        
        self.widget_manager.makeWidgetComboBox(key=f"type_{row}")
        self.widget_manager.dict_combobox[f"type_{row}"].addItems(TableColumnConfigDialog_Config.COMBO_ITEMS)
        self.widget_manager.dict_combobox[f"type_{row}"].setCurrentText(TableColumnConfigDialog_Config.DEFAULT_PARAMS[1])
        self.widget_manager.dict_table["table_columns"].setCellWidget(row, 1, self.widget_manager.dict_combobox[f"type_{row}"])

        self.widget_manager.makeWidgetLineEdit(key=f"width_{row}", text_set=TableColumnConfigDialog_Config.DEFAULT_PARAMS[2])
        self.widget_manager.dict_table["table_columns"].setCellWidget(row, 2, self.widget_manager.dict_lineedit[f"width_{row}"])

    def convertTableToTableColumns(self):
        table_columns = {}
        table = self.widget_manager.dict_table["table_columns"]
        celltype_found = False  # celltypeの最初の要素を追跡

        for row in range(table.rowCount()):
            col_name = table.cellWidget(row, 0).text()
            try:
                col_type = table.cellWidget(row, 1).currentText() # combo box
            except:
                col_type = table.cellWidget(row, 1).text() # line edit
            col_width = int(table.cellWidget(row, 2).text())

            # original col_info
            col_info = self.table_columns_tmp.getColumns().get(col_name, {})
            # col_info for update
            col_info_tmp = {
                "order": row,
                "type": col_type,
                "width": col_width,
            }

            if col_type == "celltype":
                if not celltype_found:
                    col_info_tmp["default"] = True
                    celltype_found = True
                else:
                    col_info_tmp["default"] = False
            elif col_type == "checkbox":
                col_info_tmp["default"] = False

            if col_info.get("name_fixed", False):
                col_info_tmp["name_fixed"] = col_info["name_fixed"]
            if col_info.get("removable", False):
                col_info_tmp["removable"] = col_info["removable"]
            if col_info.get("editable", False):
                col_info_tmp["editable"] = col_info["editable"]
            if col_info.get("default", False):
                col_info_tmp["default"] = col_info["default"]

            table_columns[col_name] = col_info_tmp
        return table_columns
    
    # update table_columns_tmp
    def updateTableColumnsTmp(self):
        table_columns_tmp = self.convertTableToTableColumns()
        self.table_columns_tmp.setColumns(table_columns_tmp)
    
    # update original table_columns
    def updateTableColumnsAndAccept(self):
        table_columns = self.convertTableToTableColumns()
        self.table_columns.setColumns(table_columns)
        self.accept()

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["update"].clicked.connect(self.updateTableColumnsAndAccept)
        self.widget_manager.dict_button["exit"].clicked.connect(self.reject)
        self.widget_manager.dict_button["del_col"].clicked.connect(self.deleteSelectedTableColumns)
        self.widget_manager.dict_button["add_col"].clicked.connect(self.addNewTableColumn)