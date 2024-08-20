from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QSlider
from PyQt5.QtCore import Qt
from .base_layouts import makeLayoutLineEditLabel
from ..io.file_dialog import openFileDialogAndSetLineEdit

# 読み込むファイルを選択するためのウィジェット
def makeLayoutLoadFileWidget(widget_manager, label="", key_label="", key_lineedit="", key_button="", filetype=None):
    layout = QHBoxLayout() # entry
    layout.addLayout(makeLayoutLineEditLabel(widget_manager, key_label=key_label, key_lineedit=key_lineedit, label=label))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Browse", func_=lambda: openFileDialogAndSetLineEdit(widget_manager, filetype, widget_manager.dict_lineedit[key_lineedit])))
    return layout