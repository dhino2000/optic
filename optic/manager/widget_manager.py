from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.axes import Axes

# Widget作成関数
"""
make Widget Function
"""
# QLabel Widget
def makeWidgetLabel(
    label: str,
    align: Qt.AlignmentFlag,
    font_family: str, 
    font_size: int,
    color: str,
    bold: bool,
    italic: bool,
    use_global_style: bool
) -> QLabel:
    widget = QLabel(label)
    widget.setAlignment(align)
    widget.setStyleSheet(f"color: {color};")
    
    if use_global_style:
        widget.setObjectName('use-global')
    else:
        font = QFont(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        font.setItalic(italic)
        widget.setFont(font)
    return widget

# QCheckBox Widget
def makeWidgetCheckBox(
    label: str, 
    func_: Callable[..., Any], 
    checked: bool,
    use_global_style: bool
) -> QCheckBox:
    widget = QCheckBox(label)
    widget.setChecked(checked) 
    if func_:
        widget.stateChanged.connect(func_)
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# QLineEdit
def makeWidgetLineEdit(
    text_set: str,
    width_fix: int,
    use_global_style: bool
) -> QLineEdit:
    widget = QLineEdit()
    if width_fix:
        widget.setFixedWidth(width_fix)
    widget.setText(text_set)
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# QSlider Widget
def makeWidgetSlider(
    func_: Callable[..., Any], 
    value_min: int, 
    value_max:int, 
    value_set:int, 
    height:int, 
    axis:Qt.Orientation,
    use_global_style: bool
) -> QSlider:
    widget = QSlider(axis)
    widget.setMinimum(value_min)
    widget.setMaximum(value_max)
    widget.setMaximumHeight(height)
    widget.setValue(value_set)
    if func_:
        widget.valueChanged.connect(lambda value: func_(value))
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# QPushButton Widget
def makeWidgetButton(
    label: str, 
    func_: Callable[..., Any],
    use_global_style: bool
) -> QPushButton:
    widget = QPushButton(label)
    if func_:
        widget.clicked.connect(func_)
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# QTable Widget
def makeWidgetTable(
    use_global_style: bool
) -> QTableWidget:
    widget = QTableWidget()
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# QTable ListWidget
def makeWidgetListWidget(
    parent: Any, 
    items: List[Any], 
    selection_mode: QAbstractItemView.SelectionMode, 
    editable: bool, 
    drag_drop_mode: QAbstractItemView.DragDropMode,
    use_global_style: bool
) -> QListWidget:
    """
    QListWidgetを作成し、設定する関数

    :param parent: 親ウィジェット
    :param items: リストに追加するアイテムのリスト
    :param selection_mode: 選択モード
    :param editable: アイテムを編集可能にするかどうか
    :param drag_drop_mode: ドラッグ＆ドロップモード
    :param use_global_style: グローバルスタイルを使用するかどうか
    :return: 設定されたQListWidget
    """
    widget = QListWidget(parent)
    
    if items:
        widget.addItems(items)
    
    widget.setSelectionMode(selection_mode)
    
    # 編集可能設定
    if editable:
        widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
    
    # ドラッグ＆ドロップモード設定
    widget.setDragDropMode(drag_drop_mode)
    
    if use_global_style:
        widget.setObjectName('use-global')
    
    return widget

# ComboBox Widget
def makeWidgetComboBox(
    items: List[Any],
    use_global_style: bool
) -> QComboBox:
    widget = QComboBox()
    if items:
        widget.addItems(items)
    if use_global_style:
        widget.setObjectName('use-global')
    return widget

# Figure Widget
def makeWidgetFigure(
) -> Figure:
    widget = Figure()
    return widget

# FiugreCanvasQTAgg Widget
def makeWidgetFigureCanvas(
    figure: Figure,
) -> FigureCanvasQTAgg:
    widget = FigureCanvasQTAgg(figure)
    return widget

# QGraphicsScene Widget
def makeWidgetScene(
) -> QGraphicsScene:
    widget = QGraphicsScene()
    return widget

# QGraphicsView Widget
def makeWidgetView(
    scene: QGraphicsScene, 
    width_min: int, 
    height_min: int, 
    color: str, 
    anti_aliasing: bool, 
    smooth_pixmap_transform: bool,
) -> QGraphicsView:
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
def addWidgetAxisOnFigure(
    figure: Figure, 
    num_row: int, 
    num_col: int, 
    position: int,
) -> Figure:
    figure = figure.add_subplot(num_row, num_col, position)
    return figure



"""
GUI Widget管理用クラス
"""
class WidgetManager:
    def __init__(self):
        self.dict_label       :Dict[str, QLabel] = {}
        self.dict_lineedit    :Dict[str, QLineEdit] = {}
        self.dict_button      :Dict[str, QPushButton] = {} 
        self.dict_ax          :Dict[str, Axes] = {} 
        self.dict_checkbox    :Dict[str, QCheckBox] = {} 
        self.dict_slider      :Dict[str, QSlider] = {}
        self.dict_combobox    :Dict[str, QComboBox] = {} 
        self.dict_listwidget  :Dict[str, QListWidget] = {} 
        self.dict_buttongroup :Dict[str, QButtonGroup] = {}
        self.dict_scene       :Dict[str, QGraphicsScene] = {}
        self.dict_view        :Dict[str, QGraphicsView] = {}
        self.dict_table       :Dict[str, QTableWidget] = {}
        self.dict_figure      :Dict[str, Figure] = {}
        self.dict_canvas      :Dict[str, FigureCanvasQTAgg] = {}

    def makeWidgetLabel(
        self, 
        key: str, 
        label: str, 
        align: Qt.AlignmentFlag = Qt.AlignLeft,
        font_family: str="Arial", 
        font_size: int=12,
        color: str="black",
        bold: bool=False,
        italic: bool=False,
        use_global_style: bool=True
    ) -> QLabel:
        self.dict_label[key] = makeWidgetLabel(label, align, font_family, font_size, color, bold, italic, use_global_style)
        return self.dict_label[key]
    
    def makeWidgetCheckBox(
        self, 
        key: str, 
        label: str, 
        func_: Callable[..., Any] = None, 
        checked: bool = False,
        use_global_style: bool=True
    ) -> QCheckBox:
        self.dict_checkbox[key] = makeWidgetCheckBox(label, func_, checked, use_global_style)
        return self.dict_checkbox[key]
    
    def makeWidgetLineEdit(
        self, 
        key: str, 
        text_set: str = "", 
        width_fix: int = 0,
        use_global_style: bool=True
    ) -> QLineEdit:
        self.dict_lineedit[key] = makeWidgetLineEdit(text_set, width_fix, use_global_style)
        return self.dict_lineedit[key]
    
    def makeWidgetSlider(
        self, 
        key: str, 
        func_: Callable[..., Any] = None, 
        value_min: int = 0, 
        value_max: int = 255, 
        value_set: int = 10, 
        height: int = 10, 
        axis: Qt.Orientation = Qt.Horizontal,
        use_global_style: bool=True
    ) -> QSlider:
        self.dict_slider[key] = makeWidgetSlider(func_, value_min, value_max, value_set, height, axis, use_global_style)
        return self.dict_slider[key]
    
    def makeWidgetButton(
        self, 
        key: str, 
        label: str, 
        func_: Callable[..., Any] = None,
        use_global_style: bool=True
    ) -> QPushButton:
        self.dict_button[key] = makeWidgetButton(label, func_, use_global_style)
        return self.dict_button[key]

    def makeWidgetTable(
        self, 
        key: str,
        use_global_style: bool=True
    ) -> QTableWidget:
        self.dict_table[key] = makeWidgetTable(use_global_style)
        return self.dict_table[key]
    
    def makeWidgetListWidget(
        self, 
        key: str, 
        parent: Any=None, 
        items: List[Any]=None, 
        selection_mode: QAbstractItemView.SelectionMode=QListWidget.SingleSelection, 
        editable: bool=False, 
        drag_drop_mode: QAbstractItemView.DragDropMode=QListWidget.NoDragDrop,
        use_global_style: bool=True
    ) -> QListWidget:
        self.dict_listwidget[key] = makeWidgetListWidget(parent, items, selection_mode, editable, drag_drop_mode, use_global_style)
        return self.dict_listwidget[key]
    
    def makeWidgetComboBox(
        self, 
        key: str, 
        items: List[Any]=None,
        use_global_style: bool=True
    ) -> QComboBox:
        self.dict_combobox[key] = makeWidgetComboBox(items, use_global_style)
        return self.dict_combobox[key]

    def makeWidgetFigure(
        self, 
        key: str,
    ) -> Figure:
        self.dict_figure[key] = makeWidgetFigure()
        return self.dict_figure[key]

    def makeWidgetFigureCanvas(
        self, 
        key: str, 
        figure: Figure,
    ) -> FigureCanvasQTAgg:
        self.dict_canvas[key] = makeWidgetFigureCanvas(figure)
        return self.dict_canvas[key]

    def makeWidgetScene(
        self, 
        key: str,
    ) -> QGraphicsScene:
        self.dict_scene[key] = makeWidgetScene()
        return self.dict_scene[key]

    def makeWidgetView(
        self, 
        key: str, 
        width_min: int=0, 
        height_min: int=0, 
        color: str="black", 
        anti_aliasing: bool=True, 
        smooth_pixmap_transform: bool=True,
    ) -> QGraphicsView:
        scene = self.makeWidgetScene(key)
        self.dict_view[key] = makeWidgetView(scene, width_min, height_min, color, anti_aliasing, smooth_pixmap_transform)
        return self.dict_view[key]

    def addWidgetAxisOnFigure(
        self, 
        key: str, 
        figure: Figure, 
        num_row: int, 
        num_col: int, 
        position: int,
        use_global_style: bool=True
    ) -> Axes:
        self.dict_ax[key] = addWidgetAxisOnFigure(figure, num_row, num_col, position, use_global_style)
        return self.dict_ax[key]