# sliderがメインのlayout作成用関数
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutSliderLabel

# 画像のコントラスト調節スライダー、表示チェックボックス用Layout
def makeLayoutContrastSlider(widget_manager, key_label, key_checkbox, key_slider, label_checkbox, label_label, func_slider=None, func_checkbox=None, checked=True):
    layout = QVBoxLayout()
    # チェックボックスの設定
    layout.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox, label=label_checkbox, func_=func_checkbox, checked=checked))

    # Min, Max Valueスライダーの設定
    for m, value_set in zip(["min", "max"], [0, 255]):
        layout.addLayout(makeLayoutSliderLabel
                            (
                            widget_manager,
                            key_label=f"{key_label}_{m}", 
                            key_slider=key_slider, 
                            label=f"{m} {label_label}", 
                            value_set=value_set, 
                            func_=func_slider
                            )
                        )
    return layout

# 透明度調節スライダーのLayout, ALL ROI, Selected ROI
def makeLayoutOpacitySlider(widget_manager, key_label, key_slider, label, func_slider=None):
    layout = QHBoxLayout()
    for (key_, label_, default_value) in zip(['opacity_allroi', 'opacity_selectedroi'],
                                             ['Opacity of All ROI', 'Opacity of Selected ROI'],
                                             [50, 255]):
        layout.addLayout(makeLayoutSliderLabel
                            (
                            widget_manager,
                            key_label=f"{key_label}_{key_}", 
                            key_slider=f"{key_slider}_{key_}", 
                            label=f"{label} {label_}", 
                            value_set=default_value,
                            func_=func_slider
                            )
                        )
    return layout