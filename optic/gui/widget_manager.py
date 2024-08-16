from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# Widget作成関数
"""
make Widget Function
"""
# QLabel Widget
def makeWidgetLabel(label, align=Qt.AlignLeft):
    widget = QLabel(label)
    widget.setAlignment(align)
    return widget

# QCheckBox Widget
def makeWidgetCheckBox(label, func_=None, checked=False):
    widget = QCheckBox(label)
    widget.setChecked(checked) 
    if func_:
        widget.stateChanged.connect(func_)
    return widget

# QLineEdit
def makeWidgetLineEdit(text_set="", width_fix=None):
    widget = QLineEdit()
    if width_fix:
        widget.setFixedWidth(width_fix)
    widget.setText(text_set)
    return widget

# QSlider Widget
def makeWidgetSlider(func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
    widget = QSlider(axis)
    widget.setMinimum(value_min)
    widget.setMaximum(value_max)
    widget.setMaximumHeight(height)
    widget.setValue(value_set)
    if func_:
        widget.valueChanged.connect(lambda value: func_(value))
    return widget

# QPushButton Widget
def makeWidgetButton(label, func_=None):
    widget = QPushButton(label)
    if func_:
        widget.clicked.connect(func_)
    return widget



"""
GUI Widget管理用クラス
"""
class WidgetManager:
    def __init__(self):
        self.dict_label       = {} # labelの保管
        self.dict_lineedit    = {} # lineeditの保管
        self.dict_button      = {} # buttonの保管
        self.dict_ax          = {} # axの保管
        self.dict_checkbox    = {} # checkboxの保管
        self.dict_slider      = {} # sliderの保管
        self.dict_combobox    = {} # pulldownの保管
        self.dict_list        = {} # ListWidgetの保管
        self.dict_buttongroup = {}
        self.dict_scene       = {}
        self.dict_view        = {}
        self.dict_table       = {}
        self.dict_figure      = {}
        self.dict_canvas      = {}

    def makeWidgetLabel(self, key, label, align=Qt.AlignLeft):
        self.dict_label[key] = makeWidgetLabel(label, align)
        return self.dict_label[key]
    
    def makeWidgetCheckBox(self, key, label, func_=None, checked=False):
        self.dict_checkbox[key] = makeWidgetCheckBox(label, func_, checked)
        return self.dict_checkbox[key]
    
    def makeWidgetLineEdit(self, key, text_set="", width_fix=None):
        self.dict_lineedit[key] = makeWidgetLineEdit(text_set, width_fix)
        return self.dict_lineedit[key]
    
    def makeWidgetSlider(self, key, func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
        self.dict_slider[key] = makeWidgetSlider(func_, value_min, value_max, value_set, height, axis)
        return self.dict_slider[key]
    
    def makeWidgetButton(self, key, label, func_=None):
        self.dict_button[key] = makeWidgetButton(label, func_)
        return self.dict_button[key]