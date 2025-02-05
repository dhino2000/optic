from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMainWindow
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.io_layouts import makeLayoutLoadFileWidget, makeLayoutLoadFileExitHelp

# load multi Fall.mat for Suite2pROITracking
class LoadMultiFallDialog(QDialog):
    def __init__(
            self, 
            gui_defaults: GuiDefaults, 
            parent: QWidget = None,
            plane_t: int = 2
            ):
        if parent is not None:
            super().__init__(parent)
        else:
            QMainWindow.__init__(self)
        self.widget_manager = initManagers(WidgetManager())
        self.plane_t = plane_t

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Suite2pROITracking load multi Fall.mat')
        layout = QVBoxLayout()
        # Label
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="load_fall", label="File Load", font_size=12, bold=True, italic=True, use_global_style=False))
        # LineEdit
        for t in range(self.plane_t):
            label = f"Fall mat file path (session {t})"
            key = f"path_fall_t{t}"
            layout.addLayout(makeLayoutLoadFileWidget(self.widget_manager, label=label, key_label=key, key_lineedit=key, key_button=key))
        # add, remove lineedit
        layout_button_lineedit = QHBoxLayout()
        layout_button_lineedit.addWidget(self.widget_manager.makeWidgetButton(key="add_lineedit", label="Add LineEdit"))
        layout_button_lineedit.addWidget(self.widget_manager.makeWidgetButton(key="remove_lineedit", label="Remove LineEdit"))
        layout.addLayout(layout_button_lineedit)
        
        # load, exit, help
        layout_button_load_exit_help = makeLayoutLoadFileExitHelp(self.widget_manager)
        layout_button_load_exit_help.addWidget(self.widget_manager.makeWidgetButton(key="load_roi_tracking", label="Load ROI Tracking"))
        layout.addLayout(layout_button_load_exit_help)

        self.setLayout(layout)

        # self.bindFuncAllWidget()

    def getDate(self):
        self.date =  self.widget_manager.dict_combobox["date"].currentText()
        self.accept()
    
    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["ok"].clicked.connect(self.getDate)