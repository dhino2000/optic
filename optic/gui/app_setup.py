# アプリsetup 
from PyQt5.QtWidgets import QLayout, QWidget

def clearLayout(layout: QLayout):
    """
    Recursively removes all widgets and sub-layouts within the specified layout.

    Args:
        layout (QLayout): The layout to clear.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                clearLayout(item.layout())

def setupMainWindow(q_window, gui_defaults):
    q_window.setWindowTitle(gui_defaults["TITLE"])
    q_window.setGeometry(gui_defaults["INIT_POSITION_X"], gui_defaults["INIT_POSITION_Y"], gui_defaults["WIDTH"], gui_defaults["HEIGHT"])