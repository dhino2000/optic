from typing import Any, Dict, Literal
from ..config.constants import AxisKeys, PlotColors
from ..visualization.canvas_visual import plotTraces

class CanvasControl:
    def __init__(self, key_app, figure, canvas, data_manager, widget_manager, config_manager, control_manager, ax_layout='triple'):
        """
        Args:
            key_app (str): The key for the application.
            figure (Figure): The Figure object.
            canvas (FigureCanvasQTAgg): The FigureCanvasQTAgg object.
            data_manager (DataManager): The DataManager object.
            widget_manager (WidgetManager): The WidgetManager object.
            config_manager (ConfigManager): The ConfigManager object.
            control_manager (ControlManager): The ControlManager object.
            ax_layout (str): The layout of the axes.
        """
        self.key_app:                               str = key_app
        self.figure                                     = figure
        self.canvas                                     = canvas
        self.data_manager                               = data_manager
        self.widget_manager                             = widget_manager
        self.config_manager                             = config_manager
        self.control_manager                            = control_manager
        self.ax_layout:                             str = ax_layout

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

    def plotTraces(self, roi_selected_id: int):
        traces = self.data_manager.getTracesOfSelectedROI(self.key_app, roi_selected_id)
        colors = {"F": PlotColors.F, "Fneu": PlotColors.FNEU, "spks": PlotColors.SPKS}
        labels = {"F": "F", "Fneu": "Fneu", "spks": "spks"}
        plotTraces(self.axes["top"], traces, colors, labels, 'Traces')