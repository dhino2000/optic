from __future__ import annotations
from ..type_definitions import *
import os
from PyQt5.QtWidgets import QWidget, QLineEdit, QFileDialog, QMessageBox

def openFileDialog(
        q_widget    : QWidget, 
        file_type   : Union[str, List[str]], 
        title       : str="Open File", 
        initial_dir : str="", 
        multiple    : bool=False
        ) -> Union[str, List[str]]:
    """
    Open file dialog and return selected file path(s).
    
    Args:
        q_widget (QWidget): Parent widget
        file_type (Union[str, List[str]]): File extension(s) - e.g., ".mat", ".tif", ".npy", ".h5" 
                                           or list of extensions [".mat", ".h5"]
        title (str): Dialog window title
        initial_dir (str): Initial directory path
        multiple (bool): If True, allows multiple file selection
        
    Returns:
        Union[str, List[str]]: Selected file path(s)
    """
    from ..config.constants import FILE_FILTERS
    options = QFileDialog.Options()
    
    # Handle single or multiple file types
    if isinstance(file_type, list):
        # Combine multiple file filters
        filter_list = [FILE_FILTERS.get(ft, f"*{ft}") for ft in file_type]
        file_filter = ";;".join(filter_list) + ";;All Files (*)"
    else:
        file_filter = FILE_FILTERS.get(file_type, "All Files (*)")
    
    # Select single or multiple files
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
    from ..config.constants import FILE_FILTERS
    options = QFileDialog.Options()
    file_filter = FILE_FILTERS.get(file_type, "All Files (*)")
    while True:
        file_path, _ = QFileDialog.getSaveFileName(q_widget, title, initial_dir, file_filter, options=options)
        if not file_path:
            return None, False
        
        if os.path.exists(file_path):
            reply = QMessageBox.question(q_widget, 'File overwrite',
                                         "The file already exists. Do you want to overwrite it?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
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
        file_type           : Union[str, List[str]], 
        line_edit           : QLineEdit, 
        title               : str="Open File", 
        initial_dir         : str=""
        ) -> None:
    if not isinstance(line_edit, QLineEdit):
        raise TypeError("line_edit must be an instance of QLineEdit")

    file_path = openFileDialog(q_widget, file_type, title, initial_dir)
    if file_path:
        line_edit.setText(file_path)