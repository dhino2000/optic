from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager

# User select 
class UserSelectDialog(QDialog):
    def __init__(self, parent, gui_defaults):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('User Selection')
        layout = QVBoxLayout()
        list_user = ["Fukatsu", "Takahashi", "Tanisumi"]
        layout.addWidget(self.widget_manager.makeWidgetComboBox(key="user", items=list_user))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="ok", label="OK"))

        self.setLayout(layout)

        # self.bindFuncAllWidget()

    def OK(self):
        return