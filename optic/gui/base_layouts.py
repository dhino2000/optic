# シンプルな機能を持つlayout作成用関数
# ほぼmakeWidgetと同じ
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QSlider
from PyQt5.QtCore import Qt

# QLineEdit Layout label付き
def makeLayoutLineEditLabel(widget_manager, key_label, key_lineedit, label, text_set="", width_fix=None):
    layout = QVBoxLayout()
    label_widget = widget_manager.makeWidgetLabel(key_label, label)
    lineedit_widget = widget_manager.makeWidgetLineEdit(key_lineedit, text_set, width_fix)
    layout.addWidget(label_widget)
    layout.addWidget(lineedit_widget)
    return layout

# QButtonGroup Layout
def makeLayoutButtonGroup(widget_manager, key, list_label, set_exclusive=True):
    layout = QHBoxLayout()
    button_group = QButtonGroup(widget_manager)
    button_group.setExclusive(set_exclusive)

    for i, label in enumerate(list_label):
        radio_button = QRadioButton(label)
        if i == 0:  # 1番目にチェック
            radio_button.setChecked(True)
        layout.addWidget(radio_button)
        button_group.addButton(radio_button, i)

    widget_manager.dict_buttongroup[key] = button_group
    return layout

# QSlider Layout label付き
def makeLayoutSliderLabel(widget_manager, key_label, key_slider, label, align=Qt.AlignLeft, func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
    layout = QVBoxLayout()
    label_widget = widget_manager.makeWidgetLabel(key_label, label, align)
    slider_widget = widget_manager.makeWidgetSlider(key_slider, func_, value_min, value_max, value_set, height, axis)
    layout.addWidget(label_widget)
    layout.addWidget(slider_widget)
    return layout