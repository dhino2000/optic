from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

# 選択した細胞のプロパティを表示
def makeLayoutROIProperty(widget_manager: WidgetManager, key_label: str) -> QVBoxLayout:
    layout = QVBoxLayout()
    # ROIの中心座標, size, radius, aspect_ratio, compact, footprint, solidity, skew(歪度), std
    for list_roi_prop in (["med", "npix", "npix_soma", "radius", "aspect_ratio"], ["compact", "solidity", "footprint", "skew", "std"]):
        layout_hbox = QHBoxLayout()
        for roi_prop in list_roi_prop:
            layout_hbox.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_{roi_prop}", label=f"{roi_prop}: "))
        layout.addLayout(layout_hbox)
    return layout

# Cell ROI, Not Cell ROI, All ROIの数を表示するlabel用Layout
def makeLayoutROICount(widget_manager: WidgetManager, key_label: str, table_columns: TableColumns) -> QHBoxLayout:
    layout = QHBoxLayout()
    # ROI number label
    list_celltype = ["All"]
    list_celltype += [key for key, value in table_columns.items() if value['type'] == 'celltype']
    for celltype in list_celltype:
        text = f"{celltype}: 0"
        layout.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_roicount_{celltype}", label=text))  # レイアウトにラベルを追加
    return layout