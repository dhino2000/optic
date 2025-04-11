from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog
from functools import partial
from optic.config import *
from optic.controls import *
from optic.dialog import *
from optic.gui import *
from optic.io import *
from optic.manager import *
from optic.gui.bind_func import *

class Suite2pROITrackingGUI(QMainWindow):
    def __init__(self):
        APP_NAME = "SUITE2P_ROI_TRACKING"
        QMainWindow.__init__(self)
        self.widget_manager, self.config_manager, self.data_manager, self.control_manager = initManagers(WidgetManager(), ConfigManager(), DataManager(), ControlManager())
        self.config_manager.setCurrentApp(APP_NAME)
        self.app_keys = self.config_manager.gui_defaults["APP_KEYS"]

        self.setupUI_done = False
        setupMainWindow(self, self.config_manager.gui_defaults)

        self.initUI()

    """
    setup UI Function
    """
    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout_main = QGridLayout(self.central_widget)

        # FileLoadUI用のレイアウト
        self.layout_file_load = QHBoxLayout()
        self.setupFileLoadUI()
        self.layout_main.addLayout(self.layout_file_load, 1, 0, 1, 1)

        # メインUI用のレイアウト
        self.layout_main_ui = QGridLayout()
        self.layout_main.addLayout(self.layout_main_ui, 0, 0, 1, 2)

        self.layout_extra_ui = QHBoxLayout()
        self.layout_main.addLayout(self.layout_extra_ui, 1, 1, 1, 1)

    def setupFileLoadUI(self):
        file_load_widget = QWidget()
        layout = QVBoxLayout(file_load_widget)
        # ファイル読み込み用のUIを追加
        layout.addLayout(self.makeLayoutSectionBottom())
        # bindFunc
        self.bindFuncFileLoadUI()

        self.layout_file_load.addWidget(file_load_widget)

    def loadFilePathsandInitialize(self):
        self.control_manager, self.data_manager = initManagers(self.control_manager, self.data_manager)
        success = self.loadData()
        if success:
            QMessageBox.information(self, "File load", "File loaded successfully!")
            self.setupMainUI()
        else:
            QMessageBox.warning(self, "File Load Error", "Failed to load the file.")
            return

    def setupMainUI(self):
        if self.setupUI_done:
            # メインUIのクリア
            clearLayout(self.layout_main_ui)
            clearLayout(self.layout_extra_ui)
        
        # 新しいメインUIの設定
        self.setupMainUILayouts()
        self.setupControls()
        self.bindFuncAllWidget()

        self.setupUI_done = True

    def loadData(self):
        for app_key in self.app_keys:
            success = self.data_manager.loadFallMat(
                app_key=app_key, 
                path_fall=self.widget_manager.dict_lineedit[f"path_fall_{app_key}"].text(),
                config_manager=self.config_manager
            )
        return success

    def setupMainUILayouts(self):
        self.layout_main_ui.addLayout(self.makeLayoutSectionLeftUpper(), 0, 0, 1, 1)
        self.layout_main_ui.addLayout(self.makeLayoutSectionRightUpper(), 0, 1, 1, 1)
        self.layout_extra_ui.addLayout(self.makeLayoutSectionBottomExtra())

    def setupControls(self):
        for app_key in self.app_keys:
            self.control_manager.table_controls[app_key] = TableControl(
                app_key=app_key,
                q_table=self.widget_manager.dict_table[app_key],
                data_manager=self.data_manager,
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
            )
            
            self.control_manager.table_controls[app_key].setupWidgetROITable(app_key)
            self.control_manager.view_controls[app_key] = ViewControl(
                app_key=app_key,
                q_view=self.widget_manager.dict_view[app_key], 
                q_scene=self.widget_manager.dict_scene[app_key], 
                data_manager=self.data_manager, 
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
                app_key_sec=self.app_keys[1] if app_key == self.app_keys[0] else None # only "pri" app_key has sec app_key
            )
            self.control_manager.view_controls[app_key].setViewSize()
            
            self.control_manager.initializeSkipROITypes(app_key, self.control_manager.table_controls[app_key].table_columns)

    """
    makeLayout Function; Component
    小要素のLayout
    return -> Layout
    """
    "Left/Right Upper"
    # View
    def makeLayoutComponentROIView(self, app_key):
        layout = makeLayoutViewWithZTSlider(self.widget_manager, app_key)
        return layout

    # ROI property label
    def makeLayoutComponentROIPropertyDisplay_Threshold(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIProperty(self.widget_manager, key_label=f"{app_key}_roi_prop"))
        return layout
    
    # ROI display, background image button group, checkbox
    def makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(self, app_key):
        layout = QHBoxLayout()
        layout.addWidget(makeLayoutWidgetDislplayCelltype(
            self.widget_manager, 
            key_checkbox=f'{app_key}_display_celltype', 
            key_scrollarea=f'{app_key}_display_celltype', 
            table_columns=self.config_manager.table_columns[app_key],
            gui_defaults=self.config_manager.gui_defaults,
        ))
        layout.addWidget(makeLayoutWidgetBGImageTypeDisplay(
            self, 
            self.widget_manager, 
            key_buttongroup=f'{app_key}_im_bg_type'
        ))
        layout.addWidget(makeLayoutWidgetROIChooseSkip(
            self.widget_manager, 
            key_checkbox=f'{app_key}_skip_celltype', 
            key_scrollarea=f'{app_key}_skip_celltype', 
            table_columns=self.config_manager.table_columns[app_key],
            gui_defaults=self.config_manager.gui_defaults,
        ))
        return layout
    
    # channel contrast, ROI opacity slider
    def makeLayoutComponentContrastOpacitySlider(self, app_key):
        layout = QVBoxLayout()
        channels = self.config_manager.gui_defaults["CHANNELS"]
        layout_channel = QHBoxLayout()
        for channel in channels:
            layout_channel.addLayout(makeLayoutContrastSlider(
                self.widget_manager, 
                key_label=f"{app_key}_{channel}", 
                key_checkbox=f"{app_key}_{channel}", 
                key_slider=f"{app_key}_{channel}", 
                label_checkbox=f"Show {channel} channel", 
                label_label=f"{channel} Value", 
                checked=True
            ))

        layout.addLayout(layout_channel)
        layout.addLayout(makeLayoutOpacitySlider(
            self.widget_manager, 
            key_label=app_key, 
            key_slider=app_key, 
            label=app_key
        ))
        return layout
    
    # Table, ROI count label, Table Columns Config, Set ROI Celltype, ROICheck IO
    def makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICheckIO(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutTableROICountLabel(
            self.widget_manager, 
            key_label=app_key, 
            key_table=app_key, 
            table_columns=self.config_manager.table_columns[app_key]
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(key=f"{app_key}_config_table", label="Table Columns Config"))
        layout.addLayout(makeLayoutROICheckIO(
            self.widget_manager, 
            key_button_save=f"roicuration_save_{app_key}",
            key_button_load=f"roicuration_load_{app_key}",
        ))
        return layout

    def makeLayoutComponent_View_Label_Radiobutton_Slider(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentROIView(app_key))
        layout.addLayout(self.makeLayoutComponentROIPropertyDisplay_Threshold(app_key))
        layout.addLayout(self.makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(app_key))
        layout.addLayout(self.makeLayoutComponentContrastOpacitySlider(app_key))
        return layout
    
    def makeLayoutComponent_Table_Button(self, app_key):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICheckIO(app_key))
        return layout

    "Bottom Extra"
    # Image Registration
    def makeLayoutComponenImageRegistration(self):
        layout = makeLayoutFallRegistration(
            self.widget_manager,
            self.data_manager,
            self.app_keys[0],                 
            f"elastix_registration",
            f"elastix_ref_c",
            f"opacity_roi_pair",
            f"elastix_method",
            f"elastix_ref_c",    
            f"elastix_config", 
            f"elastix_run",
            f"show_roi_match",
            f"show_roi_pair",
            f"show_reg_im_bg",
            f"show_reg_im_roi",
            f"opacity_roi_pair",
        )
        layout.addWidget(self.widget_manager.makeWidgetButton(key="save_reg_roi_bg", label="Save registered ROI and images"))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="load_reg_roi_bg", label="Load registered ROI and images"))
        return layout
    
    # Optimal Transport ROI Matching
    def makeLayoutComponentROIMatching(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIMatching(
            self.widget_manager,
            "roi_matching",
            "ot_method",
            "ot_partial_mass",
            "ot_partial_reg",
            "ot_dist_exp",
            "ot_threshold_transport",
            "ot_threshold_cost",
            "ot_partial_mass",
            "ot_partial_reg",
            "ot_dist_exp",
            "ot_threshold_transport",
            "ot_threshold_cost",
            "ot_method",
            "ot_run",
            "ot_clear",
        ))
        layout.addLayout(makeLayoutROIMatchingTest(
            self.widget_manager,
            "roi_matching_test",
        ))
        layout.addLayout(makeLayoutROITrackingIO(
            self.widget_manager,
            "roi_matching_save",
            "roi_matching_load",
        ))
        return layout

    "Bottom"
    # ファイル読み込み用UI Layout
    def makeLayoutComponentFileLoadUI(self):
        layout = QVBoxLayout()
        # Label
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="load_fall", label="File Load", font_size=12, bold=True, italic=True, use_global_style=False))
        # LineEdit
        for app_key in self.app_keys:
            list_label = [f"Fall mat file path ({app_key} Image)"]
            list_key = [f"path_fall_{app_key}"]
            for label, key in zip(list_label, list_key):
                layout.addLayout(makeLayoutLoadFileWidget(self.widget_manager, label=label, key_label=key, key_lineedit=key, key_button=key))
        # Button
        layout.addLayout(makeLayoutLoadFileExitHelp(self.widget_manager))
        return layout

    

    """
    makeLayout Function; Section
    領域レベルの大Layout
    """
    # 上段, 左
    def makeLayoutSectionLeftUpper(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponent_View_Label_Radiobutton_Slider(self.app_keys[0]))
        layout.addLayout(self.makeLayoutComponent_Table_Button(self.app_keys[0]))
        return layout
    
    # 上段. 右
    def makeLayoutSectionRightUpper(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponent_View_Label_Radiobutton_Slider(self.app_keys[1]))
        layout.addLayout(self.makeLayoutComponent_Table_Button(self.app_keys[1]))
        return layout

    # 下段
    def makeLayoutSectionBottom(self):
        layout = self.makeLayoutComponentFileLoadUI()
        return layout
    
    # 下段, 追加
    def makeLayoutSectionBottomExtra(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponenImageRegistration())
        layout.addLayout(self.makeLayoutComponentROIMatching())
        return layout
    
    """
    make SubWindow, Dialog Function
    """
    # Table Column Config Dialog
    def showSubWindowTableColumnConfig(self, app_key):
        config_window = TableColumnConfigDialog(
            self, 
            self.control_manager.table_controls[app_key].table_columns, 
            self.config_manager.gui_defaults
        )
        if config_window.exec_():
            self.loadFilePathsandInitialize()

    # Elastix Params Config Dialog
    def showSubWindowElastixParamsConfig(self):
        config_window = ElastixParamsConfigDialog(
            self, 
            self.config_manager.json_config.get("elastix_params"),
            self.config_manager.gui_defaults,
        )
        if config_window.exec_() == QDialog.Accepted:
            self.config_manager.json_config.set("elastix_params", config_window.elastix_params)

    # ROI Matching Test Dialog
    def showSubWindowROIMatchingTest(self):
        config_window = ROIMatchingTestDialog(
            self, 
            self.config_manager.gui_defaults,
            self.data_manager,
            self.config_manager,
            self.control_manager,
            self.app_keys[0],
            self.app_keys[1],
            self.control_manager.view_controls[self.app_keys[0]].getShowRegImROI()
        )
        if config_window.exec_() == QDialog.Accepted:
            pass

    """
    bindFunc Function
    配置したwidgetに関数を紐づけ
    """
    def bindFuncFileLoadUI(self):
        for app_key in self.app_keys:
            list_key = [f"path_fall_{app_key}"]
            list_filetype = ["mat"]
            for key, filetype in zip(list_key, list_filetype):
                bindFuncLoadFileWidget(q_widget=self, q_button=self.widget_manager.dict_button[key], q_lineedit=self.widget_manager.dict_lineedit[key], filetype=filetype)

        self.widget_manager.dict_button["load_file"].clicked.connect(lambda: self.loadFilePathsandInitialize())
        bindFuncExit(q_window=self, q_button=self.widget_manager.dict_button["exit"])
        bindFuncHelp(q_button=self.widget_manager.dict_button["help"], url=AccessURL.HELP[self.config_manager.current_app])

    def bindFuncAllWidget(self):
        for app_key in self.app_keys:
            # ROICheck save load
            bindFuncROICheckIO(
                q_window=self, 
                q_lineedit=self.widget_manager.dict_lineedit[f"path_fall_{app_key}"], 
                q_button_save=self.widget_manager.dict_button[f"roicuration_save_{app_key}"], 
                q_button_load=self.widget_manager.dict_button[f"roicuration_load_{app_key}"], 
                q_table=self.widget_manager.dict_table[f"{app_key}"], 
                widget_manager=self.widget_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
                app_key=app_key,
                local_var=False
            )
            # Table Column Config
            self.widget_manager.dict_button[f"{app_key}_config_table"].clicked.connect(
                partial(self.showSubWindowTableColumnConfig, app_key)
            )
            # Radiobutton BGImageType buttonChanged
            bindFuncRadiobuttonBGImageTypeChanged(
                q_buttongroup=self.widget_manager.dict_buttongroup[f"{app_key}_im_bg_type"], 
                view_control=self.control_manager.view_controls[app_key],
            )
            # Radiobutton ROIDisplayType checkboxChanged
            dict_q_checkbox = {}
            for celltype in self.config_manager.table_columns[app_key]._celltype:
                dict_q_checkbox[celltype] = [checkbox for key, checkbox in self.widget_manager.dict_checkbox.items() if (celltype in key) and ("celltype_roi_display" in key) and (app_key in key)][0]
            bindFuncCheckBoxDisplayCelltypeChanged(
                dict_q_checkbox=dict_q_checkbox, 
                view_control=self.control_manager.view_controls[app_key],
                table_control=self.control_manager.table_controls[app_key],
            )
            # Checkbox ROISkip stateChanged
            bindFuncCheckBoxROIChooseSkip(
                dict_q_checkbox=dict_q_checkbox,
                control_manager=self.control_manager,
                app_key=app_key,
            )
            # ROICheck Table TableColumn CellType Changed
            bindFuncRadiobuttonOfTableChanged(
                table_control=self.control_manager.table_controls[app_key],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Slider Opacity valueChanged
            bindFuncOpacitySlider(
                q_slider=self.widget_manager.dict_slider[f"{app_key}_opacity_roi_all"],
                view_control=self.control_manager.view_controls[app_key],
            )
            bindFuncHighlightOpacitySlider(
                q_slider=self.widget_manager.dict_slider[f"{app_key}_opacity_roi_selected"],
                view_control=self.control_manager.view_controls[app_key],
            )
            # Slider Contrast valueChanged, Checkbox show channel stateChanged
            for channel in self.config_manager.gui_defaults["CHANNELS"]:
                bindFuncBackgroundContrastSlider(
                    q_slider_min=self.widget_manager.dict_slider[f"{app_key}_{channel}_contrast_min"],
                    q_slider_max=self.widget_manager.dict_slider[f"{app_key}_{channel}_contrast_max"],
                    view_control=self.control_manager.view_controls[app_key],
                    channel=channel
                )
                bindFuncBackgroundVisibilityCheckbox(
                    q_checkbox=self.widget_manager.dict_checkbox[f"{app_key}_{channel}_show"], 
                    view_control=self.control_manager.view_controls[app_key],
                    channel=channel,
                )
            # View Event
            bindFuncViewEvents(
                q_view=self.widget_manager.dict_view[app_key],
                view_control=self.control_manager.view_controls[app_key],
            )

        # ROICheck Table onSelectionChanged
        bindFuncTableSelectionChangedWithTracking(
            q_table_pri=self.widget_manager.dict_table[self.app_keys[0]],
            q_table_sec=self.widget_manager.dict_table[self.app_keys[1]],
            table_control_pri=self.control_manager.table_controls[self.app_keys[0]],
            table_control_sec=self.control_manager.table_controls[self.app_keys[1]],
            view_control_pri=self.control_manager.view_controls[self.app_keys[0]],
            view_control_sec=self.control_manager.view_controls[self.app_keys[1]],
            canvas_control_pri=None,
            canvas_control_sec=None,
        )

        # Show matched ROI
        bindFuncCheckboxShowMatchedROI(
            q_checkbox=self.widget_manager.dict_checkbox['show_roi_match'],
            view_controls=self.control_manager.view_controls
        )
        # Show ROI pair
        bindFuncCheckboxShowROIPair(
            q_checkbox=self.widget_manager.dict_checkbox['show_roi_pair'],
            view_controls=self.control_manager.view_controls
        )
        # Slider ROI pair Opacity valueChanged
        bindFuncROIPairOpacitySlider(
            q_slider=self.widget_manager.dict_slider[f"opacity_roi_pair"],
            view_control=self.control_manager.view_controls[self.app_keys[0]],
        )
        # Show registered background image
        bindFuncCheckboxShowRegisteredBGImage(
            q_checkbox=self.widget_manager.dict_checkbox['show_reg_im_bg'],
            view_controls=self.control_manager.view_controls
        )
        # Show registered ROI image
        bindFuncCheckboxShowRegisteredROIImage(
            q_checkbox=self.widget_manager.dict_checkbox['show_reg_im_roi'],
            view_controls=self.control_manager.view_controls
        )

        # Elastix Run
        bindFuncButtonRunElastixForFall(
                self,
                q_button=self.widget_manager.dict_button['elastix_run'],
                data_manager=self.data_manager,
                config_manager=self.config_manager,
                control_manager=self.control_manager,
                app_key=self.app_keys[0],
                app_key_sec=self.app_keys[1],
                combobox_elastix_method=self.widget_manager.dict_combobox['elastix_method'],
                path_points_txt="points_tmp.txt",
                output_directory="./elastix"
        ) 
        # Elastix config
        self.widget_manager.dict_button[f"elastix_config"].clicked.connect(
            lambda: self.showSubWindowElastixParamsConfig()
        )
        # Registerd ROI and images IO
        bindFuncRegisteredROIAndBGImageIO(
            q_button_save=self.widget_manager.dict_button['save_reg_roi_bg'],
            q_button_load=self.widget_manager.dict_button['load_reg_roi_bg'],
            q_window=self,
            q_lineedit=self.widget_manager.dict_lineedit[f"path_fall_{self.app_keys[1]}"],
            data_manager=self.data_manager,
            app_key=self.app_keys[1],
        )
        # ROI Tracking IO
        bindFuncROITrackingIO(
            q_window=self,
            q_button_save=self.widget_manager.dict_button['roi_matching_save'],
            q_button_load=self.widget_manager.dict_button['roi_matching_load'],
            q_lineedit_pri=self.widget_manager.dict_lineedit[f'path_fall_{self.app_keys[0]}'],
            q_lineedit_sec=self.widget_manager.dict_lineedit[f'path_fall_{self.app_keys[1]}'],
            q_table_pri=self.widget_manager.dict_table[self.app_keys[0]],
            q_table_sec=self.widget_manager.dict_table[self.app_keys[1]],
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            app_key_pri=self.app_keys[0],
            app_key_sec=self.app_keys[1],
        )
        # ROI Matching Run
        bindFuncButtonRunROIMatching(
            self,
            q_button=self.widget_manager.dict_button['ot_run'],
            widget_manager=self.widget_manager,
            data_manager=self.data_manager,
            control_manager=self.control_manager,
            app_key_pri=self.app_keys[0],
            app_key_sec=self.app_keys[1],
        )
        # Clear ROI Matching result
        bindFuncButtonClearColumnCells(
            q_button=self.widget_manager.dict_button['ot_clear'],
            q_table=self.widget_manager.dict_table[self.app_keys[0]],
            idx_col=self.config_manager.table_columns[self.app_keys[0]].getColumns()["Cell_ID_Match"]["order"], # hardcoded !!!
        )
        # ROI Matching Test
        self.widget_manager.dict_button[f"roi_matching_test"].clicked.connect(
            lambda: self.showSubWindowROIMatchingTest()
        )