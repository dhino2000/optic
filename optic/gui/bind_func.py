# 配置した後のwidgetに関数を紐づけ
# makeLayout <- -> bindFunc
from ..io.file_dialog import openFileDialogAndSetLineEdit
from ..utils import *

# -> makeLayoutLoadFileWidget
def bindFuncLoadFileWidget(q_widget, q_button, q_lineedit, filetype=None):
    q_button.clicked.connect(lambda: openFileDialogAndSetLineEdit(q_widget, filetype, q_lineedit))

# -> widget_manager.dict_button["exit"]
def bindFuncExit(q_window, q_button):
    q_button.clicked.connect(lambda: exitApp(q_window))

# -> makeLayoutContrastSlider
def bindFuncContrastSlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))

# -> makeLayoutOpacitySlider
def bindFuncOpacitySlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))