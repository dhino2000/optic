from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..config.constants import TableColumnConfigDialog_Config
from ..utils.table_utils import deleteSelectedRows, addRow

# Table Columns Config
class TableColumnConfigDialog(QDialog):
    def __init__(
            self, 
            parent: QMainWindow, 
            table_columns: TableColumns, 
            gui_defaults: GuiDefaults,
            ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
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

    def setupConfigTable(self):
        columns = self.table_columns.getColumns()
        self.widget_manager.dict_table["table_columns"].setRowCount(len(columns))
        
        for i, (col_name, col_info) in enumerate(columns.items()):
            # Column Name
            self.widget_manager.makeWidgetLineEdit(key=f"col_name_{i}", text_set=col_name)
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 0, self.widget_manager.dict_lineedit[f"col_name_{i}"])
            
            # Type
            self.widget_manager.makeWidgetComboBox(key=f"type_{i}")
            self.widget_manager.dict_combobox[f"type_{i}"].addItems(TableColumnConfigDialog_Config.COMBO_ITEMS)
            self.widget_manager.dict_combobox[f"type_{i}"].setCurrentText(col_info[f'type'])
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 1, self.widget_manager.dict_combobox[f"type_{i}"])
            
            # Width
            self.widget_manager.makeWidgetLineEdit(key=f"width_{i}", text_set=str(col_info['width']))
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 2, self.widget_manager.dict_lineedit[f"width_{i}"])

    def deleteSelectedTableColumns(self):
        deleteSelectedRows(self.widget_manager.dict_table["table_columns"])

    def addNewColumn(self):
        row = addRow(self.widget_manager.dict_table["table_columns"])
        
        # 新しい行にウィジェットを追加
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
            col_type = table.cellWidget(row, 1).currentText()
            col_width = int(table.cellWidget(row, 2).text())

            column_info = {
                "order": row,
                "type": col_type,
                "width": col_width
            }

            if col_type == "celltype":
                if not celltype_found:
                    column_info["default"] = True
                    celltype_found = True
                else:
                    column_info["default"] = False
            elif col_type == "checkbox":
                column_info["default"] = False

            table_columns[col_name] = column_info
        return table_columns
        
    def updateTableColumns(self):
        table_columns = self.convertTableToTableColumns()
        self.table_columns.setColumns(table_columns)
        self.accept()

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["update"].clicked.connect(self.updateTableColumns)
        self.widget_manager.dict_button["exit"].clicked.connect(self.reject)
        self.widget_manager.dict_button["del_col"].clicked.connect(self.deleteSelectedTableColumns)
        self.widget_manager.dict_button["add_col"].clicked.connect(self.addNewColumn)