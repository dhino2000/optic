from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import Qt
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager

# User select 
class UserSelectDialog(QDialog):
    def __init__(self, parent: QWidget, gui_defaults: GuiDefaults, json_config: JsonConfig):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.user = ""
        self.list_user = json_config.get("user_settings")["user"]

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
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="user", label="User:"))
        layout.addWidget(self.widget_manager.makeWidgetComboBox(key="user", items=self.list_user))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="ok", label="OK"))

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def getUser(self):
        self.user = self.widget_manager.dict_combobox["user"].currentText()
        self.accept()
    
    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["ok"].clicked.connect(self.getUser)