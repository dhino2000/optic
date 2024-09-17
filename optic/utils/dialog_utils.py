from PyQt5.QtWidgets import QMessageBox

def showConfirmationDialog(parent, title, message, default_button=QMessageBox.No):
    """
    確認ダイアログを表示する汎用関数

    Args:
    parent: 親ウィジェット
    title: ダイアログのタイトル
    message: 表示するメッセージ
    default_button: デフォルトで選択されるボタン

    Returns:
    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel のいずれか
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
    msg_box.setDefaultButton(default_button)
    
    return msg_box.exec_()