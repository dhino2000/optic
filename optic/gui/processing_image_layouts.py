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