from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

def setAppStyle(app: QApplication, font_name: str = "MS UI Gothic", font_size: int = 9, widget_height: int = 25, widget_margin: int = 2):
    """
    アプリケーション全体のスタイルを設定する。

    :param app: QApplicationインスタンス
    :param font_name: フォント名（デフォルトは "MS UI Gothic"）
    :param font_size: フォントサイズ（デフォルトは 9）
    :param widget_height: ウィジェットの高さ（デフォルトは 25）
    :param widget_margin: ウィジェットの余白（デフォルトは 2）
    """
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