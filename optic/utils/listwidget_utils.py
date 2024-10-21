from PyQt5.QtWidgets import QListWidget, QLineEdit

def addItemToListWidgetFromLineEdit(list_widget: QListWidget, line_edit: QLineEdit, dupilcate: bool=False) -> None:
    """
    add item to ListWidget from LineEdit
    """
    text = line_edit.text().strip()
    if text:
        if not dupilcate:
            items = [list_widget.item(i).text() for i in range(list_widget.count())]
            if text in items:
                return False
        list_widget.addItem(text)
        return True
    return False

def removeSelectedItemFromListWidget(list_widget: QListWidget) -> None:
    """
    remove selected item from ListWidget
    """
    current_item = list_widget.currentItem()
    if current_item:
        row = list_widget.row(current_item)
        list_widget.takeItem(row)

def clearListWidget(list_widget: QListWidget) -> None:
    """
    clear all items from ListWidget
    """
    list_widget.clear()