from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QSlider
from PyQt5.QtCore import Qt
from .base_layouts import makeLayoutLineEditLabel
from ..io.file_dialog import openFileDialogAndSetLineEdit

# 読み込むファイルを選択するためのウィジェット
def makeLayoutLoadFileWidget(widget_manager, label="", key_label="", key_lineedit="", key_button=""):
    layout = QHBoxLayout() # entry
    layout.addLayout(makeLayoutLineEditLabel(widget_manager, key_label=key_label, key_lineedit=key_lineedit, label=label))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Browse"))
    return layout

