# viewに関係するlayout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from ..utils.layout_utils import clearLayout
from .base_layouts import makeLayoutLineEditLabel, makeLayoutButtonGroup
from ..config.constants import BGImageTypeList
from ..gui.table_layouts import makeLayoutROIFilterThreshold

# 表示するROIのThreshold checkbox, lineedit
def makeLayoutROIThresholds(widget_manager, key_label, key_lineedit, key_button, label_button, dict_roi_threshold):
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label=label_button))
    layout.addLayout(makeLayoutROIFilterThreshold(widget_manager, 
                                                  key_label=key_label, 
                                                  key_lineedit=key_lineedit,
                                                  dict_roi_threshold=dict_roi_threshold))
                                                
    return layout

# 表示するROIの種類を選択するbuttongroup
def makeLayoutDislplayCelltype(q_widget, widget_manager, key_buttongroup, table_columns):
    # ROIの表示切り替え All, Cell, Not Cell
    roidisp_options = ["All ROI", "None"]
    # Table colをもとに作成
    roidisp_options.extend([key for key, value in table_columns.items() if value['type'] == 'celltype'])
    layout = makeLayoutButtonGroup(q_widget, widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=roidisp_options)
    return layout

# 表示するbackgroundを選択するbuttongroup
def makeLayoutBGImageTypeDisplay(q_widget, widget_manager, key_buttongroup):
    # 背景画像の切り替え meanImg, meanImgE, max_proj, Vcorr, RefImg
    bg_types = BGImageTypeList.FALL
    layout = makeLayoutButtonGroup(q_widget, widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=bg_types)
    return layout

# 画面クリック時 Astrocyte, Neuron, Not Cell, Check, TrackingのROIをスキップするか
def makeLayoutROIChooseSkip(widget_manager, key_checkbox, table_columns):
    layout = QHBoxLayout()
    skip_items = [key for key, value in table_columns.items() if value['type'] in ['celltype', 'checkbox']]
    for item in skip_items:
        key_checkbox_item = f"skip_choose_{item}"
        label_checkbox_item = f"Skip {item} ROI"
        layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_checkbox}_{key_checkbox_item}", label=label_checkbox_item))
    return layout