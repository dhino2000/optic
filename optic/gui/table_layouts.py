# TableWidget Layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
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