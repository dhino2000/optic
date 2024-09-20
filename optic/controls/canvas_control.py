from __future__ import annotations
from typing import Any, Dict, Literal
from ..config.constants import AxisKeys, PlotColors, PlotLabels
from ..utils.data_utils import downSampleTrace
from ..visualization.canvas_visual import plotTraces
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..manager import ConfigManager, ControlManager, DataManager, WidgetManager

class CanvasControl:
    def __init__(self, 
                 key_app         : str, 
                 figure          : Figure, 
                 canvas          : FigureCanvasQTAgg, 
                 data_manager    : DataManager, 
                 widget_manager  : WidgetManager, 
                 config_manager  : ConfigManager, 
                 control_manager : ControlManager, 
                 ax_layout       : Literal["triple", "single"] ='triple'):
        self.key_app                                    = key_app
        self.figure                                     = figure
        self.canvas                                     = canvas
        self.data_manager                               = data_manager
        self.widget_manager                             = widget_manager
        self.config_manager                             = config_manager
        self.control_manager                            = control_manager
        self.ax_layout                                  = ax_layout

        self.axes:                       Dict[str, Any] = {}

        self.setupAxes()

    def setupAxes(self):
        if self.ax_layout == 'single':
            self.axes[AxisKeys.TOP] = self.figure.add_subplot(111)
        elif self.ax_layout == 'triple':
            for i, key_ax in enumerate([AxisKeys.TOP, AxisKeys.MID, AxisKeys.BOT]):
                self.axes[key_ax] = self.figure.add_subplot(3, 1, i+1)
        
        self.figure.subplots_adjust(top=0.95, bottom=0.1, right=0.9, left=0.1, hspace=0.4)

    def updatePlot(self):
        self.canvas.draw()

    def plotTraces(self, roi_selected_id: int, length_plot:int = 1000):
        traces = self.data_manager.getTracesOfSelectedROI(self.key_app, roi_selected_id)
        if self.widget_manager.dict_checkbox[f"light_plot_mode"].isChecked():
            traces = {key: downSampleTrace(value, length_plot) for key, value in traces.items()}
        colors = {"F": PlotColors.F, "Fneu": PlotColors.FNEU, "spks": PlotColors.SPKS}
        labels = {"F": PlotLabels.F, "Fneu": PlotLabels.FNEU, "spks": PlotLabels.SPKS}
        plotTraces(self.axes["top"], traces, colors, labels, 'Traces')