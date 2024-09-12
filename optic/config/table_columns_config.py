from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers

# Table Columns Config
class TableColumnConfigWindow(QDialog):
    def __init__(self, parent, table_columns, gui_defaults):
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

        layout.addWidget(self.widget_manager.makeWidgetTable(key="table_columns"))
        self.widget_manager.dict_table["table_columns"].setColumnCount(3)
        self.widget_manager.dict_table["table_columns"].setHorizontalHeaderLabels(['Column Name', 'Type', 'Width'])
        self.populateConfigTable()

        layout.addWidget(self.widget_manager.makeWidgetButton(key="update", label="Update"))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="exit", label="Exit"))

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def populateConfigTable(self):
        columns = self.table_columns.getColumns()
        self.widget_manager.dict_table["table_columns"].setRowCount(len(columns))
        
        for i, (col_name, col_info) in enumerate(columns.items()):
            # Column Name
            self.widget_manager.makeWidgetLineEdit(key="col_name", text_set=col_name)
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 0, self.widget_manager.dict_lineedit["col_name"])
            
            # Type
            self.widget_manager.makeWidgetComboBox(key="type")
            self.widget_manager.dict_combobox["type"].addItems(['id', 'celltype', 'checkbox', 'string'])
            self.widget_manager.dict_combobox["type"].setCurrentText(col_info['type'])
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 1, self.widget_manager.dict_combobox["type"])
            
            # Width
            self.widget_manager.makeWidgetLineEdit(key="width", text_set=str(col_info['width']))
            self.widget_manager.dict_table["table_columns"].setCellWidget(i, 2, self.widget_manager.dict_lineedit["width"])

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["exit"].clicked.connect(self.close)