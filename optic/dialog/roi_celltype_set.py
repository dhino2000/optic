from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.table_layouts import makeLayoutAllROISetSameCelltype, makeLayoutAllROICheckboxToggle
from ..gui.base_layouts import makeLayoutComboBoxLabel

# Set ROIs celltype
class ROICellTypeSetDialog(QDialog):
    def __init__(
            self, 
            parent: QMainWindow, 
            app_key: AppKeys,
            config_manager: ConfigManager,
            table_control: TableControl,
            table_columns: TableColumns, 
            gui_defaults: GuiDefaults,
            ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.table_columns = table_columns
        self.config_manager = config_manager
        self.table_control = table_control
        self.app_key = app_key

        window_settings = gui_defaults.get("WINDOW_SETTINGS_ROI_CELLTYPE_SET", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Set ROIs Celltype')
        layout = QVBoxLayout()

        layout.addWidget(self.widget_manager.makeWidgetLabel(key="roi_celltype_set", label="Selected ROIs Celltype Set", font_size=12, bold=True, italic=True, use_global_style=False))
        
        layout_combobox = QHBoxLayout()
        layout_combobox.addLayout(makeLayoutComboBoxLabel(
            self.widget_manager,
            key_label="set_roi_idx_min",
            key_combobox="set_roi_idx_min",
            label="Set ROI index min:",
            axis="vertical",
            items=[str(i) for i in range(self.table_control.len_row())]
            ))

        layout.addLayout(layout_combobox)
        
        layout.addLayout(makeLayoutAllROISetSameCelltype(
            self.widget_manager, 
            key_button=self.app_key, 
            table_columns=self.config_manager.table_columns[self.app_key].getColumns()
        ))
        layout.addLayout(makeLayoutAllROICheckboxToggle(
            self.widget_manager, 
            key_button=self.app_key, 
            table_columns=self.config_manager.table_columns[self.app_key].getColumns()
        ))

        layout_update_exit = QHBoxLayout()
        layout_update_exit.addWidget(self.widget_manager.makeWidgetButton(key="update", label="Update"))
        layout_update_exit.addWidget(self.widget_manager.makeWidgetButton(key="exit", label="Exit"))

        layout.addLayout(layout_update_exit)

        self.setLayout(layout)

        self.bindFuncAllWidget()

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["exit"].clicked.connect(self.reject)

        # # Set AllROI same celltype
        # bindFuncButtonSetAllROISameCelltype(
        #     widget_manager=self.widget_manager,
        #     table_control=self.control_manager.table_controls[self.app_key_pri],
        #     view_control=self.control_manager.view_controls[self.app_key_pri],
        # )
        # # Toggle AllROI checkbox
        # bindFuncCheckboxToggleAllROI(
        #     widget_manager=self.widget_manager,
        #     table_control=self.control_manager.table_controls[self.app_key_pri],
        #     view_control=self.control_manager.view_controls[self.app_key_pri],
        # )