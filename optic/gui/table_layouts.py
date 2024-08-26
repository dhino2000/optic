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