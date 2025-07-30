from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QWidget
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager
from ..gui.base_layouts import makeLayoutLineEditLabel

# Fs input
# This dialog is used to set the frequency sampling rate.
class FsInputDialog(QDialog):
    def __init__(
            self, 
            parent          : QWidget, 
            gui_defaults    : GuiDefaults, 
            json_config     : JsonConfig,
            title           : str = "Sampling rate input",
        ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.title = title
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
        self.setWindowTitle(self.title)
        layout = QVBoxLayout()

        # LineEdit
        layout.addLayout(makeLayoutLineEditLabel(
            self.widget_manager,
            key_label="fs",
            key_lineedit="fs",
            label="Sampling rate (Hz)",
        ))
        # Button
        layout.addWidget(self.widget_manager.makeWidgetButton("ok", "OK"))

        self.setLayout(layout)
        self.bindFuncAllWidget()

    def inputFs(self) -> None:
        try:
            fs = int(self.widget_manager.dict_lineedit["fs"].text())
            self.fs = fs
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid integer for the sampling rate.")
            return None

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["ok"].clicked.connect(self.inputFs)