# 配置した後のwidgetに関数を紐づけ
# makeLayout <- -> bindFunc
from ..io.file_dialog import openFileDialogAndSetLineEdit

# -> makeLayoutLoadFileWidget
def bindFuncLoadFileWidget(q_widget, q_button, q_lineedit, filetype=None):
    q_button.clicked.connect(lambda: openFileDialogAndSetLineEdit(q_widget, filetype, q_lineedit))

# -> makeLayoutContrastSlider
def bindFuncContrastSlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))

# -> makeLayoutOpacitySlider
def bindFuncOpacitySlider(q_slider):
    q_slider.valueChanged.connect(lambda value: func_(value))