# データの読み込み、書き込み用関数
from PyQt5.QtWidgets import QFileDialog, QLineEdit

FILE_FILTERS = {
    "mat": "mat Files (*.mat);;All Files (*)",
    "tiff": "tiff Files (*.tif *.tiff);;All Files (*)",
    "npy": "npy Files (*.npy);;All Files (*)"
}

# 開くファイルのファイルパスを返す
def openFileDialog(q_widget, file_type, title="Open File", initial_dir="", multiple=False):
    options = QFileDialog.Options()
    file_filter = FILE_FILTERS.get(file_type, "All Files (*)")

    # 複数ファイルを選択するか
    if multiple:
        files, _ = QFileDialog.getOpenFileNames(q_widget, title, initial_dir, file_filter, options=options)
        return files
    else:
        file_path, _ = QFileDialog.getOpenFileName(q_widget, title, initial_dir, file_filter, options=options)
        return file_path

# 保存するファイルのファイルパスを返す
def saveFileDialog(q_widget, file_type, title="Save File", initial_dir=""):
    options = QFileDialog.Options()
    file_filter = FILE_FILTERS.get(file_type, "All Files (*)")
    file_path, _ = QFileDialog.getSaveFileName(q_widget, title, initial_dir, file_filter, options=options)
    return file_path

# 選択したファイルのパスをQLineEditに表示
def openFileDialogAndSetLineEdit(q_widget, file_type, line_edit, title="Open File", initial_dir=""):
    if not isinstance(line_edit, QLineEdit):
        raise TypeError("line_edit must be an instance of QLineEdit")

    file_path = openFileDialog(q_widget, file_type, title, initial_dir)
    if file_path:
        line_edit.setText(file_path)