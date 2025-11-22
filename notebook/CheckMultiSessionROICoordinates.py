import sys
import os

dir_notebook = os.path.dirname(os.path.abspath("__file__"))
dir_parent = os.path.dirname(dir_notebook)
if not dir_parent in sys.path:
    sys.path.append(dir_parent)

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QApplication, QDialog, QComboBox, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QRectF
import shutil
from copy import deepcopy
import numpy as np
from optic.gui.app_setup import setupMainWindow
from optic.gui.app_style import applyAppStyle
from optic.gui.base_layouts import makeLayoutComboBoxLabel, makeLayoutButtonGroup
from optic.gui.io_layouts import makeLayoutLoadFileExitHelp
from optic.gui.processing_image_layouts import makeLayoutMicrogliaXYCTStackRegistration
from optic.dialog.elastix_params_config import ElastixParamsConfigDialog
from optic.dialog.multi_session_file_loader import MultiSessionFileLoaderDialog
from optic.controls.view_control import ViewControl
from optic.manager import WidgetManager, ConfigManager, DataManager, ControlManager, LayoutManager, initManagers
from optic.utils.view_utils import generateSessionColors
from optic.gui.bind_func import bindFuncExit

class CheckMultiSessionROICoordinatesGUI(QMainWindow):
    def __init__(self):
        APP_NAME = "CHECK_MULTI_SESSION_ROI_COORDINATES"
        QMainWindow.__init__(self)
        
        # Initialize managers
        self.widget_manager, self.config_manager, self.data_manager, self.control_manager, self.layout_manager = initManagers(
            WidgetManager(), ConfigManager(), DataManager(), ControlManager(), LayoutManager()
        )
        self.config_manager.setCurrentApp(APP_NAME)
        self.app_keys = self.config_manager.gui_defaults["APP_KEYS"]
        self.app_key_pri = self.app_keys[0]
        
        # Setup main window
        setupMainWindow(self, self.config_manager.gui_defaults)
        
        # Flag to track if setup is complete
        self.setup_complete = False
        
        # File paths lists
        self.list_path_fall = []
        self.list_path_roi_curation = []
        
        # Show file loader dialog first
        self.showFileLoaderDialog()
    
    def initUI(self):
        """
        Initialize main UI after files are loaded
        """
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout_main = QVBoxLayout(self.central_widget)
        
        # Main UI layout (Grid)
        self.layout_main_ui = QGridLayout()
        self.layout_main.addLayout(self.layout_main_ui)
        
        # Setup layouts
        self.setupMainUILayouts()

        # Setup controls
        self.setupControls()

        # Bind functions to widgets
        self.bindFuncAllWidget()

        # update view
        self.updateView_CheckMultiSessionROICoordinates()
    
    def setupMainUILayouts(self):
        """
        Setup main UI layouts
        """
        self.layout_main_ui.addLayout(self.makeLayoutSectionLeftUpper(), 0, 0)
        self.layout_main_ui.addLayout(self.makeLayoutSectionRightUpper(), 0, 1)
        self.layout_main_ui.addLayout(self.makeLayoutSectionBottom(), 1, 0, 1, 2)

    def setupControls(self):
        self.control_manager.view_controls[self.app_key_pri] = ViewControl(
            app_key=self.app_key_pri,
            q_view=self.widget_manager.dict_view[self.app_key_pri], 
            q_scene=self.widget_manager.dict_scene[self.app_key_pri], 
            data_manager=self.data_manager, 
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
        )
        self.control_manager.view_controls[self.app_key_pri].setViewSize()
        
    """
    makeLayout Functions: Component Level
    """
    
    def makeLayoutComponentROIView(self):
        """
        ROI view component with QGraphicsView
        Similar to Suite2pROICurationGUI's ROI view
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout = QVBoxLayout()
        
        # Create QGraphicsView and QGraphicsScene
        view = self.widget_manager.makeWidgetView(key=self.app_key_pri)
        scene = self.widget_manager.makeWidgetScene(key=self.app_key_pri)
        view.setScene(scene)
        
        layout.addWidget(view)
        return layout
    
    def makeLayoutComponentSessionDisplaySettings(self):
        """
        Session-wise cell type display checkboxes
        
        Structure for each session:
          Session N
            ☑ Neuron  ☑ Glia  ☐ Neuropil  ...
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout = QVBoxLayout()
        
        # Title label
        layout.addWidget(self.widget_manager.makeWidgetLabel(
            key="session_display_title",
            label="Session Display Settings"
        ))
        
        # Scroll area for sessions
        scroll_area = self.widget_manager.makeWidgetScrollArea(
            key="session_display_scroll"
        )
        widget_scroll = QWidget()
        layout_scroll = QVBoxLayout(widget_scroll)
        
        # Create checkboxes for each session
        num_sessions = len(self.list_path_fall)
        for i in range(num_sessions):
            session_key = f"session_{i}"
            
            # Session label
            layout_scroll.addWidget(self.widget_manager.makeWidgetLabel(
                key=f"{session_key}_label",
                label=f"Session {i}",
                bold=True
            ))
            
            # Cell type checkboxes (horizontal layout)
            layout_celltype = QHBoxLayout()
            
            key_checkbox = ["bg"]
            # Get cell types from dict_roi_celltype
            key_checkbox.extend(self.data_manager.dict_roi_celltype[session_key].keys())
            
            for celltype in key_checkbox:
                checkbox = self.widget_manager.makeWidgetCheckBox(
                    key=f"{session_key}_display_{celltype}",
                    label=celltype,
                    checked=True
                )
                layout_celltype.addWidget(checkbox)
            
            layout_scroll.addLayout(layout_celltype)
        
        layout_scroll.addStretch()
        scroll_area.setWidget(widget_scroll)
        layout.addWidget(scroll_area)
        
        return layout
    
    def makeLayoutComponentRegistration(self):
        """
        Image registration controls
        
        Components:
          - Reference session selector (ComboBox)
          - Background image type selector (ButtonGroup)
          - Register button
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout = QVBoxLayout()
        
        # Background image type selector (use base_layout)
        layout.addWidget(self.widget_manager.makeWidgetLabel(
            key="registration_bg_label",
            label="Background Image Type:"
        ))
        
        bg_types = ["meanImg", "meanImgE", "max_proj", "Vcorr"]
        widget_bg_type = makeLayoutButtonGroup(
            q_widget=self,
            widget_manager=self.widget_manager,
            key_buttongroup="im_bg_type",
            list_label_buttongroup=bg_types,
            axis="horizontal",
            set_exclusive=True,
            idx_check=0,  # Default: meanImg
            is_scroll=False
        )
        layout.addLayout(widget_bg_type)
        
        layout.addLayout(makeLayoutMicrogliaXYCTStackRegistration(
            self.widget_manager,
            1, # n_channels fixed
            len(self.data_manager.session_keys), # n_sessions     
            f"elastix_registration",
            f"elastix_ref_c",
            f"elastix_ref_plane_t",
            f"opacity_roi_pair",
            f"elastix_method",
            f"elastix_ref_c",
            f"elastix_ref_plane_t",          
            f"elastix_config", 
            f"elastix_run_t",   
            f"export_reg_tiff",
            f"show_roi_match",
            f"show_roi_pair",
            f"show_reg_im_bg",
            f"show_reg_im_roi",
            f"opacity_roi_pair",
        ))
        
        layout.addStretch()
        
        return layout
    
    """
    makeLayout Functions: Section Level
    """
    
    def makeLayoutSectionLeftUpper(self):
        """
        Left upper section: ROI view
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentROIView())
        return layout
    
    def makeLayoutSectionRightUpper(self):
        """
        Right upper section: Display settings and registration
        
        Returns:
        --------
        layout : QVBoxLayout
        """
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentSessionDisplaySettings())
        layout.addLayout(self.makeLayoutComponentRegistration())
        return layout
    
    def makeLayoutSectionBottom(self):
        """
        Bottom section: Control buttons (Load File, Help, Exit)
        Uses makeLayoutLoadFileExitHelp from optic.gui.io_layouts
        
        Returns:
        --------
        layout : QHBoxLayout
        """
        layout = makeLayoutLoadFileExitHelp(self.widget_manager)
        return layout
    
    """
    make SubWindow, Dialog Function
    """
    def showFileLoaderDialog(self):
        """
        Show multi-session file loader dialog
        ROICuration.mat files are REQUIRED for this application
        """
        dialog = MultiSessionFileLoaderDialog(
            self, 
            self.config_manager.gui_defaults,
            require_roi_curation=True
        )
        
        if dialog.exec_():
            # Dialog accepted - get file paths
            file_paths = dialog.getFilePaths()
            self.list_path_fall = file_paths['list_path_fall']
            self.list_path_roi_curation = file_paths['list_path_roi_curation']
            
            # Load data and initialize UI
            success = self.loadMultiSessionData()
            if success:
                self.initUI()
                self.setup_complete = True
                QMessageBox.information(self, "Success", "Files loaded successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to load files.")
                self.close()

    # Elastix Params Config Dialog
    def showSubWindowElastixParamsConfig(self):
        config_window = ElastixParamsConfigDialog(
            self, 
            self.config_manager.json_config.get("elastix_params"),
            self.config_manager.gui_defaults,
        )
        if config_window.exec_() == QDialog.Accepted:
            self.config_manager.json_config.set("elastix_params", config_window.elastix_params)


    """
    Function for bindFunc
    """
    def loadROICurationMat(self, app_key: str, path_roi_curation: str):
        from scipy.io import loadmat
        import numpy as np
        mat_roicheck = loadmat(path_roi_curation, simplify_cells=True)
        date = list(mat_roicheck["manualROIcheck"].keys())[-1] # get last date as default
        # select saved date
        dict_roicheck = mat_roicheck["manualROIcheck"][date]
        dict_roicheck = {k.replace(" ", "_"): v for k, v in dict_roicheck.items()} # this is temporary fix for old ROIcheck files !!!
        # MATLAB convert [1] to 1
        # so, convert 1 to [1]
        for key in dict_roicheck.keys():
            if isinstance(dict_roicheck[key], int):
                dict_roicheck[key] = [dict_roicheck[key]]

        table_columns = dict_roicheck.get("TableColumns")
        list_celltype = [col_name for col_name, col_info in table_columns.items() if col_info["type"] == "celltype"]
        dict_roi_celltype = {celltype: dict_roicheck[celltype] for celltype in list_celltype}
        self.data_manager.dict_roi_celltype[app_key] = dict_roi_celltype

        index_to_label = {idx: i for i, celltype in enumerate(list_celltype) for idx in dict_roi_celltype[celltype]}
        self.data_manager.dict_roi_visibility[app_key] = np.array([index_to_label[i] for i in range(max(index_to_label) + 1)])


    def loadMultiSessionData(self):
        """
        Load data from multiple sessions
        """
        # set app keys
        self.app_keys = []
        self.data_manager.dict_roi_visibility = {}
        for i, (path_fall, path_roi) in enumerate(zip(self.list_path_fall, self.list_path_roi_curation)):
            session_key = f"session_{i}"

            # Load Fall.mat
            success, e = self.data_manager.loadFallMat(
                app_key=session_key,
                path_fall=path_fall,
                config_manager=self.config_manager
            )
            # Load ROICuration.mat
            self.loadROICurationMat(
                app_key=session_key,
                path_roi_curation=path_roi
            )
            if i == 0: # Exception handling for primary app key # HARD-CODED !!!
                success, e = self.data_manager.loadFallMat(
                    app_key=self.app_key_pri,
                    path_fall=path_fall
                )
            if not success:
                raise Exception(f"Failed to load Fall.mat for {session_key}: {e}")
            
            # set ROI visibility dict
            self.data_manager.dict_roi_visibility[session_key] = {roi_id: True for roi_id in self.data_manager.getDictROICoords(session_key).keys()}

        # generate session colors
        self.data_manager.session_keys = [f"session_{i}" for i in range(len(self.list_path_fall))]
        self.data_manager.session_colors = generateSessionColors(len(self.data_manager.session_keys))
            
        return True
    
    # update view for CheckMultiSessionROICoordinates
    def updateView_CheckMultiSessionROICoordinates(self) -> None:
        """
        Update view for CheckMultiSessionROICoordinates
        """
        from optic.utils.view_utils import colorizeGrayscale, alphaBlend, alphaBlendImage, getROIMask
        ALPHA_ROI = 128

        # Get image size from first session
        height, width = self.data_manager.getImageSize("pri") # HARDCODED !!!
        view_control = self.control_manager.view_controls[self.app_key_pri] # HARDCODED !!!
        
        # Initialize result image (black background)
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Process each session
        for session_key, session_color in zip(self.data_manager.session_keys, self.data_manager.session_colors):
            # Check bg checkbox and draw background
            bg_checkbox_key = f"{session_key}_display_bg"
            if self.widget_manager.dict_checkbox[bg_checkbox_key].isChecked():
                bg_image_type = view_control.bg_image_type # HARDCODED !!!
                if view_control.show_reg_im_bg:
                    bg_image = self.data_manager.getDictBackgroundImageRegistered(session_key).get(bg_image_type)
                else:
                    bg_image = self.data_manager.getDictBackgroundImage(session_key).get(bg_image_type)
                if bg_image is not None:
                    colored_bg = colorizeGrayscale(bg_image, session_color)
                    bg_mask = np.ones((height, width), dtype=np.uint8)
                    result = alphaBlendImage(result, colored_bg, bg_mask, alpha=ALPHA_ROI)
            
            # Get ROI data
            dict_roi = self.data_manager.getDictROICoords(session_key)
            dict_roi_visibility = self.data_manager.dict_roi_visibility.get(session_key)
            
            # Draw ROI mask
            roi_mask = getROIMask(dict_roi, dict_roi_visibility, (height, width))
            result = alphaBlend(result, roi_mask, session_color, alpha=ALPHA_ROI)
        
        # Update view
        qimage = QImage(result.data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        view = view_control.q_view
        scaled_pixmap = pixmap.scaled(
            view.viewport().size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        view_control.layer_bg.setPixmap(scaled_pixmap)
        
        # Fit scene to view
        view_control.q_scene.setSceneRect(QRectF(scaled_pixmap.rect()))

    """
    bindFunc Functions
    """
    def bindFuncFileLoaderDialog(self):
        # Load File button - reopen the file loader dialog
        self.widget_manager.dict_button["load_file"].clicked.connect(
            lambda: self.showFileLoaderDialog()
        )

    # Radiobutton BGImageType changed
    def bindFuncRadiobuttonBGImageTypeChanged(self, q_buttongroup) -> None:
        def _onBGImageTypeChanged(button_id: int) -> None:
            bg_image_type = q_buttongroup.button(button_id).text()
            self.control_manager.view_controls[self.app_key_pri].setBackgroundImageType(bg_image_type)
            self.updateView_CheckMultiSessionROICoordinates()
        q_buttongroup.buttonClicked[int].connect(_onBGImageTypeChanged)
        checked_button = q_buttongroup.checkedButton()
        _onBGImageTypeChanged(q_buttongroup.id(checked_button))

    # Checkbox Background/Celltype display changed
    def bindFuncCheckboxSessionDisplayChanged(self, q_checkbox, session_key, celltype) -> None:
        def _onSessionDisplayChanged(state: int) -> None:
            is_checked = q_checkbox.isChecked()
            if celltype == "bg":
                # Background display
                self.updateView_CheckMultiSessionROICoordinates()
            else:
                # Celltype display
                idxs_display_true = self.data_manager.dict_roi_celltype.get(session_key).get(celltype, [])
                for roi_id in idxs_display_true:
                    self.data_manager.dict_roi_visibility[session_key][roi_id] = is_checked
                self.updateView_CheckMultiSessionROICoordinates()
        q_checkbox.stateChanged.connect(_onSessionDisplayChanged)
        _onSessionDisplayChanged(q_checkbox.checkState())

    # Checkbox Show Registered BG Image
    def bindFuncCheckboxShowRegisteredBGImage(self, q_checkbox) -> None:
        def onVisibilityChanged(state: int) -> None:
            is_visible = (state == Qt.Checked)
            self.control_manager.view_controls[self.app_key_pri].setShowRegImBG(is_visible)
            self.updateView_CheckMultiSessionROICoordinates()
        q_checkbox.stateChanged.connect(onVisibilityChanged)

    # Checkbox Show Registered ROI Image
    def bindFuncCheckboxShowRegisteredROIImage(self, q_checkbox) -> None:
        def onVisibilityChanged(state: int) -> None:
            is_visible = (state == Qt.Checked)
            self.control_manager.view_controls[self.app_key_pri].setShowRegImROI(is_visible)
            self.updateView_CheckMultiSessionROICoordinates()
        q_checkbox.stateChanged.connect(onVisibilityChanged)

    # Button Run Elastix for image registration
    def bindFuncButtonRunElastixForFall(
            self,
            q_button: QPushButton,
            combobox_elastix_method: QComboBox,
    ) -> None:
        from optic.processing.elastix import (
            convertDictToElastixFormat, makeElastixParameterObject, calculateSingleTransform, 
            applySingleTransform, applyDictROICoordsTransform
        )
        def _runElastix():
            path_points_txt: str="./elastix/points_tmp.txt"
            output_directory: str="./elastix"
            os.makedirs(output_directory, exist_ok=True)

            elastix_method = combobox_elastix_method.currentText()
            print(f"{elastix_method} transform")
            dict_params = self.config_manager.json_config.get("elastix_params")[elastix_method]
            self.data_manager.dict_parameter_map[self.app_key_pri] = convertDictToElastixFormat(dict_params)
            parameter_object = makeElastixParameterObject(self.data_manager.getParameterMap(self.app_key_pri))
            
            print("Elastix Parameters", dict_params)

            # get fixed image and moving image, (meanImg, meanImgE, max_proj, Vcorr)
            session_fix = int(self.widget_manager.dict_combobox["elastix_ref_plane_t"].currentText())
            key_session_fix = f"session_{session_fix}"
            img_type_pri = self.control_manager.view_controls[self.app_key_pri].getBackgroundImageType()
            img_fix = self.data_manager.getDictBackgroundImage(key_session_fix).get(img_type_pri)

            if len(self.data_manager.session_keys) < 2:
                QMessageBox.warning(self, "Error", "At least two sessions are required for registration.")
                return
            else:
                for i, session_key_mov in enumerate(self.data_manager.session_keys):
                    if session_key_mov == key_session_fix:
                        continue
                    print(f"Registering {session_key_mov} to {key_session_fix}...")
                    img_type_sec = img_type_pri
                    img_mov = self.data_manager.getDictBackgroundImage(session_key_mov).get(img_type_sec)
                    # run elastix
                    transform_parameters = calculateSingleTransform(img_fix, img_mov, parameter_object, output_directory)
                    self.data_manager.dict_transform_parameters[session_key_mov] = transform_parameters
                    # apply transform parameters to image
                    # background image
                    dict_im_bg_reg_mov = {}
                    for key_im in self.data_manager.getDictBackgroundImage(session_key_mov).keys():
                        dict_im_bg_reg_mov[key_im] = applySingleTransform(self.data_manager.getDictBackgroundImage(session_key_mov).get(key_im), transform_parameters, output_directory)
                    self.data_manager.dict_im_bg_reg[session_key_mov] = dict_im_bg_reg_mov
                    # ROI image
                    img_roi_mov = deepcopy(self.data_manager.getDictROIImage(session_key_mov).get("all"))
                    val_max = np.max(img_roi_mov)
                    img_roi_mov_reg = applySingleTransform(img_roi_mov, transform_parameters, output_directory)
                    img_roi_mov_reg_clipped = np.minimum(img_roi_mov_reg, val_max) # avoid making contours of ROIs
                    self.data_manager.dict_im_roi_reg[session_key_mov]["all"] = img_roi_mov_reg_clipped
                    
                    # ROI coordinates
                    path_transform_parameters_file = os.path.join(output_directory,"TransformParameters.0.txt") # hardcoded !!!
                    dict_roi_coords = self.data_manager.getDictROICoords(session_key_mov)
                    dict_roi_coords_reg = applyDictROICoordsTransform(
                        img_fix, img_mov, 
                        dict_roi_coords, 
                        self.data_manager.getParameterMap(self.app_key_pri),
                        path_transform_parameters_file, 
                        path_points_txt, 
                        output_directory
                        )
                    self.data_manager.dict_roi_coords_reg[session_key_mov] = dict_roi_coords_reg

                    self.updateView_CheckMultiSessionROICoordinates()

                    shutil.rmtree(output_directory)
                    os.remove(path_points_txt)
                QMessageBox.information(self, "Image Registration Finish", "Image Registration Finished!")
        q_button.clicked.connect(lambda: _runElastix())

    """
    bindFunc All Widgets
    """
    def bindFuncAllWidget(self):
        # Load File button
        self.bindFuncFileLoaderDialog()
        # Exit
        bindFuncExit(self.widget_manager.dict_button["exit"], self)
    
        # Radiobutton BGImageType buttonChanged
        self.bindFuncRadiobuttonBGImageTypeChanged(q_buttongroup=self.widget_manager.dict_buttongroup[f"im_bg_type"])

        # Checkbox Session Display Changed
        for session_key in self.data_manager.session_keys:
            list_checkbox = ["bg"] + list(self.data_manager.dict_roi_celltype[session_key].keys())
            list_checkbox = [f"{session_key}_display_{celltype}" for celltype in list_checkbox]
            for checkbox_key in list_checkbox:
                celltype = checkbox_key.replace(f"{session_key}_display_", "")
                self.bindFuncCheckboxSessionDisplayChanged(
                    q_checkbox=self.widget_manager.dict_checkbox[checkbox_key],
                    session_key=session_key,
                    celltype=celltype
                )

        # Elastix config
        self.widget_manager.dict_button[f"elastix_config"].clicked.connect(lambda: self.showSubWindowElastixParamsConfig())
        # Show registered background image
        self.bindFuncCheckboxShowRegisteredBGImage(q_checkbox=self.widget_manager.dict_checkbox['show_reg_im_bg'])
        # Show registered ROI image
        self.bindFuncCheckboxShowRegisteredROIImage(q_checkbox=self.widget_manager.dict_checkbox['show_reg_im_roi'])
        # run elastix button
        self.bindFuncButtonRunElastixForFall(
            q_button=self.widget_manager.dict_button["elastix_run_t"],
            combobox_elastix_method=self.widget_manager.dict_combobox["elastix_method"],
        )

if __name__ == "__main__":
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    applyAppStyle(app)
    gui = CheckMultiSessionROICoordinatesGUI()
    gui.show()
    sys.exit(app.exec_())