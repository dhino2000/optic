from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

# Image Registration config
def makeLayoutImageRegistration(
        widget_manager      : WidgetManager, 
        key_label           : str, 
        key_combobox        : str, 
        key_button_config   : str,
        key_button_run      : str,
        items_combobox      : List[str]=[],
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Image Registration"))
    layout.addWidget(widget_manager.makeWidgetComboBox(key=key_combobox, items=items_combobox))
    layout.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Image Registration"))
    return layout

# Elastix Config
def makeLayoutElastixConfig(widget_manager: WidgetManager, key_button: str) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Elastix Config"))
    return layout

# Image Normalization config
def makeLayoutImageNormalization(
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
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Image Normalization"))
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