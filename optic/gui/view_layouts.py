from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from ..utils.layout_utils import clearLayout
from .base_layouts import makeLayoutLineEditLabel, makeLayoutButtonGroup
from ..config.constants import BGImageTypeList
from ..gui.table_layouts import makeLayoutROIFilterThreshold

def makeLayoutViewWithZTSlider(
        widget_manager: WidgetManager,
        key_view: str,
        slider_z: bool = False,
        slider_t: bool = False,
        key_label_z: str = "",
        key_label_t: str = "",
        key_slider_z: str = "",
        key_slider_t: str = "",
        stack_size_z: int = 1,
        stack_size_t: int = 1,
) -> QVBoxLayout:
    layout = QVBoxLayout()

    q_view = widget_manager.makeWidgetView(key=key_view)
    layout.addWidget(q_view)

    # add z slider
    if slider_z:
        # add label
        label = widget_manager.makeWidgetLabel(key=key_label_z, label="Z: 0")
        layout.addWidget(label)
        slider = widget_manager.makeWidgetSlider(
            key=key_slider_z,
            value_min=0,
            value_max=stack_size_z - 1,
            value_set=0,
        )
        layout.addWidget(slider)

    # add t slider
    if slider_t:
        label = widget_manager.makeWidgetLabel(key=key_label_t, label="T: 0")
        layout.addWidget(label)
        slider = widget_manager.makeWidgetSlider(
            key=key_slider_t,
            value_min=0,
            value_max=stack_size_t - 1,
            value_set=0,
        )
        layout.addWidget(slider)

    return layout

# 表示するROIのThreshold checkbox, lineedit
def makeLayoutROIThresholds(
        widget_manager: WidgetManager, 
        key_label: str, 
        key_lineedit: str, 
        key_button: str, 
        label_button: str, 
        dict_roi_threshold: Dict[str, str]
        ) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label=label_button))
    layout.addLayout(makeLayoutROIFilterThreshold(widget_manager, 
                                                  key_label=key_label, 
                                                  key_lineedit=key_lineedit,
                                                  dict_roi_threshold=dict_roi_threshold))
                                                
    return layout

# 表示するROIの種類を選択するbuttongroup
def makeLayoutDislplayCelltype(q_widget: QWidget, widget_manager: WidgetManager, key_buttongroup: str, table_columns: TableColumns) -> QHBoxLayout:
    # ROIの表示切り替え All, Cell, Not Cell
    roidisp_options = ["All ROI", "None"]
    # Table colをもとに作成
    roidisp_options.extend([key for key, value in table_columns.items() if value['type'] == 'celltype'])
    layout = makeLayoutButtonGroup(q_widget, widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=roidisp_options)
    return layout

# 表示するbackgroundを選択するbuttongroup
def makeLayoutBGImageTypeDisplay(q_widget: QWidget, widget_manager: WidgetManager, key_buttongroup: str) -> QHBoxLayout:
    # 背景画像の切り替え meanImg, meanImgE, max_proj, Vcorr, RefImg
    bg_types = BGImageTypeList.FALL
    layout = makeLayoutButtonGroup(q_widget, widget_manager, key_buttongroup=key_buttongroup, list_label_buttongroup=bg_types)
    return layout

# 画面クリック時 Astrocyte, Neuron, Not Cell, Check, TrackingのROIをスキップするか
def makeLayoutROIChooseSkip(widget_manager: WidgetManager, key_checkbox: str, table_columns: TableColumns) -> QHBoxLayout:
    layout = QHBoxLayout()
    skip_items = [key for key, value in table_columns.items() if value['type'] in ['celltype', 'checkbox']]
    for item in skip_items:
        key_checkbox_item = f"skip_choose_{item}"
        label_checkbox_item = f"Skip {item} ROI"
        layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_checkbox}_{key_checkbox_item}", label=label_checkbox_item))
    return layout