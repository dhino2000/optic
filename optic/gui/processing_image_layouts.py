from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from ..gui.base_layouts import makeLayoutComboBoxLabel, makeLayoutSliderLabel

# Fall Image Registration config
def makeLayoutFallRegistration(
        widget_manager               : WidgetManager, 
        data_manager                 : DataManager,
        app_key                      : str,
        key_label_elastix_method     : str, 
        key_label_ref_c              : str,
        key_label_opacity_pair       : str,
        key_combobox_elastix_method  : str, 
        key_combobox_ref_c           : str,
        key_button_config            : str,
        key_button_run               : str,
        key_checkbox_show_roi_match  : str,
        key_checkbox_show_roi_pair   : str,
        key_checkbox_show_reg_im_bg  : str,
        key_checkbox_show_reg_im_roi : str,
        key_slider_opacity_pair      : str,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_elastix_method, label="Image Registration", bold=True, italic=True, use_global_style=False))
    layout_elastix = QHBoxLayout()
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_elastix_method, 
        key_combobox_elastix_method, 
        "Elastix method:", 
        axis="horizontal", 
        items=["rigid", "affine", "bspline"]
        ))
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_c, 
        key_combobox_ref_c, 
        "Reference channel:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getNChannels(app_key))]
        ))
    layout_elastix.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout_elastix.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Elastix"))
    layout_checkbox = QHBoxLayout()
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_roi_match, label="Show Matched ROI", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_roi_pair, label="Show ROI pairs", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg_im_bg, label="Show Registered Image", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg_im_roi, label="Show Registered ROI", checked=True))
    layout_slider = QHBoxLayout()
    layout_slider.addLayout(makeLayoutSliderLabel(widget_manager, key_label_opacity_pair, key_slider_opacity_pair, "Opacity of ROI pair", value_set=255))

    layout.addLayout(layout_elastix)
    layout.addLayout(layout_checkbox)
    layout.addLayout(layout_slider)
    return layout

# Microglia XYCT Stack Image Registration config
def makeLayoutMicrogliaXYCTStackRegistration(
        widget_manager              : WidgetManager, 
        n_channels                  : int,
        t_planes                    : int,
        key_label_elastix_method    : str, 
        key_label_ref_c             : str,
        key_label_ref_t             : str,
        key_label_opacity_pair      : str,
        key_combobox_elastix_method : str, 
        key_combobox_ref_c          : str,
        key_combobox_ref_t          : str,
        key_button_config           : str,
        key_button_run_t            : str,
        key_button_export           : str,
        key_checkbox_show_roi_match : str,
        key_checkbox_show_roi_pair  : str,
        key_checkbox_show_reg_im_bg : str,
        key_checkbox_show_reg_im_roi: str,
        key_slider_opacity_pair     : str,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_elastix_method, label="Image Registration", bold=True, italic=True, use_global_style=False))
    layout_elastix = QHBoxLayout()
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_elastix_method, 
        key_combobox_elastix_method, 
        "Elastix method:", 
        axis="horizontal", 
        items=["rigid", "affine", "bspline"]
        ))
    layout_elastix.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout_ref_plane = QHBoxLayout()
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_c, 
        key_combobox_ref_c, 
        "Reference channel:", 
        axis="horizontal",
        items=[str(i) for i in range(n_channels)]
        ))
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_t, 
        key_combobox_ref_t, 
        "Reference T plane:", 
        axis="horizontal",
        items=[str(i) for i in range(t_planes)]
        ))
    
    layout_run = QHBoxLayout()
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run_t, label="Run Elastix (t-axis)"))
    layout_checkbox = QHBoxLayout()
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_roi_match, label="Show Matched ROI", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_roi_pair, label="Show ROI pairs", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg_im_bg, label="Show Registered Image", checked=True))
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg_im_roi, label="Show Registered ROI", checked=True))
    layout_slider = QHBoxLayout()
    layout_slider.addLayout(makeLayoutSliderLabel(widget_manager, key_label_opacity_pair, key_slider_opacity_pair, "Opacity of ROI pair", value_set=255))

    layout.addLayout(layout_elastix)
    layout.addLayout(layout_ref_plane)
    layout.addLayout(layout_run)
    layout.addLayout(layout_checkbox)
    layout.addLayout(layout_slider)
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_export, label="Export Registered Image"))
    return layout

