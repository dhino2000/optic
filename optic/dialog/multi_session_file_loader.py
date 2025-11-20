from __future__ import annotations
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from ..manager import WidgetManager, initManagers
from ..config.constants import Extension
from ..gui.io_layouts import makeLayoutLoadFileWidget
from ..gui.bind_func import bindFuncLoadFileWidget
from ..utils.layout_utils import clearLayout
import os

class MultiSessionFileLoaderDialog(QDialog):
    def __init__(self, parent: QWidget, gui_defaults: dict, require_roi_curation: bool = False):
        """
        Parameters:
        -----------
        parent : QWidget
            Parent widget
        gui_defaults : dict
            GUI default settings
        require_roi_curation : bool
            If True, ROICuration.mat files are required and must match Fall.mat files count
        """
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        
        # Flag to check if ROICuration files are required
        self.require_roi_curation = require_roi_curation
        
        # Lists to store file paths
        self.list_path_fall = []
        self.list_path_roi_curation = []
        
        # Row counters
        self.row_count_fall = 1
        self.row_count_roi_curation = 1
        
        # Layout references
        self.layout_fall_section = None
        self.layout_roi_curation_section = None
        
        # Window settings
        window_settings = gui_defaults.get("WINDOW_SETTINGS_DIALOG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Multi-Session File Loader')
        
        layout_main = QVBoxLayout()
        
        # Upper section: Fall.mat and ROICuration.mat sections
        layout_upper = QHBoxLayout()
        
        # Left: Fall.mat section
        self.layout_fall_section = self.makeLayoutMultiSessionSection(
            label_text="Fall.mat file path",
            key_prefix="path_fall",
            initial_count=1
        )
        layout_upper.addLayout(self.layout_fall_section)
        
        # Right: ROICuration.mat section
        roi_label = "ROICuration.mat file path"
        if self.require_roi_curation:
            roi_label += " (Required)"
        else:
            roi_label += " (Optional)"
        
        self.layout_roi_curation_section = self.makeLayoutMultiSessionSection(
            label_text=roi_label,
            key_prefix="path_roi_curation",
            initial_count=1
        )
        layout_upper.addLayout(self.layout_roi_curation_section)
        
        layout_main.addLayout(layout_upper)
        
        # Bottom section: Load Files / Cancel buttons
        layout_main.addLayout(self.makeLayoutDialogButtons())
        
        self.setLayout(layout_main)
        
        self.bindFuncAllWidget()
    
    """
    makeLayout Functions
    """
    def makeLayoutMultiSessionSection(self, label_text: str, key_prefix: str, initial_count: int = 1):
        """
        Create a section for loading multiple files
        
        Parameters:
        -----------
        label_text : str
            Base text for labels (e.g., "Fall.mat file path")
        key_prefix : str
            Prefix for widget management keys (e.g., "path_fall")
        initial_count : int
            Number of rows to display initially
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout_section = QVBoxLayout()
        
        # Section title
        section_title = label_text.split(" file path")[0] + " Files"
        layout_section.addWidget(
            self.widget_manager.makeWidgetLabel(
                key=f"{key_prefix}_section_title",
                label=f"【{section_title}】"
            )
        )
        
        # Add initial rows
        for i in range(initial_count):
            row_index = i + 1 
            layout_row = makeLayoutLoadFileWidget(
                self.widget_manager,
                label=f"{label_text} {row_index}:",
                key_label=f"{key_prefix}_{row_index}",
                key_lineedit=f"{key_prefix}_{row_index}",
                key_button=f"{key_prefix}_{row_index}",
            )
            layout_section.addLayout(layout_row)
        
        # Add / Delete buttons
        layout_buttons = QHBoxLayout()
        button_add = self.widget_manager.makeWidgetButton(
            key=f"add_{key_prefix}",
            label="Add"
        )
        button_delete = self.widget_manager.makeWidgetButton(
            key=f"delete_{key_prefix}",
            label="Delete"
        )
        layout_buttons.addWidget(button_add)
        layout_buttons.addWidget(button_delete)
        layout_buttons.addStretch()
        
        layout_section.addLayout(layout_buttons)
        layout_section.addStretch()
        
        return layout_section

    def makeLayoutDialogButtons(self):
        """
        Create button layout for the bottom of the dialog
        
        Returns:
        --------
        layout : QHBoxLayout
        """
        layout_buttons = QHBoxLayout()
        layout_buttons.addStretch()
        
        button_load = self.widget_manager.makeWidgetButton(
            key="load_files",
            label="Load Files"
        )
        button_cancel = self.widget_manager.makeWidgetButton(
            key="cancel",
            label="Cancel"
        )
        
        layout_buttons.addWidget(button_load)
        layout_buttons.addWidget(button_cancel)
        
        return layout_buttons
    
    """
    File path row manipulation functions
    """
    def addFilePathRow(self, key_prefix: str, label_base_text: str, layout_target: QVBoxLayout):
        """
        Add a new file path input row
        
        Parameters:
        -----------
        key_prefix : str
            "path_fall" or "path_roi_curation"
        label_base_text : str
            Base text for label
        layout_target : QVBoxLayout
            Target layout to add the row to
        """
        # Update counter
        if key_prefix == "path_fall":
            self.row_count_fall += 1
            row_index = self.row_count_fall
        else:  # path_roi_curation
            self.row_count_roi_curation += 1
            row_index = self.row_count_roi_curation
        
        # Create new row
        layout_row = makeLayoutLoadFileWidget(
            self.widget_manager,
            label=f"{label_base_text} {row_index}:",
            key_label=f"{key_prefix}_{row_index}",
            key_lineedit=f"{key_prefix}_{row_index}",
            key_button=f"{key_prefix}_{row_index}",
        )
        
        # Insert before Add/Delete buttons (count - 2: skip buttons layout and stretch)
        insert_position = layout_target.count() - 2
        layout_target.insertLayout(insert_position, layout_row)
        
        # Bind function to the newly added Browse button
        key = f"{key_prefix}_{row_index}"
        self.bindFuncBrowseButton(key, key_prefix)
    
    def deleteFilePathRow(self, key_prefix: str, layout_target: QVBoxLayout):
        """
        Delete the last file path input row
        
        Parameters:
        -----------
        key_prefix : str
            "path_fall" or "path_roi_curation"
        layout_target : QVBoxLayout
            Target layout to remove the row from
        """
        # Keep at least 1 row
        if key_prefix == "path_fall":
            if self.row_count_fall <= 1:
                return
            row_index = self.row_count_fall
            self.row_count_fall -= 1
        else:  # path_roi_curation
            if self.row_count_roi_curation <= 1:
                return
            row_index = self.row_count_roi_curation
            self.row_count_roi_curation -= 1
        
        # Get the layout to remove (2 positions before the end: before buttons and stretch)
        remove_position = layout_target.count() - 3
        layout_to_remove = layout_target.itemAt(remove_position)
        
        # Clear and remove layout
        if layout_to_remove and layout_to_remove.layout():
            clearLayout(layout_to_remove.layout())
            layout_target.removeItem(layout_to_remove)
        
        # Remove widgets from widget_manager
        key = f"{key_prefix}_{row_index}"
        if key in self.widget_manager.dict_label:
            del self.widget_manager.dict_label[key]
        if key in self.widget_manager.dict_lineedit:
            del self.widget_manager.dict_lineedit[key]
        if key in self.widget_manager.dict_button:
            del self.widget_manager.dict_button[key]
    
    """
    Data retrieval and validation functions
    """
    def getFilePaths(self):
        """
        Get all input file paths
        
        Returns:
        --------
        dict : {
            'list_path_fall': [path1, path2, ...],
            'list_path_roi_curation': [path1, path2, ...]
        }
        """
        self.list_path_fall = []
        self.list_path_roi_curation = []
        
        # Get Fall.mat paths
        for i in range(1, self.row_count_fall + 1):
            key = f"path_fall_{i}"
            if key in self.widget_manager.dict_lineedit:
                path = self.widget_manager.dict_lineedit[key].text().strip()
                if path:
                    self.list_path_fall.append(path)
        
        # Get ROICuration.mat paths
        for i in range(1, self.row_count_roi_curation + 1):
            key = f"path_roi_curation_{i}"
            if key in self.widget_manager.dict_lineedit:
                path = self.widget_manager.dict_lineedit[key].text().strip()
                if path:
                    self.list_path_roi_curation.append(path)
        
        return {
            'list_path_fall': self.list_path_fall,
            'list_path_roi_curation': self.list_path_roi_curation
        }
    
    def validateFilePaths(self):
        """
        Validate file paths
        - Check if at least one Fall.mat file is provided
        - Check if Fall.mat and ROICuration.mat counts match (if required)
        - Check if files exist
        - Check if extensions are correct
        
        Returns:
        --------
        is_valid : bool
        error_messages : list[str]
        """
        file_paths = self.getFilePaths()
        error_messages = []
        
        # Check if at least one Fall.mat file is provided
        if not file_paths['list_path_fall']:
            error_messages.append("At least one Fall.mat file must be provided.")
        
        # Check if counts match (only if ROICuration is required)
        if self.require_roi_curation:
            if len(file_paths['list_path_fall']) != len(file_paths['list_path_roi_curation']):
                error_messages.append(
                    f"Number of Fall.mat files ({len(file_paths['list_path_fall'])}) "
                    f"and ROICuration.mat files ({len(file_paths['list_path_roi_curation'])}) must match."
                )
            
            # Check if all ROICuration files are provided
            if len(file_paths['list_path_roi_curation']) < len(file_paths['list_path_fall']):
                error_messages.append("All Fall.mat files must have corresponding ROICuration.mat files.")
        
        # Check Fall.mat files
        for i, path in enumerate(file_paths['list_path_fall'], 1):
            if not os.path.exists(path):
                error_messages.append(f"Fall.mat file {i} does not exist: {path}")
            elif not path.endswith(Extension.MAT):
                error_messages.append(f"Fall.mat file {i} has incorrect extension: {path}")
        
        # Check ROICuration.mat files (only check provided files)
        for i, path in enumerate(file_paths['list_path_roi_curation'], 1):
            if path:  # Only check if path is provided
                if not os.path.exists(path):
                    error_messages.append(f"ROICuration.mat file {i} does not exist: {path}")
                elif not path.endswith(Extension.MAT):
                    error_messages.append(f"ROICuration.mat file {i} has incorrect extension: {path}")
        
        is_valid = len(error_messages) == 0
        return is_valid, error_messages
    
    def loadFiles(self):
        """
        Validate and load files when Load Files button is clicked
        """
        is_valid, error_messages = self.validateFilePaths()
        
        if not is_valid:
            error_text = "\n".join(error_messages)
            QMessageBox.warning(self, "Validation Error", f"File validation failed:\n\n{error_text}")
            return
        
        # If validation passed, accept the dialog
        self.accept()
    
    """
    Bind functions
    """
    def bindFuncBrowseButton(self, key: str, key_prefix: str):
        """
        Bind file browser function to a Browse button
        
        Parameters:
        -----------
        key : str
            Widget key (e.g., "path_fall_1")
        key_prefix : str
            "path_fall" or "path_roi_curation"
        """
        bindFuncLoadFileWidget(
            q_widget=self,
            q_button=self.widget_manager.dict_button[key],
            q_lineedit=self.widget_manager.dict_lineedit[key],
            filetype=[Extension.MAT]
        )
    
    def bindFuncAllWidget(self):
        """
        Bind all widget functions
        """
        # Bind initial Browse buttons
        for i in range(1, self.row_count_fall + 1):
            key = f"path_fall_{i}"
            self.bindFuncBrowseButton(key, "path_fall")
        
        for i in range(1, self.row_count_roi_curation + 1):
            key = f"path_roi_curation_{i}"
            self.bindFuncBrowseButton(key, "path_roi_curation")
        
        # Bind Add/Delete buttons for Fall.mat
        self.widget_manager.dict_button["add_path_fall"].clicked.connect(
            lambda: self.addFilePathRow("path_fall", "Fall.mat file path", self.layout_fall_section)
        )
        self.widget_manager.dict_button["delete_path_fall"].clicked.connect(
            lambda: self.deleteFilePathRow("path_fall", self.layout_fall_section)
        )
        
        # Bind Add/Delete buttons for ROICuration.mat
        roi_label = "ROICuration.mat file path"
        if self.require_roi_curation:
            roi_label += " (Required)"
        else:
            roi_label += " (Optional)"
        
        self.widget_manager.dict_button["add_path_roi_curation"].clicked.connect(
            lambda: self.addFilePathRow("path_roi_curation", roi_label, self.layout_roi_curation_section)
        )
        self.widget_manager.dict_button["delete_path_roi_curation"].clicked.connect(
            lambda: self.deleteFilePathRow("path_roi_curation", self.layout_roi_curation_section)
        )
        
        # Bind dialog buttons
        self.widget_manager.dict_button["load_files"].clicked.connect(self.loadFiles)
        self.widget_manager.dict_button["cancel"].clicked.connect(self.reject)