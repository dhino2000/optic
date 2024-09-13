from PyQt5.QtWidgets import QLayout

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