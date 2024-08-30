# Widgetのデフォルトのキーイベントを無効化するフィルター
from PyQt5.QtWidgets import QRadioButton
from types import MethodType

def keyPressEventIgnore(self, event):
    if event.type() == event.KeyPress:
        event.ignore()
    else:
        super(type(self), self).keyPressEvent(event)

def applyKeyPressEventIgnore(widget):
    if isinstance(widget, QRadioButton):
        widget.keyPressEvent = MethodType(keyPressEventIgnore, widget)

    return widget