# Stack Image Registration config
def makeLayoutStackRegistration(
        widget_manager              : WidgetManager, 
        data_manager                : DataManager,
        app_key                     : str,
        key_label_elastix_method    : str, 
        key_label_ref_c             : str,
        key_label_ref_t             : str,
        key_label_ref_z             : str,
        key_combobox_elastix_method : str, 
        key_combobox_ref_c          : str,
        key_combobox_ref_t          : str,
        key_combobox_ref_z          : str,
        key_button_config           : str,
        key_button_run_t            : str,
        key_button_run_z            : str,
        key_button_export           : str,
        key_checkbox_show_reg       : str,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_elastix_method, label="Image Registration", bold=True, italic=True, use_global_style=False))
    layout_elastix = QHBoxLayout()
    layout_elastix.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_elastix_method, 
        key_combobox_elastix_method, 
        "Elastix method:", 
        axis="horizontal", 
        items=["rigid", "affine", "bspline"]
        ))
    layout_elastix.addLayout(makeLayoutElastixConfig(widget_manager, key_button_config))
    layout_ref_plane = QHBoxLayout()
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_c, 
        key_combobox_ref_c, 
        "Reference channel:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfC(app_key))]
        ))
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_t, 
        key_combobox_ref_t, 
        "Reference T plane:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfT(app_key))]
        ))
    layout_ref_plane.addLayout(makeLayoutComboBoxLabel(
        widget_manager, 
        key_label_ref_z, 
        key_combobox_ref_z, 
        "Reference Z plane:", 
        axis="horizontal",
        items=[str(i) for i in range(data_manager.getSizeOfZ(app_key))]
        ))
    layout_run = QHBoxLayout()
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run_t, label="Run Elastix (t-axis)"))
    layout_run.addWidget(widget_manager.makeWidgetButton(key=key_button_run_z, label="Run Elastix (z-axis)"))
    layout_checkbox = QHBoxLayout()
    layout_checkbox.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_show_reg, label="Show Registered Image", checked=True))

    layout.addLayout(layout_elastix)
    layout.addLayout(layout_ref_plane)
    layout.addLayout(layout_run)
    layout.addLayout(layout_checkbox)
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_export, label="Export Image"))
    return layout

# save elastix transform parameter
def makeLayoutSaveElastixTransform(
        widget_manager: WidgetManager, 
        key_button: str
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Save Elastix Transform Parameters"))
    return layout

# load and apply elastix transform parameter
def makeLayoutApplyElastixTransform(
        widget_manager: WidgetManager, 
        key_label: str,
        key_button_xyct_xyczt: str
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Load and Apply Elastix Transform Parameters", font_size=12, bold=True, italic=True, use_global_style=False))
    layout_button = QHBoxLayout()
    layout_button.addWidget(widget_manager.makeWidgetButton(key=key_button_xyct_xyczt, label="XYCT -> XYCZT"))
    layout.addLayout(layout_button)
    return layout

# Elastix Config
def makeLayoutElastixConfig(widget_manager: WidgetManager, key_button: str) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Elastix Config"))
    return layout

# Stack Image Normalization config
def makeLayoutStackNormalization(
        widget_manager      : WidgetManager,
        key_label           : str,
        key_label_area      : str,
        key_lineedit_area   : str,
        key_button_area     : str,
        key_button_add      : str,
        key_button_remove   : str,
        key_button_clear    : str,
        key_button_run      : str,
        key_listwidget      : str,
    ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Image Normalization", bold=True, italic=True, use_global_style=False))
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label_area, label="Area for Normalization (x_min, x_max, y_min, y_max, z_min, z_max, t_min, t_max)"))
    layout.addWidget(widget_manager.makeWidgetLineEdit(key=key_lineedit_area, text_set="0, 511, 0, 511, 0, 0, 0, 0"))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_area, label="Set reference area"))
    layout_add_remove = QHBoxLayout()
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_add, label="Add current area"))
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_remove, label="Remove selected area"))
    layout_add_remove.addWidget(widget_manager.makeWidgetButton(key=key_button_clear, label="Clear all areas"))
    layout.addLayout(layout_add_remove)
    layout.addWidget(widget_manager.makeWidgetListWidget(key=key_listwidget))
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button_run, label="Run Image Normalization"))
    return layout

# Concatenate tif image and cellpose npy mask, export FallLike.mat
def makeLayoutExportFallLike(
        widget_manager: WidgetManager,
        key_label: str,
        key_button_load_mask: str,
        key_button_export: str
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetLabel(key=key_label, label="Make FallLike.mat", font_size=12, bold=True, italic=True, use_global_style=False))
    layout_button = QHBoxLayout()
    layout_button.addWidget(widget_manager.makeWidgetButton(key=key_button_load_mask, label="Load cellpose seg.npy (XY image)"))
    layout_button.addWidget(widget_manager.makeWidgetButton(key=key_button_export, label="Export FallLike.mat"))
    layout.addLayout(layout_button)
    return layout 