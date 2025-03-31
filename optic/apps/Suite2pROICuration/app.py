from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication
from optic.config import *
from optic.controls import *
from optic.dialog import *
from optic.gui import *
from optic.io import *
from optic.manager import *
from optic.gui.bind_func import *

class Suite2pROICurationGUI(QMainWindow):
    def __init__(self):
        APP_NAME = "SUITE2P_ROI_CURATION"
        QMainWindow.__init__(self)
        self.widget_manager, self.config_manager, self.data_manager, self.control_manager, self.layout_manager = initManagers(
            WidgetManager(), ConfigManager(), DataManager(), ControlManager(), LayoutManager()
        )
        self.config_manager.setCurrentApp(APP_NAME)
        self.app_keys = self.config_manager.gui_defaults["APP_KEYS"]
        self.app_key_pri = self.app_keys[0]

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
        self.layout_file_load = QVBoxLayout()
        self.setupFileLoadUI()
        self.layout_main.addLayout(self.layout_file_load, 1, 0, 1, 1)

        # メインUI用のレイアウト
        self.layout_main_ui = QGridLayout()
        self.layout_main.addLayout(self.layout_main_ui, 0, 0, 1, 1)

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
        
        # 新しいメインUIの設定
        self.setupMainUILayouts()
        self.setupControls()
        self.bindFuncAllWidget()

        self.setupUI_done = True

    def loadData(self):
        success = self.data_manager.loadFallMat(
            app_key=self.app_key_pri, 
            path_fall=self.widget_manager.dict_lineedit[f"path_fall_{self.app_key_pri}"].text()
        )
        if self.widget_manager.dict_lineedit[f"path_reftif_{self.app_key_pri}"].text() != "":
            success = self.data_manager.loadTifImage(
                app_key=self.app_key_pri,
                path_image=self.widget_manager.dict_lineedit[f"path_reftif_{self.app_key_pri}"].text(), 
            )
        return success

    def setupMainUILayouts(self):
        self.layout_main_ui.addLayout(self.makeLayoutSectionLeftUpper(), 0, 0)
        self.layout_main_ui.addLayout(self.makeLayoutSectionMiddleUpper(), 0, 1)
        self.layout_main_ui.addLayout(self.makeLayoutSectionRightUpper(), 0, 2)

    def setupControls(self):
        self.control_manager.table_controls[self.app_key_pri] = TableControl(
            app_key=self.app_key_pri,
            q_table=self.widget_manager.dict_table[self.app_key_pri],
            data_manager=self.data_manager,
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
        )
        
        self.control_manager.table_controls[self.app_key_pri].setupWidgetROITable(self.app_key_pri)
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
        self.control_manager.canvas_controls[self.app_key_pri] = CanvasControl(
            app_key=self.app_key_pri,
            figure=self.widget_manager.dict_figure[self.app_key_pri], 
            canvas=self.widget_manager.dict_canvas[self.app_key_pri], 
            data_manager=self.data_manager, 
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            ax_layout="triple"
        )
        self.control_manager.initializeSkipROITypes(self.app_key_pri, self.control_manager.table_controls[self.app_key_pri].table_columns)

    """
    makeLayout Function; Component
    小要素のLayout
    return -> Layout
    """

    "Bottom"
    # ファイル読み込み用UI Layout
    def makeLayoutComponentFileLoadUI(self):
        layout = QVBoxLayout()

        # LineEdit
        list_label = ["Fall mat file path", "Reference Tiff image file path (optional)"]
        list_key = [f"path_fall_{self.app_key_pri}", f"path_reftif_{self.app_key_pri}"]
        for label, key in zip(list_label, list_key):
            layout.addLayout(makeLayoutLoadFileWidget(
                self.widget_manager, 
                label=label, 
                key_label=key, 
                key_lineedit=key, 
                key_button=key
            ))
        # Button
        layout.addLayout(makeLayoutLoadFileExitHelp(self.widget_manager))
        return layout

    "Left Upper"
    def makeLayoutComponentPlotProperty(self):
        layout = QHBoxLayout()
        layout.addLayout(makeLayoutLightPlotMode(self.widget_manager, self.config_manager))
        layout.addLayout(makeLayoutMinimumPlotRange(self.widget_manager, self.config_manager, self.app_key_pri))
        return layout
    
    # EventFile load, plot property
    def makeLayoutComponentEventFilePlotProperty(self):
        layout = makeLayoutEventFilePlotProperty(
            self.widget_manager, 
            f"{self.app_key_pri}_load_eventfile",
            f"{self.app_key_pri}_clear_eventfile",
            f"{self.app_key_pri}_plot_eventfile",
            f"{self.app_key_pri}_plot_eventfile_ffneu",
            f"{self.app_key_pri}_plot_eventfile_dff0",
            f"{self.app_key_pri}_eventfile_prop_range",
            f"{self.app_key_pri}_eventfile_prop_ffneu",
            f"{self.app_key_pri}_eventfile_prop_dff0",
            f"{self.app_key_pri}_eventfile_loaded",
            f"{self.app_key_pri}_eventfile_prop_range",
            f"{self.app_key_pri}_eventfile_prop_ffneu",
            f"{self.app_key_pri}_eventfile_prop_dff0",
            f"{self.app_key_pri}_eventfile_loaded",
            self.app_key_pri)
        return layout
    
    "Middle Upper"
    # ROI view
    def makeLayoutComponentROIView(self):
        layout = makeLayoutViewWithZTSlider(self.widget_manager, self.app_key_pri)
        return layout

    # ROI property label
    def makeLayoutComponentROIPropertyDisplay_Threshold(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIProperty(self.widget_manager, key_label=f"{self.app_key_pri}_roi_prop"))
        return layout

    # ROI display, background image button group, checkbox
    def makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(self):
        layout = QHBoxLayout()
        layout.addWidget(makeLayoutWidgetDislplayCelltype(
            self.widget_manager, 
            key_checkbox=f'{self.app_key_pri}_display_celltype', 
            key_scrollarea=f'{self.app_key_pri}_display_celltype', 
            table_columns=self.config_manager.table_columns[self.app_key_pri]
        ))
        layout.addWidget(makeLayoutWidgetBGImageTypeDisplay(
            self, 
            self.widget_manager, 
            key_buttongroup=f'{self.app_key_pri}_im_bg_type'
        ))
        layout.addWidget(makeLayoutWidgetROIChooseSkip(
            self.widget_manager, 
            key_checkbox=f'{self.app_key_pri}_skip_celltype', 
            key_scrollarea=f'{self.app_key_pri}_skip_celltype', 
            table_columns=self.config_manager.table_columns[self.app_key_pri]
        ))
        return layout

    # channel contrast, ROI opacity slider
    def makeLayoutComponentContrastOpacitySlider(self):
        layout = QVBoxLayout()
        channels = self.config_manager.gui_defaults["CHANNELS"]
        layout_channel = QHBoxLayout()
        for channel in channels:
            layout_channel.addLayout(makeLayoutContrastSlider(
                self.widget_manager, 
                key_label=f"{self.app_key_pri}_{channel}", 
                key_checkbox=f"{self.app_key_pri}_{channel}", 
                key_slider=f"{self.app_key_pri}_{channel}", 
                label_checkbox=f"Show {channel} channel", 
                label_label=f"{channel} Value", 
                checked=True
            ))

        layout.addLayout(layout_channel)
        layout.addLayout(makeLayoutOpacitySlider(
            self.widget_manager, 
            key_label=self.app_key_pri, 
            key_slider=self.app_key_pri, 
            label=self.app_key_pri
        ))
        layout.addLayout(makeLayoutDisplayROIContours(
            self.widget_manager,
            key_checkbox_contour_all=f"{self.app_key_pri}_display_contour_all",
            key_checkbox_contour_selected=f"{self.app_key_pri}_display_contour_selected",
            key_checkbox_contour_next=f"{self.app_key_pri}_display_contour_next",
        ))
        return layout

    "Right Upper"
    # Table, ROI count label, Table Columns Config, Set ROI Celltype, ROICheck IO
    def makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICheckIO(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutTableROICountLabel(
            self.widget_manager, 
            key_label=self.app_key_pri, 
            key_table=self.app_key_pri, 
            table_columns=self.config_manager.table_columns[self.app_key_pri]
        ))
        layout.addWidget(self.widget_manager.makeWidgetButton(key=f"{self.app_key_pri}_config_table", label="Table Columns Config"))
        layout.addWidget(self.widget_manager.makeWidgetButton(key=f"{self.app_key_pri}_roi_celltype_set", label="Set ROI Celltype"))
        layout.addLayout(makeLayoutROICheckIO(
            self.widget_manager, 
            key_button_save=f"roicuration_save_{self.app_key_pri}",
            key_button_load=f"roicuration_load_{self.app_key_pri}",
        ))
        return layout

    # ROI Filter, threshold
    def makeLayoutComponentROIFilter(self):
        layout = QHBoxLayout()
        layout.addLayout(makeLayoutROIFilterThreshold(
            self.widget_manager, 
            key_label=f"{self.app_key_pri}_roi_filter", 
            key_lineedit=f"{self.app_key_pri}_roi_filter",
            dict_roi_threshold=self.config_manager.gui_defaults["ROI_THRESHOLDS"]
        ))
        layout.addLayout(makeLayoutROIFilterButton(
            self.widget_manager, 
            key_label=f"{self.app_key_pri}_roi_filter", 
            key_button=f"{self.app_key_pri}_roi_filter"
        ))
        return layout
    

    """
    makeLayout Function; Section
    領域レベルの大Layout
    """
    # 左上
    def makeLayoutSectionLeftUpper(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutCanvasTracePlot(
            self.widget_manager, 
            key_figure=self.app_key_pri, 
            key_canvas=self.app_key_pri, 
            key_button=f"export_canvas_{self.app_key_pri}"
        ), stretch=1)
        layout.addLayout(self.makeLayoutComponentPlotProperty())
        layout.addLayout(self.makeLayoutComponentEventFilePlotProperty())
        return layout

    # 中上
    def makeLayoutSectionMiddleUpper(self):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentROIView())
        layout.addLayout(self.makeLayoutComponentROIPropertyDisplay_Threshold())
        layout.addLayout(self.makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip())
        layout.addLayout(self.makeLayoutComponentContrastOpacitySlider())
        return layout
    
    # 右上
    def makeLayoutSectionRightUpper(self):
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICheckIO())
        layout.addLayout(self.makeLayoutComponentROIFilter())
        return layout

    # 下
    def makeLayoutSectionBottom(self):
        layout = self.makeLayoutComponentFileLoadUI()
        return layout
    
    """
    make SubWindow, Dialog Function
    """
    def showSubWindowTableColumnConfig(self, app_key):
        config_window = TableColumnConfigDialog(
            self, 
            self.control_manager.table_controls[app_key].table_columns, 
            self.config_manager.gui_defaults
        )
        if config_window.exec_():
            self.loadFilePathsandInitialize()

    def showSubWindowSetROICellTypeSet(self, app_key):
        celltype_window = ROICellTypeSetDialog(
            self, 
            self.app_key_pri,
            self.config_manager,
            self.control_manager.table_controls[app_key],
            self.config_manager.gui_defaults
        )
        celltype_window.show()
            

    """
    bindFunc Function
    配置したwidgetに関数を紐づけ
    """
    def bindFuncFileLoadUI(self):        
        list_key = [f"path_fall_{self.app_key_pri}", f"path_reftif_{self.app_key_pri}"]
        list_filetype = [Extension.MAT, Extension.TIFF]
        for key, filetype in zip(list_key, list_filetype):
            bindFuncLoadFileWidget(
                q_widget=self, 
                q_button=self.widget_manager.dict_button[key], 
                q_lineedit=self.widget_manager.dict_lineedit[key], 
                filetype=filetype
            )

        self.widget_manager.dict_button["load_file"].clicked.connect(lambda: self.loadFilePathsandInitialize())
        bindFuncExit(q_window=self, q_button=self.widget_manager.dict_button["exit"])
        bindFuncHelp(q_button=self.widget_manager.dict_button["help"], url=AccessURL.HELP[self.config_manager.current_app])

    def bindFuncAllWidget(self):
        # ROICheck save load
        bindFuncROICheckIO(
            q_window=self, 
            q_lineedit=self.widget_manager.dict_lineedit[f"path_fall_{self.app_key_pri}"], 
            q_button_save=self.widget_manager.dict_button[f"roicuration_save_{self.app_key_pri}"], 
            q_button_load=self.widget_manager.dict_button[f"roicuration_load_{self.app_key_pri}"], 
            q_table=self.widget_manager.dict_table[f"{self.app_key_pri}"], 
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            app_key=self.app_key_pri,
            local_var=False
        )
        # Table Column Config
        self.widget_manager.dict_button[f"{self.app_key_pri}_config_table"].clicked.connect(
            lambda: self.showSubWindowTableColumnConfig(self.app_key_pri)
        )
        # Set ROI Celltype
        self.widget_manager.dict_button[f"{self.app_key_pri}_roi_celltype_set"].clicked.connect(
            lambda: self.showSubWindowSetROICellTypeSet(self.app_key_pri)
        )
        # Radiobutton BGImageType buttonChanged
        bindFuncRadiobuttonBGImageTypeChanged(
            q_buttongroup=self.widget_manager.dict_buttongroup[f"{self.app_key_pri}_im_bg_type"], 
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Radiobutton ROIDisplayType checkboxChanged
        dict_q_checkbox = {}
        for celltype in self.config_manager.table_columns[self.app_key_pri]._celltype:
            dict_q_checkbox[celltype] = [checkbox for key, checkbox in self.widget_manager.dict_checkbox.items() if (celltype in key) and ("celltype_roi_display" in key)][0]
        bindFuncCheckBoxDisplayCelltypeChanged(
            dict_q_checkbox=dict_q_checkbox, 
            view_control=self.control_manager.view_controls[self.app_key_pri],
            table_control=self.control_manager.table_controls[self.app_key_pri],
        )
        # Checkbox ROISkip stateChanged
        bindFuncCheckBoxROIChooseSkip(
            dict_q_checkbox=dict_q_checkbox,
            control_manager=self.control_manager,
            app_key=self.app_key_pri,
        )
        # Filter ROIs
        bindFuncButtonFilterROI(
            q_button=self.widget_manager.dict_button[f"{self.app_key_pri}_roi_filter"],
            dict_q_lineedit={key: self.widget_manager.dict_lineedit[f"{self.app_key_pri}_roi_filter_{key}"] for key in self.config_manager.gui_defaults["ROI_THRESHOLDS"].keys()},
            table_control=self.control_manager.table_controls[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # ROICheck Table onSelectionChanged
        bindFuncTableSelectionChanged(
            q_table=self.widget_manager.dict_table[self.app_key_pri],
            table_control=self.control_manager.table_controls[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
            canvas_control=self.control_manager.canvas_controls[self.app_key_pri],
        )
        # ROICheck Table TableColumn CellType Changed
        bindFuncRadiobuttonOfTableChanged(
            table_control=self.control_manager.table_controls[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Slider Opacity valueChanged
        bindFuncOpacitySlider(
            q_slider=self.widget_manager.dict_slider[f"{self.app_key_pri}_opacity_roi_all"],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        bindFuncHighlightOpacitySlider(
            q_slider=self.widget_manager.dict_slider[f"{self.app_key_pri}_opacity_roi_selected"],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Slider Contrast valueChanged, Checkbox show channel stateChanged
        for channel in self.config_manager.gui_defaults["CHANNELS"]:
            bindFuncBackgroundContrastSlider(
                q_slider_min=self.widget_manager.dict_slider[f"{self.app_key_pri}_{channel}_contrast_min"],
                q_slider_max=self.widget_manager.dict_slider[f"{self.app_key_pri}_{channel}_contrast_max"],
                view_control=self.control_manager.view_controls[self.app_key_pri],
                channel=channel
            )
            bindFuncBackgroundVisibilityCheckbox(
                q_checkbox=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_{channel}_show"], 
                view_control=self.control_manager.view_controls[self.app_key_pri],
                channel=channel,
            )
        # display all, selected, next ROI Contour
        bindFuncCheckBoxDisplayROIContours(
            q_checkbox_contour_all=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_display_contour_all"],
            q_checkbox_contour_selected=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_display_contour_selected"],
            q_checkbox_contour_next=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_display_contour_next"],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # View Events
        bindFuncViewEvents(
            q_view=self.widget_manager.dict_view[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Canvas MouseEvent
        # Top axis events
        canvas_control = self.control_manager.canvas_controls[self.app_key_pri]
        bindFuncCanvasMouseEvent(
            canvas_control.canvas,
            canvas_control,
            canvas_control.axes[AxisKeys.TOP],
            list_event=['scroll_event', 'button_press_event', 'button_release_event', 'motion_notify_event'],
            list_func=[canvas_control.onScroll, canvas_control.onPress, canvas_control.onRelease, canvas_control.onMotion]
        )
        # Middle axis events
        bindFuncCanvasMouseEvent(
            canvas_control.canvas,
            canvas_control,
            canvas_control.axes[AxisKeys.MID],
            list_event=['button_press_event'],
            list_func=[canvas_control.onClick]
        )
        # export figure
        bindFuncButtonExportFigure(
            self.widget_manager.dict_button[f"export_canvas_{self.app_key_pri}"],
            self,
            self.widget_manager.dict_figure[self.app_key_pri],
            path_dst = self.widget_manager.dict_lineedit[f"path_fall_{self.app_key_pri}"].text().replace(".mat", "_traceplot.png")
        )
        # Canvas load EventFile
        bindFuncButtonEventfileIO(
            q_button_load=self.widget_manager.dict_button[f"{self.app_key_pri}_load_eventfile"],
            q_button_clear=self.widget_manager.dict_button[f"{self.app_key_pri}_clear_eventfile"],
            q_window=self,
            q_combobox_eventfile=self.widget_manager.dict_combobox[f"{self.app_key_pri}_eventfile_loaded"],
            data_manager=self.data_manager,
            control_manager=self.control_manager,
            canvas_control=self.control_manager.canvas_controls[self.app_key_pri],
            app_key=self.app_key_pri,
        )
        # Canvas plot EventFile property
        bindFuncCheckboxEventfilePlotProperty(
            q_checkbox_ffneu=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_plot_eventfile_ffneu"],
            q_checkbox_dff0=self.widget_manager.dict_checkbox[f"{self.app_key_pri}_plot_eventfile_dff0"],
            canvas_control=self.control_manager.canvas_controls[self.app_key_pri],
        )