# canvasのplot用
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

# F, Fneu, spks, eventのプロットプロット用のcanvas Layout
def makeLayoutCanvasTracePlot(widget_manager, key_figure, key_canvas, key_app="pri", toolbar=True):
    # プロットウィジェットの設定
    layout = QVBoxLayout()
    widget_manager.makeWidgetFigure(key_figure)
    widget_manager.makeWidgetFigureCanvas(key_canvas, widget_manager.dict_figure[key_figure])

    canvas = widget_manager.dict_canvas[key_canvas]
    toolbar = NavigationToolbar2QT(canvas, None)
    if toolbar:
        layout.addWidget(toolbar)
    layout.addWidget(canvas)
    return layout