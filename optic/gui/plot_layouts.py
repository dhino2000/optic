# canvasのplot用
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

# F, Fneu, spks, eventのプロットプロット用のcanvas Layout
def makeLayoutCanvasTracePlot(widget_manager, key_figure, key_canvas, key_app="pri"):
    # プロットウィジェットの設定
    layout = QVBoxLayout()
    widget_manager.makeWidgetFigure(key_figure)
    widget_manager.makeWidgetFigureCanvas(key_canvas, widget_manager.dict_figure[key_figure])
    for i, key_ax in enumerate([f"{key_app}_top", f"{key_app}_middle", f"{key_app}_bottom"]):
        widget_manager.addWidgetAxisOnFigure(key_ax, widget_manager.dict_figure[key_figure], 3, 1, i+1)
    widget_manager.dict_figure[key_figure].subplots_adjust(top=0.95, bottom=0.1, right=0.9, left=0.1, hspace=0.4)

    canvas = widget_manager.dict_canvas[key_canvas]
    toolbar = NavigationToolbar2QT(canvas, None)
    
    layout.addWidget(toolbar)
    layout.addWidget(canvas)
    return layout