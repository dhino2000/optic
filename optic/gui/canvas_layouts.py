from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from .base_layouts import makeLayoutLineEditLabel, makeLayoutComboBoxLabel

# F, Fneu, spks, event plotting canvas Layout
def makeLayoutCanvasTracePlot(
        widget_manager: WidgetManager, 
        key_figure: str, 
        key_canvas: str, 
        key_button: str,
        toolbar: bool=False
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    widget_manager.makeWidgetFigure(key_figure)
    widget_manager.makeWidgetFigureCanvas(key_canvas, widget_manager.dict_figure[key_figure])

    canvas = widget_manager.dict_canvas[key_canvas]
    if toolbar:
        layout.addWidget(NavigationToolbar2QT(canvas, None))
    layout.addWidget(canvas)
    layout.addWidget(widget_manager.makeWidgetButton(key=key_button, label="Export Figure"))
    return layout

# Canvas plot, plot range
def makeLayoutMinimumPlotRange(
        widget_manager: WidgetManager, 
        config_manager: ConfigManager, 
        app_key: AppKeys,
        ) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addLayout(makeLayoutLineEditLabel
                     (
                    widget_manager, 
                    key_label=f"{app_key}_plot_min_width", 
                    key_lineedit=f"{app_key}_plot_min_width", 
                    label="Minimum plot range (sec)", 
                    axis="vertical",
                    text_set=f"{config_manager.gui_defaults['CANVAS_SETTINGS']['MIN_PLOT_WIDTH_SEC']}",
                    )
                )
    return layout

# Canvas plot, Light mode
def makeLayoutLightPlotMode(
        widget_manager: WidgetManager, 
        config_manager: ConfigManager
        ) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetCheckBox(key="light_plot_mode", label="Light Mode", checked=False))
    layout.addLayout(makeLayoutLineEditLabel
                     (
                    widget_manager, 
                    key_label="light_plot_mode_threshold", 
                    key_lineedit="light_plot_mode_threshold",         
                    label="Plot data size (x4)", 
                    axis="vertical",
                    text_set=f"{config_manager.gui_defaults['CANVAS_SETTINGS']['LIGHT_MODE_DOWNSAMPLE']}",
                    )
                )
    return layout

# Eventfile plot, Eventfile plot range, F - Fneu, DF/F0
def makeLayoutEventFilePlotProperty(
        widget_manager: WidgetManager,
        key_button_load_eventfile: str,
        key_button_clear_eventfile: str,
        key_checkbox_plot_eventfile: str,
        key_checkbox_plot_eventfile_ffneu: str,
        key_checkbox_plot_eventfile_dff0: str, 
        key_label_prop_range: str,
        key_label_prop_ffneu: str,
        key_label_prop_dff0: str,
        key_label_combobox_eventfile: str,
        key_lineedit_prop_range: str,
        key_lineedit_prop_ffneu: str,
        key_lineedit_prop_dff0: str,
        key_combobox_eventfile: str,
        app_key: AppKeys,
        ) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout_prop = QHBoxLayout()
    layout_prop_range, layout_prop_ffneu, layout_prop_dff0 = QVBoxLayout(), QVBoxLayout(), QVBoxLayout()
    layout_prop_range.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_plot_eventfile, 
                                                                label="plot EventFile trace", 
                                                                checked=True,
                                                                ))
    layout_prop_range.addLayout(makeLayoutLineEditLabel(widget_manager,
                                                        key_label=key_label_prop_range,
                                                        key_lineedit=key_lineedit_prop_range,
                                                        label="plot range from Event start (pre, post; sec)",
                                                        text_set="(10, 10)"))
    layout_prop.addLayout(layout_prop_range)
    layout_prop_ffneu.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_plot_eventfile_ffneu, 
                                                                label="plot F - Fneu * factor", 
                                                                checked=True,
                                                                ))
    layout_prop_ffneu.addLayout(makeLayoutLineEditLabel(widget_manager,
                                                        key_label=key_label_prop_ffneu,
                                                        key_lineedit=key_lineedit_prop_ffneu,
                                                        label="Fneu factor",
                                                        text_set="0.7"))
    layout_prop.addLayout(layout_prop_ffneu)
    layout_prop_dff0.addWidget(widget_manager.makeWidgetCheckBox(key=key_checkbox_plot_eventfile_dff0, 
                                                                label="plot DF/F0", 
                                                                checked=True,
                                                                ))
    layout_prop_dff0.addLayout(makeLayoutLineEditLabel(widget_manager,
                                                        key_label=key_label_prop_dff0,
                                                        key_lineedit=key_lineedit_prop_dff0,
                                                        label="F0 percentile",
                                                        text_set="35"))
    layout_prop.addLayout(layout_prop_dff0)
    layout.addLayout(layout_prop)
    layout_button = QHBoxLayout()
    layout_button.addWidget(widget_manager.makeWidgetButton(key=key_button_load_eventfile, label="Load EventFile npy file"))
    layout_button.addWidget(widget_manager.makeWidgetButton(key=key_button_clear_eventfile, label="Clear"))
    layout.addLayout(layout_button)
    layout.addLayout(makeLayoutComboBoxLabel(widget_manager,
                                             key_label=key_label_combobox_eventfile,
                                             key_combobox=key_combobox_eventfile,
                                             label="Loaded EventFile",
                                             ))
    return layout

