# viewに関係するlayout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutLineEditLabel

# 表示するROIのThreshold checkbox, lineedit
def makeLayoutROIThresholds(widget_manager, key_label, key_lineedit, key_checkbox, label_checkbox, list_threshold_param=["npix", "compact"]):
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox, label=label_checkbox))
    for threshold_param in list_threshold_param:
        layout.addLayout(makeLayoutLineEditLabel(widget_manager=widget_manager,
                                                key_label=f"{key_label}_{threshold_param}", 
                                                key_lineedit=f"{key_lineedit}_{threshold_param}",
                                                label=threshold_param))
    return layout
