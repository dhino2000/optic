# viewに関係するlayout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from .base_layouts import makeLayoutLineEditLabel, makeLayoutButtonGroup

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

# 表示するROIの種類を選択するbuttongroup
def makeLayoutROITypeDisplay(widget_manager, key_buttongroup):
    # ROIの表示切り替え All, Cell, Not Cell
    roidisp_options = ["All ROI"]
    # Table colをもとに作成
    roidisp_options.extend([key for key, value in widget_manager.dict_tablecol.items() if value['type'] == 'radio'])
    roidisp_options.append("None")
    layout = makeLayoutButtonGroup(widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=roidisp_options)
    return layout

# 表示するbackgroundを選択するbuttongroup
def makeLayoutBGImageTypeDisplay(widget_manager, key_buttongroup):
    # 背景画像の切り替え meanImg, meanImgE, max_proj, Vcorr, RefImg
    bg_types = ["meanImg", "meanImgE", "max_proj", "Vcorr"]
    layout = widget_manager.makeLayoutButtonGroup(widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=bg_types)
    return layout

# 画面クリック時 Astrocyte, Neuron, Not Cell, Check, TrackingのROIをスキップするか
def makeLayoutROIChooseSkip(widget_manager, key_checkbox):
    layout = QHBoxLayout()
    skip_items = [key for key, value in widget_manager.dict_tablecol.items() if value['type'] in ['radio', 'checkbox']]
    for item in skip_items:
        key_checkbox_item = f"skip_{item}"
        label_checkbox_item = f"Skip {item} ROI"
        layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_checkbox}_{key_checkbox_item}", label=label_checkbox_item))
    return layout