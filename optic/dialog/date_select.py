from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import Qt
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager

# Date select 
class DateSelectDialog(QDialog):
    def __init__(self, parent: QWidget, gui_defaults: GuiDefaults, list_date: List[str]):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.list_date = list_date
        self.date = ""

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Date Selection')
        layout = QVBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="date", label="Date"))
        layout.addWidget(self.widget_manager.makeWidgetComboBox(key="date", items=self.list_date, idx_default=len(self.list_date)-1))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="ok", label="OK"))

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def getDate(self):
        self.date =  self.widget_manager.dict_combobox["date"].currentText()
        self.accept()
    
    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["ok"].clicked.connect(self.getDate)