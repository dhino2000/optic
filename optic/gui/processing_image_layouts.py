from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from ..gui.base_layouts import makeLayoutComboBoxLabel

# Fall Image Registration config
def makeLayoutFallRegistration(
        widget_manager              : WidgetManager, 
        data_manager                : DataManager,
        app_key                     : str,
        key_label_elastix_method    : str, 
        key_label_ref_c             : str,
        key_label_vis_c             : str,
        key_combobox_elastix_method : str, 
        key_combobox_ref_c          : str,
        key_combobox_vis_c          : str,
        key_button_config           : str,
        key_button_run              : str,
        key_checkbox_show_reg       : str,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_elastix_method, label="Image Registration", bold=True, italic=True, use_global_style=False))
    layout_elastix = QHBoxLayout()
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_elastix_method, 
        key_combobox_elastix_method, 
        "Elastix method:", 
        axis="horizontal", 
        items=["rigid", "affine", "bspline"]
        ))
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_c, 
        key_combobox_ref_c, 
        "Reference channel:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getNChannels(app_key))]
        ))
    layout_run = QHBoxLayout()
    layout_run.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Elastix"))
    layout_checkbox = QHBoxLayout()
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg, label="Show Registered Image"))
    layout_checkbox.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_vis_c, 
        key_combobox_vis_c, 
        "Registered image channel:", 
        axis="horizontal",
        items=[str(i) for i in range(3)],
        ))

    layout.addLayout(layout_elastix)
    layout.addLayout(layout_run)
    layout.addLayout(layout_checkbox)
    return layout

# Stack Image Registration config
def makeLayoutStackRegistration(
        widget_manager              : WidgetManager, 
        data_manager                : DataManager,
        app_key                     : str,
        key_label_elastix_method    : str, 
        key_label_ref_c             : str,
        key_label_ref_t             : str,
        key_label_ref_z             : str,
        key_combobox_elastix_method : str, 
        key_combobox_ref_c          : str,
        key_combobox_ref_t          : str,
        key_combobox_ref_z          : str,
        key_button_config           : str,
        key_button_run_t            : str,
        key_button_run_z            : str,
        key_button_export           : str,
        key_checkbox_show_reg       : str,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_elastix_method, label="Image Registration", bold=True, italic=True, use_global_style=False))
    layout_elastix = QHBoxLayout()
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_elastix_method, 
        key_combobox_elastix_method, 
        "Elastix method:", 
        axis="horizontal", 
        items=["rigid", "affine", "bspline"]
        ))
    layout_elastix.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout_ref_plane = QHBoxLayout()
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_c, 
        key_combobox_ref_c, 
        "Reference channel:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfC(app_key))]
        ))
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_t, 
        key_combobox_ref_t, 
        "Reference T plane:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfT(app_key))]
        ))
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_z, 
        key_combobox_ref_z, 
        "Reference Z plane:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfZ(app_key))]
        ))
    layout_run = QHBoxLayout()
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run_t, label="Run Elastix (t-axis)"))
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run_z, label="Run Elastix (z-axis)"))
    layout_checkbox = QHBoxLayout()
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg, label="Show Registered Image"))

    layout.addLayout(layout_elastix)
    layout.addLayout(layout_ref_plane)
    layout.addLayout(layout_run)
    layout.addLayout(layout_checkbox)
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_export, label="Export Image"))
    return layout

# Elastix Config
def makeLayoutElastixConfig(widget_manager: WidgetManager, key_button: str) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Elastix Config"))
    return layout

# Stack Image Normalization config
def makeLayoutStackNormalization(
        widget_manager      : WidgetManager,
        key_label           : str,
        key_label_area      : str,
        key_lineedit_area   : str,
        key_button_area     : str,
        key_button_add      : str,
        key_button_remove   : str,
        key_button_clear    : str,
        key_button_run      : str,
        key_listwidget      : str,
    ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Image Normalization", bold=True, italic=True, use_global_style=False))
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_area, label="Area for Normalization (x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max)"))
    layout.addWidget(widget_manager.makeWidgetLineEdit(key=key_lineedit_area, text_set="0, 511, 0, 511, 0, 0, 0, 0"))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_area, label="Set reference area"))
    layout_add_remove = QHBoxLayout()
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_add, label="Add current area"))
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_remove, label="Remove selected area"))
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_clear, label="Clear all areas"))
    layout.addLayout(layout_add_remove)
    layout.addWidget(widget_manager.makeWidgetListWidget(key=key_listwidget))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Image Normalization"))
    return layout