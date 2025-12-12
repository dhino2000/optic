from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

# display ROI properties: med, npix, npix_soma, radius, aspect_ratio, compact, footprint, solidity, skew, std
def makeLayoutROIProperty(
        widget_manager: WidgetManager, 
        key_label: str,
        load_caiman: bool = False
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    if load_caiman:
        # CaImAn ROI properties
        list_list_roi_prop = [
            ["med", "npix", "rval", "SNR", "cnn"],
        ]
    else:
        # Suite2p ROI properties
        list_list_roi_prop = [
            ["med", "npix", "npix_soma", "radius", "aspect_ratio"],
            ["compact", "solidity", "footprint", "skew", "std"]
        ]
    for list_roi_prop in list_list_roi_prop:
        layout_hbox = QHBoxLayout()
        for roi_prop in list_roi_prop:
            layout_hbox.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_{roi_prop}", label=f"{roi_prop}: "))
        layout.addLayout(layout_hbox)
    return layout

# display ROI count labels
def makeLayoutROICount(
        widget_manager: WidgetManager, 
        key_label: str, 
        table_columns: TableColumns
        ) -> QHBoxLayout:
    layout = QHBoxLayout()
    # ROI number label
    list_celltype = ["All"]
    list_celltype += [key for key, value in table_columns.getColumns().items() if value['type'] == 'celltype']
    for celltype in list_celltype:
        text = f"{celltype}: 0"
        layout.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_roicount_{celltype}", label=text))  # レイアウトにラベルを追加
    return layout