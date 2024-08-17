# sliderがメインのlayout作成用関数

# 画像のコントラスト調節スライダー、表示チェックボックス用Layout
def makeLayoutContrastSlider(self, key, label_checkbox, label_label, func_slider=None, func_checkbox=None):
    layout = QVBoxLayout()
    # チェックボックスの設定
    layout.addWidget(self.makeWidgetCheckBox(key, label_checkbox, func_=func_checkbox, checked=True))

    # Min, Max Valueスライダーの設定
    for m, value_set in zip(["min", "max"], [0, 255]):
        layout.addLayout(self.makeLayoutSliderLabel(key_label=f"value_{key}_{m}", 
                                                    key_slider=f"value_{key}_{m}", 
                                                    label=f"{m} {label_label}", 
                                                    value_set=value_set, 
                                                    func_=func_slider))
    return layout

# 透明度調節スライダーのLayout
def makeLayoutOpacitySlider(self):
    layout = QHBoxLayout()
    for (key, label, default_value) in zip(['opacity_allroi', 'opacity_selectedroi'],
                                            ['Opacity of All ROI', 'Opacity of Selected ROI'],
                                            [50, 255]):
        layout.addLayout(self.makeLayoutSliderLabel(key_label=key, 
                                                    key_slider=key, 
                                                    label=label, 
                                                    value_set=default_value,
                                                    func_=lambda value, k="pri": self.onSliderValueChanged(k)))
    return layout

# スライダーをまとめたLayout
def makeLayoutAllSlider(self):
    layout = QGridLayout()
    for i, channel in enumerate(["pri", "sec"]):
        layout.addLayout(self.makeLayoutContrastSlider(key=f"{channel}", 
                                                        label_checkbox=f"Show {channel}", 
                                                        label_label=f"Value ({channel})",
                                                        func_checkbox=lambda state, key="pri", channel=channel: self.toggleChannelVisibility(key, state, channel),
                                                        func_slider=lambda value, k="pri": self.onSliderValueChanged(k)), 
                                                        1, i+1, 1, 1)
    layout.addLayout(self.makeLayoutOpacitySlider(), 2, 1, 1, 2)
    return layout