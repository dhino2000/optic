# 選択した細胞のプロパティなどを表示するlabelなどをまとめたLayout関数
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

# 選択した細胞のプロパティを表示
def makeLayoutROIProperty(widget_manager):
    layout = QVBoxLayout()
    # ROIのsize, radius, aspect_ratio, compact, footprint, skew(歪度), std
    for list_label_key in (["npix", "radius", "aspect_ratio", "compact", "footprint"], ["skew", "std"]):
        layout_hbox = QHBoxLayout()
        for label_key in list_label_key:
            layout_hbox.addWidget(widget_manager.makeWidgetLabel(key=f"roi_prop_{label_key}", label=f"{label_key}: "))
        layout.addLayout(layout_hbox)
    return layout