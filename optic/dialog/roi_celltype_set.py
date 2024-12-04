from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.table_layouts import makeLayoutSelectedROISetSameCelltype, makeLayoutSelectedROICheckboxToggle
from ..gui.base_layouts import makeLayoutComboBoxLabel

# Set ROIs celltype
class ROICellTypeSetDialog(QDialog):
    def __init__(
            self, 
            parent: QMainWindow, 
            app_key: AppKeys,
            config_manager: ConfigManager,
            table_control: TableControl,
            gui_defaults: GuiDefaults,
            ):
        super().__init__(parent)
        self.parent = parent
        self.widget_manager = initManagers(WidgetManager())
        self.config_manager = config_manager
        self.table_control = table_control
        self.table_columns = table_control.table_columns
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

        layout.addWidget(self.widget_manager.makeWidgetLabel(key="roi_celltype_set", label="Set Selected ROIs Celltype", font_size=12, bold=True, italic=True, use_global_style=False))
        
        layout_combobox = QHBoxLayout()
        layout_combobox.addLayout(makeLayoutComboBoxLabel(
            self.widget_manager,
            key_label="set_roi_idx_min",
            key_combobox="set_roi_idx_min",
            label="Set ROI index min:",
            axis="vertical",
            items=[str(i) for i in range(self.table_control.len_row)]
            ))
        layout_combobox.addLayout(makeLayoutComboBoxLabel(
            self.widget_manager,
            key_label="set_roi_idx_max",
            key_combobox="set_roi_idx_max",
            label="Set ROI index max:",
            axis="vertical",
            idx_default=self.table_control.len_row-1,
            items=[str(i) for i in range(self.table_control.len_row)]
            ))

        layout.addLayout(layout_combobox)
        
        layout.addLayout(makeLayoutSelectedROISetSameCelltype(
            self.widget_manager, 
            key_button=self.app_key, 
            table_columns=self.config_manager.table_columns[self.app_key].getColumns()
        ))
        layout.addLayout(makeLayoutSelectedROICheckboxToggle(
            self.widget_manager, 
            key_button=self.app_key, 
            table_columns=self.config_manager.table_columns[self.app_key].getColumns()
        ))

        layout_update_exit = QHBoxLayout()
        layout_update_exit.addWidget(self.widget_manager.makeWidgetButton(key="exit", label="Exit"))

        layout.addLayout(layout_update_exit)

        self.setLayout(layout)
        
        self.bindFuncAllWidget()

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["exit"].clicked.connect(self.reject)

        # Set selected ROI same celltype
        list_celltype = [key for key, value in self.table_columns.getColumns().items() if value['type'] == 'celltype']
        for celltype in list_celltype:
            button = self.widget_manager.dict_button[f"{self.app_key}_roi_set_{celltype}"]
            button.clicked.connect(
                lambda checked, ct=celltype: self.table_control.setSelectedROISameCelltype(
                    ct,
                    int(self.widget_manager.dict_combobox["set_roi_idx_min"].currentText()),
                    int(self.widget_manager.dict_combobox["set_roi_idx_max"].currentText())
                )
            )

        # Toggle selected ROI checkbox
        list_checkbox = [key for key, value in self.table_columns.getColumns().items() if value['type'] == 'checkbox']
        for label, toggle in zip(["check", "uncheck"], [True, False]):
            for checkbox in list_checkbox:
                button = self.widget_manager.dict_button[f"{self.app_key}_roi_{label}_{checkbox}"]
                button.clicked.connect(
                    lambda checked, ck=checkbox, tg=toggle: self.table_control.toggleSelectedROICheckbox(
                        ck,
                        tg,
                        int(self.widget_manager.dict_combobox["set_roi_idx_min"].currentText()),
                        int(self.widget_manager.dict_combobox["set_roi_idx_max"].currentText())
                    )
                )