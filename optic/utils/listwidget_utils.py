from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QListWidget, QLineEdit, QListWidgetItem
from PyQt5.QtCore import Qt

def addItemToListWidget(list_widget: QListWidget, item: str, duplicate: bool=False, editable: bool=False) -> None:
    """
    add item to ListWidget
    """
    if item:
        if not duplicate:
            items = [list_widget.item(i).text() for i in range(list_widget.count())]
            if item in items:
                return
                
        new_item = QListWidgetItem(item)
        if editable:
            new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)
        list_widget.addItem(new_item)

def addItemToListWidgetFromLineEdit(list_widget: QListWidget, line_edit: QLineEdit, duplicate: bool=False) -> None:
    """
    add item to ListWidget from LineEdit
    """
    text = line_edit.text().strip()
    if text:
        if not duplicate:
            items = [list_widget.item(i).text() for i in range(list_widget.count())]
            if text in items:
                return False
        list_widget.addItem(text)
        return True
    return False

def getSelectedItemsFromListWidget(list_widget: QListWidget) -> str:
    """
    get selected item from ListWidget
    """
    current_item = list_widget.currentItem()
    if current_item:
        return current_item.text()
    return ""

def getIndexedItemsFromListWidget(list_widget: QListWidget, idx: int) -> int:
    """
    get indexed item from ListWidget
    """
    return list_widget.item(idx).text()

def getAllItemsFromListWidget(list_widget: QListWidget) -> List[str]:
    """
    get all items from ListWidget
    """
    return [list_widget.item(i).text() for i in range(list_widget.count())]

def removeSelectedItemsFromListWidget(list_widget: QListWidget) -> None:
    """
    remove selected item from ListWidget
    """
    for item in reversed(list_widget.selectedItems()):
        list_widget.takeItem(list_widget.row(item))

def removeIndexedItemsFromListWidget(list_widget: QListWidget, idx: int) -> None:
    """
    remove indexed item from ListWidget
    """
    list_widget.takeItem(idx)

def clearListWidget(list_widget: QListWidget) -> None:
    """
    clear all items from ListWidget
    """
    list_widget.clear()