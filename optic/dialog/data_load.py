from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import Qt
from ..manager.init_managers import initManagers
from ..manager.widget_manager import WidgetManager
from ..gui.io_layouts import makeLayoutLoadFileWidget, makeLayoutLoadFileExitHelp
from ..config.constants import Extension
from ..gui.bind_func import bindFuncLoadFileWidget

# Data load
# This dialog is used to load data, such as Fall.mat, tif files, ROICuration.mat etc.
class DataLoadDialog(QDialog):
    def __init__(
            self, 
            parent          : QWidget, 
            gui_defaults    : GuiDefaults, 
            json_config     : JsonConfig,
            title           : str = "Data Load",
            list_label      : List[str] = [""],             # Labels for the input fields
            list_key        : List[str] = [""],             # Keys for the input fields
            list_optional   : List[bool] = [False],         # the lineedit is optional or not
            list_extension  : List[str] = [Extension.MAT]   # Extensions for the input fields
        ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.title = title
        self.list_user = json_config.get("user_settings")["user"]
        self.list_label = list_label
        self.list_key = list_key
        self.list_optional = list_optional
        self.list_extension = list_extension

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG_DATA_LOAD", {})
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
        for label, key in zip(self.list_label, self.list_key):
            layout.addLayout(makeLayoutLoadFileWidget(
                self.widget_manager, 
                label=label, 
                key_label=key, 
                key_lineedit=key, 
                key_button=key
            ))
        # Button
        layout.addLayout(makeLayoutLoadFileExitHelp(self.widget_manager))

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def loadData(self) -> None:
        dict_path_file = self.getFilePaths()
        # check if the file load is successful
        print(dict_path_file)
        success = self.parent().loadData(dict_path_file)
        print(success)
        
        if success:
            self.accept()  # Close the dialog

    def getFilePaths(self) -> Dict[str, str]:
        dict_path_file = {}
        for key in self.list_key:
            if key in self.widget_manager.dict_lineedit:
                dict_path_file[key] = self.widget_manager.dict_lineedit[key].text()
        return dict_path_file

    def bindFuncAllWidget(self):
        # set input file path
        for key, extension in zip(self.list_key, self.list_extension):
            bindFuncLoadFileWidget(
                q_widget=self, 
                q_button=self.widget_manager.dict_button[key], 
                q_lineedit=self.widget_manager.dict_lineedit[key], 
                filetype=extension
            )
        # try load data
        self.widget_manager.dict_button["load_file"].clicked.connect(self.loadData)
        # exit
        self.widget_manager.dict_button["exit"].clicked.connect(self.reject)