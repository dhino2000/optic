# TableWidget Layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from .base_layouts import makeLayoutLineEditLabel
from .info_layouts import makeLayoutROICount
from .table_setup import setupWidgetROITable

# TableWidgetとROI数のラベル
def makeLayoutTableROICountLabel(widget_manager, key_label, key_table):
    layout = QVBoxLayout()
    # table
    q_table = widget_manager.makeWidgetTable(key=key_table)

    # label
    layout_label = makeLayoutROICount(widget_manager, key_label)

    layout.addWidget(q_table)
    layout.addLayout(layout_label)
    return layout

# 全てのROIを同じcelltypeにそろえる
def makeLayoutAllROISetSameCelltype(widget_manager, key_button):
    layout = QHBoxLayout()

    list_celltype = [key for key in widget_manager.dict_tablecol.keys() if widget_manager.dict_tablecol[key].get("group") == "celltype"]
    for celltype in list_celltype:
        layout.addWidget(widget_manager.makeWidgetButton(key=f"{key_button}_roi_set_{celltype}", label=f"Set {celltype}"))
    return layout

# ROI filter thresholds
def makeLayoutROIFilterThreshold(widget_manager, key_label, key_lineedit, dict_roi_threshold, num_row=2, num_col=3):
    layout = QGridLayout()

    # 配置する要素数がグリッド数を超えていないか
    if num_row * num_col > len(dict_roi_threshold):
        raise ValueError(f"Grid size ({num_row}x{num_col}={num_row*num_col}) is smaller than the number of dict_roi_threshold items ({len(dict_roi_threshold)}).")

    for i, (key_threshold, value_threshold) in enumerate(dict_roi_threshold.items()):
        row = i // num_col
        col = i % num_col
        layout.addLayout(makeLayoutLineEditLabel(
            widget_manager, 
            key_label, 
            key_lineedit, 
            label=key_threshold, 
            axis="vertical", 
            text_set=value_threshold, 
            width_fix=None)
            , row, col, 1, 1)
    return layout

# ROI filter button
def makeLayoutROIFilterButton(widget_manager, key_label, key_button):
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=f"{key_label}_roi_filter", label="<- thresholds (min, max)"))
    layout.addWidget(widget_manager.makeWidgetButton(key=f"{key_button}_roi_filter", label=f"Filter ROI"))
    return layout