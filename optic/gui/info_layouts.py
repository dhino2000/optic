# 選択した細胞のプロパティなどを表示するlabelなどをまとめたLayout関数
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

# 選択した細胞のプロパティを表示
def makeLayoutROIProperty(widget_manager, key_label):
    layout = QVBoxLayout()
    # ROIのsize, radius, aspect_ratio, compact, footprint, skew(歪度), std
    for list_roi_prop in (["npix", "radius", "aspect_ratio", "compact", "footprint"], ["skew", "std"]):
        layout_hbox = QHBoxLayout()
        for roi_prop in list_roi_prop:
            layout_hbox.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_{roi_prop}", label=f"{roi_prop}: "))
        layout.addLayout(layout_hbox)
    return layout