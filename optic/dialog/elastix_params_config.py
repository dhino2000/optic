from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..config.constants import TableColumnConfigDialog_Config
from ..utils.table_utils import deleteSelectedRows, addRow

# Elastix Config
class ElastixParamsConfigDialog(QDialog):
    def __init__(self, parent, elastix_params, gui_defaults):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.elastix_params = elastix_params

        window_settings = gui_defaults.get("WINDOW_SETTINGS_ELASTIX_CONFIG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Elastix Configuration')
        layout = QVBoxLayout()

        self.setLayout(layout)

        # self.bindFuncAllWidget()

    def bindFuncAllWidget(self):
        pass