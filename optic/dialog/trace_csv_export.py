from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMessageBox
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.base_layouts import makeLayoutComboBoxLabel


# Choose which celltypes to extract and which trace (F / Fneu / spks / ...) to write out.
# On accept, read `list_celltype_selected` and `trace_key`.
class TraceCSVExportDialog(QDialog):
    def __init__(
            self,
            parent          : QMainWindow,
            gui_defaults    : GuiDefaults,
            list_celltype   : List[str],
            list_trace_key  : List[str],
            ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.list_celltype = list_celltype
        self.list_trace_key = list_trace_key
        self.list_celltype_selected: List[str] = []
        self.trace_key: str = list_trace_key[0] if list_trace_key else ""

        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Export Trace CSV")
        layout = QVBoxLayout()

        layout.addWidget(self.widget_manager.makeWidgetLabel(
            key="trace_csv_celltype", label="Celltype to extract",
            font_size=12, bold=True, italic=True, use_global_style=False
        ))
        # first celltype is checked by default (usually the positive one, e.g. "Neuron")
        for i, celltype in enumerate(self.list_celltype):
            layout.addWidget(self.widget_manager.makeWidgetCheckBox(
                key=f"trace_csv_celltype_{celltype}", label=celltype, checked=(i == 0)
            ))

        layout.addLayout(makeLayoutComboBoxLabel(
            self.widget_manager,
            key_label="trace_csv_trace_key",
            key_combobox="trace_csv_trace_key",
            label="Trace to export:",
            axis="vertical",
            items=self.list_trace_key,
        ))

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.widget_manager.makeWidgetButton(key="export", label="Export"))
        layout_button.addWidget(self.widget_manager.makeWidgetButton(key="cancel", label="Cancel"))
        layout.addLayout(layout_button)

        self.setLayout(layout)
        self.bindFuncAllWidget()

    def bindFuncAllWidget(self):
        self.widget_manager.dict_button["export"].clicked.connect(self.onExport)
        self.widget_manager.dict_button["cancel"].clicked.connect(self.reject)

    def onExport(self):
        self.list_celltype_selected = [
            celltype for celltype in self.list_celltype
            if self.widget_manager.dict_checkbox[f"trace_csv_celltype_{celltype}"].isChecked()
        ]
        if not self.list_celltype_selected:
            QMessageBox.warning(self, "Export Trace CSV", "Select at least one celltype.")
            return
        self.trace_key = self.widget_manager.dict_combobox["trace_csv_trace_key"].currentText()
        if not self.trace_key:
            QMessageBox.warning(self, "Export Trace CSV", "No trace available for this data type.")
            return
        self.accept()
