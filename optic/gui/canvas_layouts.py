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

# Canvas plot, Light mode
def makeLayoutComponentLightPlotMode(widget_manager, config_manager):
    layout = QHBoxLayout()
    layout.addWidget(widget_manager.makeWidgetCheckBox(key="light_plot_mode", label="Light Mode", checked=False))
    layout.addLayout(makeLayoutLineEditLabel
                     (
                    widget_manager, 
                    key_label="light_plot_mode_threshold", 
                    key_lineedit="light_plot_mode_threshold",         
                    label="Plot data size (x4): ", 
                    axis="horizontal", 
                    text_set=f"{config_manager.gui_defaults["LIGHT_MODE_DOWNSAMPLE"]}", 
                    )
                )
    return layout

