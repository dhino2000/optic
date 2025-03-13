from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutLineEditLabel

# 読み込むファイルを選択するためのウィジェット
def makeLayoutLoadFileWidget(widget_manager: WidgetManager, label: str="", key_label: str="", key_lineedit: str="", key_button: str="") -> QHBoxLayout:
    layout = QHBoxLayout() # entry
    layout.addLayout(makeLayoutLineEditLabel(widget_manager, key_label=key_label, key_lineedit=key_lineedit, label=label))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Browse"))
    return layout

# Load Files, Exit, Help
def makeLayoutLoadFileExitHelp(
        widget_manager: WidgetManager, 
        list_key: List[str] = ["load_file", "exit", "help"], 
        list_label: List[str] = ["Load Files", "Exit", "Help"]
        ) -> QHBoxLayout:
    layout = QHBoxLayout()
    for label, key in zip(list_label, list_key):
        layout.addWidget(widget_manager.makeWidgetButton(key=key, label=label))
    return layout

# Table, ROICheck IO
def makeLayoutROICheckIO(
        widget_manager: WidgetManager, 
        key_button_save: str,
        key_button_load: str,
        )-> QHBoxLayout:
    layout = QHBoxLayout()
    list_key = [key_button_save, key_button_load]
    list_label = ["Save ROICheck", "Load ROICheck"]
    for key, label in zip(list_key, list_label):
        layout.addWidget(widget_manager.makeWidgetButton(key=key, label=label))
    return layout

# ROI Tracking IO
def makeLayoutROITrackingIO(
        widget_manager: WidgetManager,
        key_button_save_roi_tracking: str,
        key_button_load_roi_tracking: str
) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key_button_save_roi_tracking, "Save ROI Tracking"))
    layout.addWidget(widget_manager.makeWidgetButton(key_button_load_roi_tracking, "Load ROI Tracking"))
    return layout

# ROI Manager IO
def makeLayoutROIManagerIO(
        widget_manager: WidgetManager, 
        key_button_save: str,
        key_button_load: str,
        )-> QHBoxLayout:
    layout = QHBoxLayout()
    list_key = [key_button_save, key_button_load]
    list_label = ["Save ROI.zip", "Load ROI.zip"]
    for key, label in zip(list_key, list_label):
        layout.addWidget(widget_manager.makeWidgetButton(key=key, label=label))
    return layout

# Cellpose Mask npy IO
def makeLayoutCellposeMaskNpyIO(
        widget_manager: WidgetManager, 
        key_button_save: str,
        key_button_load: str,
        )-> QHBoxLayout:
    layout = QHBoxLayout()
    # list_key = [key_button_save, key_button_load]
    # list_label = ["Save Mask", "Load Mask"]
    list_key = [key_button_load]
    list_label = ["Load Cellpose Mask"]
    for key, label in zip(list_key, list_label):
        layout.addWidget(widget_manager.makeWidgetButton(key=key, label=label))
    return layout