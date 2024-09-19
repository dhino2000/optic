# TableWidget Layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from .base_layouts import makeLayoutLineEditLabel
from .info_layouts import makeLayoutROICount

# TableWidgetとROI数のラベル
def makeLayoutTableROICountLabel(widget_manager, key_label, key_table, table_columns):
    layout = QVBoxLayout()
    # table
    q_table = widget_manager.makeWidgetTable(key=key_table)
    
    # label
    layout_label = makeLayoutROICount(widget_manager, key_label, table_columns)

    layout.addWidget(q_table)
    layout.addLayout(layout_label)
    return layout

# 全てのROIを同じcelltypeにそろえる
def makeLayoutAllROISetSameCelltype(widget_manager, key_button, table_columns):
    layout = QHBoxLayout()

    list_celltype = [key for key, value in table_columns.items() if value['type'] == 'celltype']
    for celltype in list_celltype:
        layout.addWidget(widget_manager.makeWidgetButton(key=f"{key_button}_roi_set_{celltype}", label=f"Set {celltype}"))
    return layout

# Check, Uncheck "checkbox" of All ROIs
def makeLayoutAllROICheckboxToggle(widget_manager, key_button, table_columns):
    layout = QHBoxLayout()

    list_checkbox = [key for key, value in table_columns.items() if value['type'] == 'checkbox']
    for checkbox in list_checkbox:
        layout_ = QVBoxLayout()
        layout_.addWidget(widget_manager.makeWidgetButton(key=f"{key_button}_roi_check_{checkbox}", label=f"Check {checkbox}"))
        layout_.addWidget(widget_manager.makeWidgetButton(key=f"{key_button}_roi_uncheck_{checkbox}", label=f"Uncheck {checkbox}"))
        layout.addLayout(layout_)
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