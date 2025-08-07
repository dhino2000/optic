from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.io_layouts import makeLayoutLoadFileWidget, makeLayoutLoadFileExitHelp
from ..gui.bind_func import bindFuncLoadFileWidget, bindFuncExit
from ..utils.layout_utils import clearLayout

# load multi Fall.mat for Suite2pROITracking
class LoadMultiFallDialog(QDialog):
    """Dialog for loading multiple Fall.mat files for Suite2pROITracking.
    args:
        gui_defaults (GuiDefaults): GUI defaults configuration.
        parent (QWidget, optional): Parent widget. Defaults to None.
        plane_t (int, optional): Number of sessions. Defaults to 2.
    """
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
        self.max_plane_t = 10  # 最大セッション数の制限
        self.min_plane_t = 2   # 最小セッション数の制限

        window_settings = gui_defaults.get("WINDOW_SETTINGS_LOAD_MULTI_FALL", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        # データ保存用
        self.list_path_fall = []
        self.accepted_data = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Suite2pROITracking load multi Fall.mat')
        layout = QVBoxLayout()
        # Label
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="load_fall", label="File Load", font_size=12, bold=True, italic=True, use_global_style=False))
        # LineEdit
        layout.addWidget(self.setupFileLoadArea())
        # add, remove lineedit
        layout.addLayout(self.makeLayoutComponentAddRemoveButtons())
        # load, exit, help, load ROI tracking buttons
        layout.addLayout(self.makeLayoutComponentLoadExitHelpButtons())

        self.setLayout(layout)

        self.bindFuncAllWidget()

    """
    makeLayout Functions
    """
    # Make layout for Fall.mat lineedit
    def setupFileLoadArea(self):
        """ファイル読み込みエリアの初期設定"""
        # ファイル読み込み用のレイアウトコンテナ
        self.file_load_container = QWidget()
        self.file_load_layout = QVBoxLayout(self.file_load_container)
        
        # 初期のLineEditを作成
        self.updateFileLoadUI()
        return self.file_load_container

    # Make layout for add/remove buttons
    def makeLayoutComponentAddRemoveButtons(self) -> QHBoxLayout:
        layout_button_lineedit = QHBoxLayout()
        layout_button_lineedit.addWidget(self.widget_manager.makeWidgetButton(key="add_lineedit", label="Add LineEdit"))
        layout_button_lineedit.addWidget(self.widget_manager.makeWidgetButton(key="remove_lineedit", label="Remove LineEdit"))
        return layout_button_lineedit
    
    # Make layout for load, exit, help, load ROI tracking buttons
    def makeLayoutComponentLoadExitHelpButtons(self) -> QHBoxLayout:
        layout_button_load_exit_help = makeLayoutLoadFileExitHelp(self.widget_manager)
        layout_button_load_exit_help.addWidget(self.widget_manager.makeWidgetButton(key="load_roi_tracking", label="Load ROI Tracking"))
        return layout_button_load_exit_help
    
    """
    button-binding Functions
    """
    def addSession(self):
        """セッションの追加"""
        if self.plane_t >= self.max_plane_t:
            QMessageBox.warning(self, "Warning", f"Maximum number of sessions is {self.max_plane_t}")
            return
            
        self.plane_t += 1
        self.updateFileLoadUI()

    def removeSession(self):
        """セッションの削除"""
        if self.plane_t <= self.min_plane_t:
            QMessageBox.warning(self, "Warning", f"Minimum number of sessions is {self.min_plane_t}")
            return
            
        # 削除されるセッションのウィジェットをクリーンアップ
        t_to_remove = self.plane_t - 1
        keys_to_remove = [f"path_fall_t{t_to_remove}"]
        
        for key in keys_to_remove:
            if key in self.widget_manager.dict_lineedit:
                del self.widget_manager.dict_lineedit[key]
            if key in self.widget_manager.dict_button:
                del self.widget_manager.dict_button[key]
            if key in self.widget_manager.dict_label:
                del self.widget_manager.dict_label[key]
        
        self.plane_t -= 1
        self.updateFileLoadUI()
    
    def updateFileLoadUI(self):
        """ファイル読み込みUIの更新"""
        # 既存のレイアウトをクリア
        self.clearFileLoadLayout()
        
        # 新しいLineEditを作成
        for t in range(self.plane_t):
            label = f"Fall mat file path (session {t})"
            key = f"path_fall_t{t}"
            file_layout = makeLayoutLoadFileWidget(
                self.widget_manager, 
                label=label, 
                key_label=key, 
                key_lineedit=key, 
                key_button=key
            )
            self.file_load_layout.addLayout(file_layout)
            
            # ファイル選択ボタンにバインド
            bindFuncLoadFileWidget(
                q_widget=self, 
                q_button=self.widget_manager.dict_button[key], 
                q_lineedit=self.widget_manager.dict_lineedit[key], 
                filetype="mat"
            )

    def clearFileLoadLayout(self):
        """ファイル読み込みレイアウトのクリア"""
        while self.file_load_layout.count():
            child = self.file_load_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                clearLayout(child.layout())
    
    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["add_lineedit"].clicked.connect(self.addSession)
        self.widget_manager.dict_button["remove_lineedit"].clicked.connect(self.removeSession)
        bindFuncExit(
            q_window=self, 
            q_button=self.widget_manager.dict_button["exit"], 
        )