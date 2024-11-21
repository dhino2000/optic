from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..controls.canvas_control import CanvasControl
from ..gui.processing_roi_layouts import makeLayoutROIMatching
from ..config.constants import OTParams, AxisKeys, ROIMatchingTest_Config
import numpy as np

# ROI Matching Test
class ROIMatchingTestDialog(QDialog):
    def __init__(
            self, 
            parent: QWidget,
            gui_defaults: GuiDefaults,
            data_manager: DataManager,
            config_manager: ConfigManager,
            control_manager: ControlManager,
            app_key_pri: AppKeys,
            app_key_sec: AppKeys,
            ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.control_manager = control_manager
        self.app_key_pri = app_key_pri
        self.app_key_sec = app_key_sec

        window_settings = gui_defaults.get("WINDOW_SETTINGS_ROI_MATCHING_TEST", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

        # data preparation
        self.getROIIndexes()
        self.getMedCoords()
        self.getROIParams()

        # canvas update
        self.updateCanvas()

    def initUI(self):
        self.setWindowTitle('ROI Matching Test')
        layout = QVBoxLayout()
        self.widget_manager.makeWidgetFigure("roi_matching")
        layout.addWidget(self.widget_manager.makeWidgetFigureCanvas("roi_matching", self.widget_manager.dict_figure["roi_matching"]), stretch=1)

        layout.addLayout(makeLayoutROIMatching(
            self.widget_manager,
            "roi_matching",
            "ot_method",
            "fgwd_alpha",
            "wd_exp",
            "fgwd_alpha",
            "wd_exp",
            "ot_method",
            "ot_run",
        ))
        self.setLayout(layout)

        self.setupControls()
        self.bindFuncAllWidget()

    def setupControls(self):
        self.canvas_control = CanvasControl(
            app_key="roi_matching",
            figure=self.widget_manager.dict_figure["roi_matching"], 
            canvas=self.widget_manager.dict_canvas["roi_matching"], 
            data_manager=self.data_manager, 
            widget_manager=self.widget_manager,
            config_manager=self.config_manager,
            control_manager=self.control_manager,
            ax_layout="single",
            plot_trace=False
        )

    # get display ROI indexes
    def getROIIndexes(self):
        self.idx_roi_pri = [key for key, value in self.control_manager.getSharedAttr(self.app_key_pri, "roi_display").items() if value]
        self.idx_roi_sec = [key for key, value in self.control_manager.getSharedAttr(self.app_key_sec, "roi_display").items() if value]

    # get med coordinates of ROIs
    def getMedCoords(self):
        self.med_coords_pri = np.array([self.data_manager.getDictROICoords(self.app_key_pri)[idx]["med"] for idx in self.idx_roi_pri])
        self.med_coords_sec = np.array([self.data_manager.getDictROICoords(self.app_key_sec)[idx]["med"] for idx in self.idx_roi_sec])

    # get ROI shape parameters
    def getROIParams(self):
        key_params = OTParams.SHAPE
        try:
            self.roi_params_pri = np.concatenate([[self.data_manager.getStat(self.app_key_pri)[cellid][key] for cellid in self.idx_roi_pri] for key in key_params], axis=1)
            self.roi_params_sec = np.concatenate([[self.data_manager.getStat(self.app_key_sec)[cellid][key] for cellid in self.idx_roi_sec] for key in key_params], axis=1)
        except np.AxisError:
            pass

    def updateCanvas(self):
        ax = self.canvas_control.axes[AxisKeys.TOP]
        xsize, ysize = self.data_manager.getImageSize(self.app_key_pri)
        ax.clear()

        color_pri  = ROIMatchingTest_Config.COLOR_PRI
        color_sec  = ROIMatchingTest_Config.COLOR_SEC
        color_pair = ROIMatchingTest_Config.COLOR_PAIR
        alpha      = ROIMatchingTest_Config.ALPHA
        fontsize   = ROIMatchingTest_Config.FONTSIZE
        label_pri  = ROIMatchingTest_Config.LABEL_PRI
        label_sec  = ROIMatchingTest_Config.LABEL_SEC

        try:
            ax.scatter(self.med_coords_pri[:, 0], self.med_coords_pri[:, 1], c=color_pri, label=label_pri, alpha=alpha)
            ax.scatter(self.med_coords_sec[:, 0], self.med_coords_sec[:, 1], c=color_sec, label=label_sec, alpha=alpha)
            for idx, med in zip(self.idx_roi_pri, self.med_coords_pri):
                ax.text(med[0], med[1], idx, fontsize=fontsize, color=color_pri)
            for idx, med in zip(self.idx_roi_sec, self.med_coords_sec):
                ax.text(med[0], med[1], idx, fontsize=fontsize, color=color_sec)

            ax.set_xlim((0, xsize))
            ax.set_ylim((0, ysize))
        except IndexError:
            pass

    def bindFuncAllWidget(self):
        pass