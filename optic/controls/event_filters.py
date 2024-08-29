# Widgetのデフォルトのキーイベントを無効化するフィルター
from PyQt5.QtCore import QObject, QEvent

class RadioButtonEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            # 左右キーのイベントを無視
            if event.key() in [Qt.Key_Left, Qt.Key_Right]:
                return True
        return super().eventFilter(obj, event)