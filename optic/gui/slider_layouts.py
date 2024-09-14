# sliderがメインのlayout作成用関数
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutSliderLabel

# 画像のコントラスト調節スライダー、表示チェックボックス用Layout
def makeLayoutContrastSlider(widget_manager, key_label, key_checkbox, key_slider, label_checkbox, label_label, checked=True, value_min=0, value_max=255):
    layout = QVBoxLayout()
    # チェックボックスの設定
    layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_checkbox}_show", label=label_checkbox, checked=checked))

    # Min, Max Valueスライダーの設定
    for m, value_set in zip(["min", "max"], [value_min, value_max]):
        layout.addLayout(makeLayoutSliderLabel
                            (
                            widget_manager,
                            key_label=f"{key_label}_contrast_{m}", 
                            key_slider=f"{key_slider}_contrast_{m}", 
                            label=f"{m} {label_label}", 
                            value_set=value_set, 
                            )
                        )
    return layout

# 透明度調節スライダーのLayout, ALL ROI, Selected ROI
def makeLayoutOpacitySlider(widget_manager, key_label, key_slider, label):
    layout = QHBoxLayout()
    for (key_, label_, default_value) in zip(['opacity_roi_all', 'opacity_roi_selected'],
                                             ['Opacity of All ROI', 'Opacity of Selected ROI'],
                                             [50, 255]):
        layout.addLayout(makeLayoutSliderLabel
                            (
                            widget_manager,
                            key_label=f"{key_label}_{key_}", 
                            key_slider=f"{key_slider}_{key_}", 
                            label=f"{label} {label_}", 
                            value_set=default_value,
                            )
                        )
    return layout