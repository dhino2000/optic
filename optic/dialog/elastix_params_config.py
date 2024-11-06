from __future__ import annotations
from ..type_definitions import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from ..manager.widget_manager import WidgetManager
from ..manager.init_managers import initManagers
from ..gui.base_layouts import makeLayoutLineEditLabel

# Elastix Config
class ElastixParamsConfigDialog(QDialog):
    def __init__(
            self, 
            parent: QWidget, 
            elastix_params: Dict[str, Any],
            gui_defaults: GuiDefaults,
            ):
        super().__init__(parent)
        self.widget_manager = initManagers(WidgetManager())
        self.elastix_params = elastix_params

        window_settings = gui_defaults.get("WINDOW_SETTINGS_ELASTIX_CONFIG", {})
        self.setGeometry(
            window_settings.get("INIT_POSITION_X"),
            window_settings.get("INIT_POSITION_Y"),
            window_settings.get("WIDTH"),
            window_settings.get("HEIGHT")
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Elastix Configuration')
        layout = QVBoxLayout()
        layout.addLayout(self.makeLayoutElastixParamsAffine())
        layout.addLayout(self.makeLayoutElastixParamsBSpline())
        layout.addLayout(self.makeLayoutButton())
        self.setLayout(layout)

        # self.bindFuncAllWidget()

    def makeLayoutElastixParamsAffine(self):
        layout = QVBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="params_affine", label="Affine Paramaters", font_size=12, bold=True, italic=True, use_global_style=False))
        layout_params = QGridLayout()
        for i, (key_param, value_param) in enumerate(self.elastix_params["affine"].items()):
            key_label = f"{key_param}_affine"
            row = i % 7
            column = i // 7
            layout_params.addLayout(makeLayoutLineEditLabel(self.widget_manager, key_label, key_label, key_param, text_set=str(value_param)), row, column)
        layout.addLayout(layout_params)
        return layout
    
    def makeLayoutElastixParamsBSpline(self):
        layout = QVBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetLabel(key="params_bspline", label="B-Spline Paramaters", font_size=12, bold=True, italic=True, use_global_style=False))
        layout_params = QGridLayout()
        for i, (key_param, value_param) in enumerate(self.elastix_params["bspline"].items()):
            key_label = f"{key_param}_bspline"
            row = i % 7
            column = i // 7
            layout_params.addLayout(makeLayoutLineEditLabel(self.widget_manager, key_label, key_label, key_param, text_set=str(value_param)), row, column)
        layout.addLayout(layout_params)
        return layout
    
    def makeLayoutButton(self):
        layout = QHBoxLayout()
        layout.addWidget(self.widget_manager.makeWidgetButton(key="ok", label="OK"))
        layout.addWidget(self.widget_manager.makeWidgetButton(key="cancel", label="Cancel"))
        return layout

    def bindFuncAllWidget(self):
        pass