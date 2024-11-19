from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutSliderLabel

# Layout for contrast slider, channel visible checkbox
def makeLayoutContrastSlider(
        widget_manager: WidgetManager, 
        key_label: str, 
        key_checkbox: str, 
        key_slider: str, 
        label_checkbox: str, 
        label_label: str, 
        checked: bool=True, 
        value_min: int=0, 
        value_max: int=255
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    # checkbox
    layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_checkbox}_show", label=label_checkbox, checked=checked))

    # Min, Max Value slider
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

# Layout for opacity sliders, ALL ROI, Selected ROI
def makeLayoutOpacitySlider(widget_manager: WidgetManager, key_label: str, key_slider: str, label: str) -> QHBoxLayout:
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