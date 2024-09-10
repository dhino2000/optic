from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# Widget作成関数
"""
make Widget Function
"""
# QLabel Widget
def makeWidgetLabel(label, align=Qt.AlignLeft):
    widget = QLabel(label)
    widget.setAlignment(align)
    return widget

# QCheckBox Widget
def makeWidgetCheckBox(label, func_=None, checked=False):
    widget = QCheckBox(label)
    widget.setChecked(checked) 
    if func_:
        widget.stateChanged.connect(func_)
    return widget

# QLineEdit
def makeWidgetLineEdit(text_set="", width_fix=None):
    widget = QLineEdit()
    if width_fix:
        widget.setFixedWidth(width_fix)
    widget.setText(text_set)
    return widget

# QSlider Widget
def makeWidgetSlider(func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
    widget = QSlider(axis)
    widget.setMinimum(value_min)
    widget.setMaximum(value_max)
    widget.setMaximumHeight(height)
    widget.setValue(value_set)
    if func_:
        widget.valueChanged.connect(lambda value: func_(value))
    return widget

# QPushButton Widget
def makeWidgetButton(label, func_=None):
    widget = QPushButton(label)
    if func_:
        widget.clicked.connect(func_)
    return widget

# QTable Widget
def makeWidgetTable():
    widget = QTableWidget()
    return widget

# QTable ListWidget
def makeWidgetListbox(parent=None, 
                      items=None, 
                      selection_mode=QListWidget.SingleSelection,
                      editable=False,
                      drag_drop_mode=QListWidget.NoDragDrop):
    """
    QListWidgetを作成し、設定する関数

    :param parent: 親ウィジェット
    :param items: リストに追加するアイテムのリスト
    :param selection_mode: 選択モード
    :param editable: アイテムを編集可能にするかどうか
    :param drag_drop_mode: ドラッグ＆ドロップモード
    :return: 設定されたQListWidget
    """
    widget = QListWidget(parent)
    
    if items:
        widget.addItems(items)
    
    widget.setSelectionMode(selection_mode)
    
    # 編集可能設定
    if editable:
        widget.setEditTriggers(QAbstractItemView.DoubleClicked)
    
    # ドラッグ＆ドロップモード設定
    widget.setDragDropMode(drag_drop_mode)
    
    return widget

# Figure Widget
def makeWidgetFigure():
    widget = Figure()
    return widget

# FiugreCanvasQTAgg Widget
def makeWidgetFigureCanvas(figure):
    widget = FigureCanvasQTAgg(figure)
    return widget

# QGraphicsScene Widget
def makeWidgetScene():
    widget = QGraphicsScene()
    return widget

# QGraphicsView Widget
def makeWidgetView(scene, width_min=None, height_min=None, color="black", anti_aliasing=True, smooth_pixmap_transform=True):
    widget = QGraphicsView(scene)
    if width_min:
        widget.setMinimumHeight(width_min)
    if height_min:
        widget.setMinimumWidth(height_min)
    widget.setStyleSheet(f"background-color: {color};")  # 背景色を黒に設定
    widget.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    if anti_aliasing:
        widget.setRenderHint(QPainter.Antialiasing)  # アンチエイリアシングを有効化
    if smooth_pixmap_transform:
        widget.setRenderHint(QPainter.SmoothPixmapTransform)  # スムーズなピクセルマップ変換を有効化
    return widget

# figureのaxisに追加, 位置を指定
def addWidgetAxisOnFigure(figure, num_row, num_col, position):
    figure = figure.add_subplot(num_row, num_col, position)
    return figure



"""
GUI Widget管理用クラス
"""
class WidgetManager:
    def __init__(self):
        self.dict_label       = {} # labelの保管
        self.dict_lineedit    = {} # lineeditの保管
        self.dict_button      = {} # buttonの保管
        self.dict_ax          = {} # axの保管
        self.dict_checkbox    = {} # checkboxの保管
        self.dict_slider      = {} # sliderの保管
        self.dict_combobox    = {} # pulldownの保管
        self.dict_listbox     = {} # ListWidgetの保管
        self.dict_buttongroup = {}
        self.dict_scene       = {}
        self.dict_view        = {}
        self.dict_table       = {}
        self.dict_figure      = {}
        self.dict_canvas      = {}

    def makeWidgetLabel(self, key, label, align=Qt.AlignLeft):
        self.dict_label[key] = makeWidgetLabel(label, align)
        return self.dict_label[key]
    
    def makeWidgetCheckBox(self, key, label, func_=None, checked=False):
        self.dict_checkbox[key] = makeWidgetCheckBox(label, func_, checked)
        return self.dict_checkbox[key]
    
    def makeWidgetLineEdit(self, key, text_set="", width_fix=None):
        self.dict_lineedit[key] = makeWidgetLineEdit(text_set, width_fix)
        return self.dict_lineedit[key]
    
    def makeWidgetSlider(self, key, func_=None, value_min=0, value_max=255, value_set=10, height=10, axis=Qt.Horizontal):
        self.dict_slider[key] = makeWidgetSlider(func_, value_min, value_max, value_set, height, axis)
        return self.dict_slider[key]
    
    def makeWidgetButton(self, key, label, func_=None):
        self.dict_button[key] = makeWidgetButton(label, func_)
        return self.dict_button[key]

    def makeWidgetTable(self, key):
        self.dict_table[key] = makeWidgetTable()
        return self.dict_table[key]
    
    def makeWidgetListbox(self, key, parent=None, items=None, selection_mode=QListWidget.SingleSelection, editable=False, drag_drop_mode=QListWidget.NoDragDrop):
        self.dict_listbox[key] = makeWidgetListbox(parent, items, selection_mode, editable, drag_drop_mode)
        return self.dict_listbox[key]

    def makeWidgetFigure(self, key):
        self.dict_figure[key] = Figure()
        return self.dict_figure[key]

    def makeWidgetFigureCanvas(self, key, figure):
        self.dict_canvas[key] = FigureCanvasQTAgg(figure)
        return self.dict_canvas[key]

    def makeWidgetScene(self, key):
        self.dict_scene[key] = makeWidgetScene()
        return self.dict_scene[key]

    def makeWidgetView(self, key, width_min=None, height_min=None, color="black", anti_aliasing=True, smooth_pixmap_transform=True):
        scene = self.makeWidgetScene(key)
        self.dict_view[key] = makeWidgetView(scene, width_min, height_min, color, anti_aliasing, smooth_pixmap_transform)
        return self.dict_view[key]

    def addWidgetAxisOnFigure(self, key, figure, num_row, num_col, position):
        self.dict_ax[key] = figure.add_subplot(num_row, num_col, position)
        return self.dict_ax[key]