from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtGui import QFont

def setAppStyle(app: QApplication, font_name: str = "MS UI Gothic", base_font_size: int = 12, base_widget_height: int = 20, base_widget_margin: int = 2):
    """
    アプリケーション全体のスタイルを設定する。

    :param app: QApplicationインスタンス
    :param font_name: フォント名（デフォルトは "MS UI Gothic"）
    :param base_font_size: 基本のフォントサイズ
    :param base_widget_height: 基本のウィジェットの高さ
    :param base_widget_margin: 基本のウィジェットの余白
    """
    scaling_factor = getScalingFactor()
    
    font_size = int(base_font_size * scaling_factor)
    widget_height = int(base_widget_height * scaling_factor)
    widget_margin = int(base_widget_margin * scaling_factor)

    # フォントの設定
    font = QFont(font_name, font_size)
    app.setFont(font)

    # スタイルシートの設定
    app.setStyleSheet(f"""
        QWidget {{
            font-size: {font_size}px;
        }}
        QLineEdit, QPushButton, QComboBox {{
            min-height: {widget_height}px;
            max-height: {widget_height}px;
            padding: 0px {widget_margin}px;
        }}
        QTableView {{
            gridline-color: #d0d0d0;
        }}
        QHeaderView::section {{
            background-color: #f0f0f0;
            padding: 4px;
            border: 1px solid #d0d0d0;
            font-weight: bold;
        }}
    """)

def applyAppStyle(app: QApplication):
    """
    アプリケーションにデフォルトのスタイルを適用する。
    """
    setAppStyle(app)

def getScalingFactor():
    """
    ディスプレイの横幅に基づいてスケーリングファクターを計算する。
    """
    screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
    width = QDesktopWidget().screenGeometry(screen).width()
    
    if width < 2400:
        return 1
    elif width < 2880:
        return 1.25
    elif width < 3360:
        return 1.5
    elif width < 3840:
        return 1.75
    else:
        return 2