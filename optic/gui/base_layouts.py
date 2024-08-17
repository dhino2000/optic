# QLineEdit Layout label付き
def makeLayoutLineEditLabel(self, key_label, key_lineedit, label, text_set="", width_fix=None):
    layout = QVBoxLayout()
    layout.addWidget(self.makeWidgetLabel(key=key_label, label=label))
    layout.addWidget(self.makeWidgetLineEdit(key=key_lineedit, text_set=text_set, width_fix=width_fix))
    return layout

# QButtonGroup Layout
def makeLayoutButtonGroup(self, key, list_label, set_exclusive=True):
    layout = QHBoxLayout()
    self.dict_buttongroup[key] = QButtonGroup(self)
    self.dict_buttongroup[key].setExclusive(set_exclusive)

    for i, label in enumerate(list_label):
        radioButton = QRadioButton(label)
        if i == 0:  # 1番目にチェック
            radioButton.setChecked(True)
        layout.addWidget(radioButton)
        self.dict_buttongroup[key].addButton(radioButton, i)

    return layout

# QSlider Layout label付き
def makeLayoutSliderLabel(self, key_label, key_slider, label, align=Qt.AlignLeft, func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
    layout = QVBoxLayout()
    label = self.makeWidgetLabel(key_label, label)
    slider = self.makeWidgetSlider(key_slider, func_, value_min, value_max, value_set, height, axis)
    layout.addWidget(label)
    layout.addWidget(slider)
    return layout