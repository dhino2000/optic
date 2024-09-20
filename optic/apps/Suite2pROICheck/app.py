from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication
from ...config import *
from ...controls import *
from ...gui import *
from ...io import *
from ...manager import *


class Suite2pROICheckGUI(QMainWindow):
    def __init__(self):
        APP_NAME = "SUITE2P_ROI_CHECK"
        QMainWindow.__init__(self)
        self.widget_manager, self.config_manager, self.data_manager, self.control_manager, self.layout_manager = initManagers(WidgetManager(), ConfigManager(), DataManager(), ControlManager(), LayoutManager())
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
            self.setupMainUI()
        else:
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
        success = loadFallMATWithGUI(
            q_window=self, 
            data_manager=self.data_manager, 
            key_app=self.app_key_pri, 
            path_fall=self.widget_manager.dict_lineedit[f"{self.app_key_pri}_path_fall"].text()
        )
        if self.widget_manager.dict_lineedit[f"{self.app_key_pri}_path_reftif"].text() != "":
            self.data_manager.dict_im_bg_chan2[self.app_key_pri] = loadTIFImage(
                data_manager=self.data_manager, 
                key_dict_im_chan2=self.app_key_pri, 
                path_image=self.widget_manager.dict_lineedit[f"{self.app_key_pri}_path_reftif"].text(), 
                preprocessing=True
                )
        return success

    def setupMainUILayouts(self):
        self.layout_main_ui.addLayout(self.makeLayoutSectionLeftUpper(), 0, 0)
        self.layout_main_ui.addLayout(self.makeLayoutSectionMiddleUpper(), 0, 1)
        self.layout_main_ui.addLayout(self.makeLayoutSectionRightUpper(), 0, 2)

    def setupControls(self):
        self.control_manager.table_controls[self.app_key_pri] = TableControl(
                                                                key_app=self.app_key_pri,
                                                                q_table=self.widget_manager.dict_table[self.app_key_pri],
                                                                data_manager=self.data_manager,
                                                                widget_manager=self.widget_manager,
                                                                config_manager=self.config_manager,
                                                                control_manager=self.control_manager,
                                                                )
        
        self.control_manager.table_controls[self.app_key_pri].setupWidgetROITable(self.app_key_pri)
        self.control_manager.view_controls[self.app_key_pri] = ViewControl(
                                                                    key_app=self.app_key_pri,
                                                                    q_view=self.widget_manager.dict_view[self.app_key_pri], 
                                                                    q_scene=self.widget_manager.dict_scene[self.app_key_pri], 
                                                                    data_manager=self.data_manager, 
                                                                    widget_manager=self.widget_manager,
                                                                    config_manager=self.config_manager,
                                                                    control_manager=self.control_manager,
                                                                    )
        self.control_manager.view_controls[self.app_key_pri].setViewSize()
        self.control_manager.canvas_controls[self.app_key_pri] = CanvasControl(
                                                                    key_app=self.app_key_pri,
                                                                    figure=self.widget_manager.dict_figure[self.app_key_pri], 
                                                                    canvas=self.widget_manager.dict_canvas[self.app_key_pri], 
                                                                    data_manager=self.data_manager, 
                                                                    widget_manager=self.widget_manager,
                                                                    config_manager=self.config_manager,
                                                                    control_manager=self.control_manager,
                                                                    ax_layout="triple"
                                                                    )


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
        list_label = ["Fall mat file path", "Reference Tiff image file path (optional)", "Cellpose Mask path (optional)"]
        list_key = [f"{self.app_key_pri}_path_fall", f"{self.app_key_pri}_path_reftif", f"{self.app_key_pri}_path_cellpose"]
        for label, key in zip(list_label, list_key):
            layout.addLayout(makeLayoutLoadFileWidget(self.widget_manager, 
                                                      label=label, 
                                                      key_label=key, 
                                                      key_lineedit=key, 
                                                      key_button=key))
        # Button
        layout.addLayout(makeLayoutLoadFileExitHelp(self.widget_manager))
        return layout

    "Left Upper"
    # EventFileの読み込み, plot用
    def makeLayoutComponentEventFilePlot(self):
        layout = QVBoxLayout()
        # Eventのplot range
        layout.addLayout(makeLayoutLineEditLabel(self.widget_manager,
                                                 key_label="eventfile_align_plot_range",
                                                 key_lineedit="eventfile_align_plot_range",
                                                 label="plot range from Event start (pre, post; sec)",
                                                 text_set="(10, 10)"))
        # プロットに重ねるEventFile npyファイルの読み込みボタン, Clearボタン
        layout.addWidget(self.widget_manager.makeWidgetButton(key="loadEventFile", label="Load EventFile npy file"))  ### 要修正
        layout.addWidget(self.widget_manager.makeWidgetButton(key="clearEventFile", label="Clear"))
        return layout

    # trace plotの表示範囲
    def makeLayoutComponentTracePlotRange(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutLineEditLabel(self.widget_manager,
                                                key_label="minPlotRange",
                                                key_lineedit="minPlotRange",
                                                label="Minimum plot range (sec)",
                                                text_set="30"))
        layout.addWidget(self.widget_manager.makeWidgetCheckBox(key="plot_eventfile_trace", 
                                                 label="plot EventFile trace", 
                                                 checked=True,
                                                 ))
        return layout

    # 上記二つを合体
    def makeLayoutComponentEventFilePlot_TracePlotRange(self):
        layout = QHBoxLayout()
        layout.addLayout(self.makeLayoutComponentEventFilePlot())
        layout.addLayout(self.makeLayoutComponentTracePlotRange())
        return layout

    "Middle Upper"
    # ROI view
    def makeLayoutComponentROIView(self):
        layout = QVBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetView(key=self.app_key_pri))
        return layout

    # ROI property label, threshold lineedit
    def makeLayoutComponentROIPropertyDisplay_Threshold(self):
        layout = QVBoxLayout()

        layout.addLayout(makeLayoutROIProperty(self.widget_manager, key_label=f"{self.app_key_pri}_roi_prop"))
        layout.addLayout(makeLayoutROIThresholds(
            self.widget_manager, 
            key_label=f"{self.app_key_pri}_roi_threshold", 
            key_lineedit=f"{self.app_key_pri}_roi_threshold", 
            key_checkbox=f"{self.app_key_pri}_roi_threshold", 
            label_checkbox="ROI Show Threshold", 
            list_threshold_param=["npix", "compact"]))
        return layout

    # ROI display, background image button group, checkbox
    def makeLayoutComponentROIDisplay_BGImageDisplay_ROISkip(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutROIDisplayType(self, 
                                                  self.widget_manager, 
                                                  key_buttongroup=f'{self.app_key_pri}_roi_type', 
                                                  table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()))
        layout.addLayout(makeLayoutBGImageTypeDisplay(self, 
                                                      self.widget_manager, 
                                                      key_buttongroup=f'{self.app_key_pri}_bgimage_type'))
        layout.addLayout(makeLayoutROIChooseSkip(self.widget_manager, 
                                                 key_checkbox=f'{self.app_key_pri}', 
                                                 table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()))
        return layout

    # channel contrast, ROI opacity slider
    def makeLayoutComponentContrastOpacitySlider(self):
        layout = QVBoxLayout()
        channels = self.config_manager.gui_defaults["CHANNELS"]
        layout_channel = QHBoxLayout()
        for channel in channels:
            layout_channel.addLayout(makeLayoutContrastSlider(self.widget_manager, 
                                                            key_label=f"{self.app_key_pri}_{channel}", 
                                                            key_checkbox=f"{self.app_key_pri}_{channel}", 
                                                            key_slider=f"{self.app_key_pri}_{channel}", 
                                                            label_checkbox=f"Show {channel} channel", 
                                                            label_label=f"{channel} Value", 
                                                            checked=True))

        layout.addLayout(layout_channel)
        layout.addLayout(makeLayoutOpacitySlider(self.widget_manager, 
                                                key_label=self.app_key_pri, 
                                                key_slider=self.app_key_pri, 
                                                label=self.app_key_pri
                                                ))
        return layout

    "Right Upper"
    # Table, ROI count label, Table Columns Config, Set ROI Celltype, ROICheck IO
    def makeLayoutComponentTable_ROICountLabel_ROISetSameCelltype_ROICheckIO(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutTableROICountLabel(self.widget_manager, 
                                                      key_label=self.app_key_pri, 
                                                      key_table=self.app_key_pri, 
                                                      table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()))
        layout.addWidget(self.widget_manager.makeWidgetButton(key=f"{self.app_key_pri}_config_table", label="Table Columns Config"))
        layout.addLayout(makeLayoutAllROISetSameCelltype(self.widget_manager, 
                                                         key_button=self.app_key_pri, 
                                                         table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()))
        layout.addLayout(makeLayoutAllROICheckboxToggle(self.widget_manager, 
                                                        key_button=self.app_key_pri, 
                                                        table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()))
        layout.addLayout(makeLayoutROICheckIO(self.widget_manager, 
                                              key_button=self.app_key_pri))
        return layout

    # ROI Filter, threshold
    def makeLayoutComponentROIFilter(self):
        layout = QHBoxLayout()
        layout.addLayout(makeLayoutROIFilterThreshold(self.widget_manager, key_label=self.app_key_pri, key_lineedit=self.app_key_pri, dict_roi_threshold=self.config_manager.gui_defaults["ROI_THRESHOLDS"]))
        layout.addLayout(makeLayoutROIFilterButton(self.widget_manager, key_label=self.app_key_pri, key_button=self.app_key_pri))
        return layout
    

    """
    makeLayout Function; Section
    領域レベルの大Layout
    """
    # 左上
    def makeLayoutSectionLeftUpper(self):
        layout = QVBoxLayout()
        layout.addLayout(makeLayoutCanvasTracePlot(self.widget_manager, 
                                                   key_figure=self.app_key_pri, 
                                                   key_canvas=self.app_key_pri, 
                                                   key_app=self.app_key_pri), 
                        stretch=1)
        layout.addLayout(makeLayoutComponentLightPlotMode(self.widget_manager, self.config_manager))
        layout.addLayout(self.makeLayoutComponentEventFilePlot_TracePlotRange())
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
    def showSubWindowTableColumnConfig(self, key_app):
        config_window = TableColumnConfigWindow(self, 
                                                self.control_manager.table_controls[key_app].table_columns, 
                                                self.config_manager.gui_defaults)
        if config_window.exec_():
            self.loadFilePathsandInitialize()
            

    """
    bindFunc Function
    配置したwidgetに関数を紐づけ
    """
    def bindFuncFileLoadUI(self):        
        list_key = [f"{self.app_key_pri}_path_fall", f"{self.app_key_pri}_path_reftif", f"{self.app_key_pri}_path_cellpose"]
        list_filetype = ["mat", "tiff", "npy"]
        for key, filetype in zip(list_key, list_filetype):
            bindFuncLoadFileWidget(q_widget=self, q_button=self.widget_manager.dict_button[key], q_lineedit=self.widget_manager.dict_lineedit[key], filetype=filetype)

        self.widget_manager.dict_button["load_file"].clicked.connect(lambda: self.loadFilePathsandInitialize())
        bindFuncExit(q_window=self, q_button=self.widget_manager.dict_button["exit"])

    def bindFuncAllWidget(self):
        # ROICheck save load
        bindFuncROICheckIO(
            q_window=self, 
            q_lineedit=self.widget_manager.dict_lineedit[f"{self.app_key_pri}_path_fall"], 
            q_table=self.widget_manager.dict_table[f"{self.app_key_pri}"], 
            q_button_save=self.widget_manager.dict_button[f"{self.app_key_pri}_save_roicheck"], 
            q_button_load=self.widget_manager.dict_button[f"{self.app_key_pri}_load_roicheck"], 
            table_columns=self.config_manager.table_columns[self.app_key_pri].getColumns()
        )
        # Table Column Config
        self.widget_manager.dict_button[f"{self.app_key_pri}_config_table"].clicked.connect(
            lambda: self.showSubWindowTableColumnConfig(self.app_key_pri)
        )
        # Radiobutton BGImageType buttonChanged
        bindFuncRadiobuttonBGImageTypeChanged(
            q_buttongroup=self.widget_manager.dict_buttongroup[f"{self.app_key_pri}_bgimage_type"], 
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Radiobutton ROIDisplayType buttonChanged
        bindFuncRadiobuttonROIDisplayTypeChanged(
            q_buttongroup=self.widget_manager.dict_buttongroup[f"{self.app_key_pri}_roi_type"], 
            view_control=self.control_manager.view_controls[self.app_key_pri],
            table_control=self.control_manager.table_controls[self.app_key_pri],
        )
        # Set AllROI same celltype
        bindFuncButtonSetAllROISameCelltype(
            widget_manager=self.widget_manager,
            table_control=self.control_manager.table_controls[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
        )
        # Toggle AllROI checkbox
        bindFuncButtonToggleAllROICheckbox(
            widget_manager=self.widget_manager,
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
        bindFuncRadiobuttonCelltypeChanged(
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
        # View MousePressEvent
        bindFuncViewMousePressEvent(
            q_view=self.widget_manager.dict_view[self.app_key_pri],
            view_control=self.control_manager.view_controls[self.app_key_pri],
            table_control=self.control_manager.table_controls[self.app_key_pri],
        )