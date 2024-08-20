from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout

# F, Fneu, spks, eventのプロットプロット用のcanvas Layout
def makeLayoutCanvasTracePlot(widget_manager, key_figure, key_canvas):
    # プロットウィジェットの設定
    layout = QVBoxLayout()
    widget_manager.dict_figure[key_figure] = Figure()
    widget_manager.dict_canvas[key_canvas] = FigureCanvas(widget_manager.dict_figure[key_figure])
    for i, key_ax in enumerate(["top", "middle", "bottom"]):
        widget_manager.dict_ax[f"{key_canvas}_{key_ax}"] = widget_manager.dict_figure[key_figure].add_subplot(3, 1, i+1)
    widget_manager.dict_figure[key_figure].subplots_adjust(top=0.95, bottom=0.1, right=0.9, left=0.1, hspace=0.4)
    # イベントハンドラの設定
    # widget_manager.dict_canvas[key].mpl_connect('scroll_event', lambda event: self.onScrollTopAxis(event, key))
    # widget_manager.dict_canvas[key].mpl_connect('button_press_event', lambda event: self.onPressTopAxis(event, key))
    # widget_manager.dict_canvas[key].mpl_connect('button_release_event', lambda event: self.onReleaseTopAxis(event, key))
    # widget_manager.dict_canvas[key].mpl_connect('motion_notify_event', lambda event: self.onMotionTopAxis(event, key))
    # widget_manager.dict_canvas[key].mpl_connect('button_press_event', lambda event: self.onClickMiddleAxis(event, key))

    layout.addWidget(widget_manager.dict_canvas[key_canvas])
    return layout