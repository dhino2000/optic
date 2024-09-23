# canvasのplot用
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from .base_layouts import makeLayoutLineEditLabel

# F, Fneu, spks, eventのプロットプロット用のcanvas Layout
def makeLayoutCanvasTracePlot(widget_manager, key_figure, key_canvas, key_app="pri", toolbar=False):
    # プロットウィジェットの設定
    layout = QVBoxLayout()
    widget_manager.makeWidgetFigure(key_figure)
    widget_manager.makeWidgetFigureCanvas(key_canvas, widget_manager.dict_figure[key_figure])

    canvas = widget_manager.dict_canvas[key_canvas]
    if toolbar:
        layout.addWidget(NavigationToolbar2QT(canvas, None))
    layout.addWidget(canvas)
    return layout

# Canvas plot, plot range
def makeLayoutMinimumPlotRange(widget_manager, config_manager, key_app):
    layout = QHBoxLayout()
    layout.addLayout(makeLayoutLineEditLabel
                     (
                    widget_manager, 
                    key_label=f"{key_app}_plot_min_width", 
                    key_lineedit=f"{key_app}_plot_min_width", 
                    label="Minimum plot range (sec)", 
                    axis="vertical",
                    text_set=f"{config_manager.gui_defaults['CANVAS_SETTINGS']['MIN_PLOT_WIDTH_SEC']}",
                    )
                )
    return layout

# Canvas plot, Light mode
def makeLayoutLightPlotMode(widget_manager, config_manager):
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

# Eventfile plot, Eventfile plot range
def makeLayoutEventFilePlot(widget_manager, key_app):
    layout = QVBoxLayout()
    layout.addWidget(widget_manager.makeWidgetCheckBox(key=f"{key_app}_plot_eventfile", 
                                                       label="plot EventFile trace", 
                                                       checked=True,
                                                       ))
    layout.addLayout(makeLayoutLineEditLabel(widget_manager,
                                                key_label=f"{key_app}_plot_eventfile_range",
                                                key_lineedit=f"{key_app}_plot_eventfile_range",
                                                label="plot range from Event start (pre, post; sec)",
                                                text_set="(10, 10)"))
    layout.addWidget(widget_manager.makeWidgetButton(key=f"{key_app}_load_eventfile", label="Load EventFile npy file"))
    layout.addWidget(widget_manager.makeWidgetButton(key=f"{key_app}_clear_eventfile", label="Clear"))
    return layout

