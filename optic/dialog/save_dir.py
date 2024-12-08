from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager
from ..gui.base_layouts import makeLayoutLineEditLabel

# Get save directory
class SaveDirectoryDialog(QDialog):
    def __init__(self, parent: QWidget, gui_defaults: GuiDefaults, initial_dir: str=""):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.initial_dir = initial_dir
        self.dir_dst = ""

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Save directory')
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutLineEditLabel(widget_manager=self.widget_manager, key_label="dir_dst", key_lineedit="dir_dst", label="Save directory:", text_set=self.initial_dir))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="ok", label="OK"))

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def getDirectory(self):
        self.dir_dst = self.widget_manager.dict_lineedit["dir_dst"].text()
        self.accept()
    
    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["ok"].clicked.connect(self.getDirectory)