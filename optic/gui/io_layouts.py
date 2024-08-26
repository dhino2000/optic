from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QSlider
from PyQt5.QtCore import Qt
from .base_layouts import makeLayoutLineEditLabel

# 読み込むファイルを選択するためのウィジェット
def makeLayoutLoadFileWidget(widget_manager, label="", key_label="", key_lineedit="", key_button=""):
    layout = QHBoxLayout() # entry
    layout.addLayout(makeLayoutLineEditLabel(widget_manager, key_label=key_label, key_lineedit=key_lineedit, label=label))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Browse"))
    return layout

# Table, ROICheck, ROIMatchのIO
def makeLayoutROICheckIO(widget_manager, key_button):
    layout = QHBoxLayout()
    list_key = [f"{key_button}_save_roicheck", f"{key_button}_load_roicheck"]
    list_label = ["Save ROICheck", "Load ROICheck"]
    for key, label in zip(list_key, list_label):
        layout.addWidget(widget_manager.makeWidgetButton(key=key, label=label))
    return layout