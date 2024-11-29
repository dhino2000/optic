from __future__ import annotations
from ..type_definitions import *
import os
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QMessageBox
from ..config.constants import FILE_FILTERS

# 開くファイルのファイルパスを返す
def openFileDialog(
        q_widget    : QWidget, 
        file_type   : str, 
        title       : str="Open File", 
        initial_dir : str="", 
        multiple    : bool=False
        ) -> Union[str, List[str]]: 
    """
    :file_type: ".mat", ".tif", ".npy", ".h5"
    """
    options = QFileDialog.Options()
    file_filter = FILE_FILTERS.get(file_type, "All Files (*)")

    # 複数ファイルを選択するか
    if multiple:
        files, _ = QFileDialog.getOpenFileNames(q_widget, title, initial_dir, file_filter, options=options)
        return files
    else:
        file_path, _ = QFileDialog.getOpenFileName(q_widget, title, initial_dir, file_filter, options=options)
        return file_path

# return flie save path and bool value of overwriting
def saveFileDialog(
        q_widget            : QWidget, 
        file_type           : str, 
        title               : str="Save File", 
        initial_dir         : str=""
        ) -> Tuple[Optional[str], bool]:
    options = QFileDialog.Options()
    file_filter = FILE_FILTERS.get(file_type, "All Files (*)")
    while True:
        file_path, _ = QFileDialog.getSaveFileName(q_widget, title, initial_dir, file_filter, options=options)
        if not file_path:
            return None, False
        
        if os.path.exists(file_path):
            reply = QMessageBox.question(q_widget, 'File overwrite',
                                         "The file already exists. Do you want to overwrite it?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                return file_path, True  
        else:
            return file_path, False
def openFolderDialog(
        q_widget                : QWidget, 
        title                   : str="Select Folder", 
        initial_dir             : str=""
        ) -> str:
    options = QFileDialog.Options()
    folder_path = QFileDialog.getExistingDirectory(q_widget, title, initial_dir, options=options)
    return folder_path

# 選択したファイルのパスをQLineEditに表示
def openFileDialogAndSetLineEdit(
        q_widget            : QWidget, 
        file_type           : str, 
        line_edit           : QLineEdit, 
        title               : str="Open File", 
        initial_dir         : str=""
        ) -> None:
    if not isinstance(line_edit, QLineEdit):
        raise TypeError("line_edit must be an instance of QLineEdit")

    file_path = openFileDialog(q_widget, file_type, title, initial_dir)
    if file_path:
        line_edit.setText(file_path)