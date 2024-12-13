from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from ..gui.base_layouts import makeLayoutComboBoxLabel, makeLayoutLineEditLabel
from ..gui.io_layouts import makeLayoutROIManagerIO, makeLayoutMaskNpyIO

# Optimal transport ROI Matching config
def makeLayoutROIMatching(
        widget_manager                   : WidgetManager, 
        key_label_roi_matching           : str, 
        key_label_ot_method              : str,
        key_label_fgwd_alpha             : str,
        key_label_wd_exp                 : str, 
        key_label_threshold_transport    : str,
        key_label_threshold_cost         : str,
        key_lineedit_fgwd_alpha          : str,
        key_lineedit_wd_exp              : str,
        key_lineedit_threshold_transport : str,
        key_lineedit_threshold_cost      : str,
        key_combobox_ot_method           : str,
        key_button_run                   : str,
        key_button_clear                 : str
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_roi_matching, label="ROI Matching", bold=True, italic=True, use_global_style=False))
    layout_ot = QHBoxLayout()
    layout_ot.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ot_method, 
        key_combobox_ot_method, 
        "Optimal Transport method:", 
        axis="horizontal", 
        items=["WD-shape", "WD-distance", "GWD", "FGWD"]
        ))
    layout_ot.addLayout(makeLayoutLineEditLabel(
        widget_manager, 
        key_label_fgwd_alpha, 
        key_lineedit_fgwd_alpha,
        label="FGWD alpha:", 
        text_set="0.1", 
        axis="horizontal"
        ))
    layout_ot.addLayout(makeLayoutLineEditLabel(
        widget_manager, 
        key_label_wd_exp, 
        key_lineedit_wd_exp,
        label="WD-distance exponent:", 
        text_set="2", 
        axis="horizontal"
        ))
    layout_ot_threshold = QHBoxLayout()
    layout_ot_threshold.addLayout(makeLayoutLineEditLabel(
        widget_manager, 
        key_label_threshold_transport, 
        key_lineedit_threshold_transport,
        label="Min transport threshold:", 
        text_set="0.001", 
        axis="horizontal"
        ))
    layout_ot_threshold.addLayout(makeLayoutLineEditLabel(
        widget_manager, 
        key_label_threshold_cost, 
        key_lineedit_threshold_cost,
        label="Max cost threshold:", 
        text_set="10000", 
        axis="horizontal"
        ))
    layout_run = QHBoxLayout()
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Optimal Transport"))
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_clear, label="Clear Matching Results"))
    layout.addLayout(layout_ot)
    layout.addLayout(layout_ot_threshold)
    layout.addLayout(layout_run)
    return layout

def makeLayoutROIMatchingTest(
        widget_manager: WidgetManager,
        key_button_roi_matching_test: str
) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key_button_roi_matching_test, "ROI Matching Test"))
    return layout

# ROI Manager layout
def makeLayoutROIManager(
        widget_manager: WidgetManager,
        key_label_roi_manager: str,
        key_button_save_roi: str,
        key_button_load_roi: str,
        key_button_save_mask: str,
        key_button_load_mask: str
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_roi_manager, label="ROI Manager", bold=True, italic=True, use_global_style=False))
    layout.addLayout(makeLayoutROIManagerIO(widget_manager, key_button_save_roi, key_button_load_roi))
    layout.addLayout(makeLayoutMaskNpyIO(widget_manager, key_button_save_mask, key_button_load_mask))
    return layout