from __future__ import annotations
from typing import Any, Dict, Literal, List
from ..config.constants import AxisKeys, PlotColors, PlotLabels
from ..utils.data_utils import downSampleTrace
from ..visualization.canvas_visual import plotTraces, zoomXAxis, moveXAxis, moveToPlotCenter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.patches as patches
import numpy as np

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
        self.fs:                                  float = self.data_manager.getFs(self.key_app)
        self.plot_data_points:                      int = self.data_manager.getLengthOfData(self.key_app)
        self.downsample_threshold:                  int = 1000
        self.time_array:                       np.array = np.arange(self.plot_data_points) / self.fs
        self.plot_range:                 List[int, int] = [0, self.plot_data_points]
        self.downsampled_range:          List[int, int] = [0, 0]
        self.is_dragging:                          bool = False
        self.drag_start_x:                        float = None


        self.setupAxes()
        self.initializePlot()

    def setupAxes(self):
        axes_config = {
            'single': [(AxisKeys.TOP, 111)],
            'triple': [(AxisKeys.TOP, 311), (AxisKeys.MID, 312), (AxisKeys.BOT, 313)]
        }
        for key, pos in axes_config[self.ax_layout]:
            self.axes[key] = self.figure.add_subplot(pos)
        self.figure.tight_layout(pad=1.08, h_pad=2.0, w_pad=2.0)

    """
    Plot
    """
    def initializePlot(self):
        self.prepareTraceData()
        self.plotTracesMean()
        self.canvas.draw_idle()

    def updatePlot(self):
        self.prepareTraceData()
        self.plotTracesZoomed()
        self.plotTracesOverall()
        self.canvas.draw_idle()

    def prepareTraceData(self):
        self.updatePlotWidth()
        self.updateDownsampleThreshold()

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')
        self.full_traces = self.data_manager.getTracesOfSelectedROI(self.key_app, roi_selected_id)
        
        self.colors = {key: getattr(PlotColors, key.upper()) for key in ["F", "Fneu", "spks"]}
        self.labels = {key: getattr(PlotLabels, key.upper()) for key in ["F", "Fneu", "spks"]}
        
        self.y_max = max(np.max(trace) for trace in self.full_traces.values())
        ylim_config = self.config_manager.gui_defaults['CANVAS_SETTINGS']['YLIM']
        self.ylim = (self.y_max * ylim_config[0], self.y_max * ylim_config[1])

        # eventfileの取得と処理
        self.eventfile = self.data_manager.getEventfile(self.key_app)
        if self.eventfile is not None:
            self.full_traces['event'] = self.eventfile * self.y_max
            self.colors['event'] = PlotColors.EVENT
            self.labels['event'] = PlotLabels.EVENT

    def plotTraces(self, ax_key, traces, title_suffix, start, end, **kwargs):
        start_time = self.time_array[start]
        end_time = self.time_array[end - 1]
        num_ticks = self.config_manager.gui_defaults['CANVAS_SETTINGS']['PLOT_POINTS']
        xticks = np.linspace(0, len(next(iter(traces.values()))) - 1, num_ticks, dtype=int)
        xticklabels = np.linspace(start_time, end_time, num_ticks).astype(int)

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')

        default_kwargs = {
            'title'       : f'ROI {roi_selected_id}, Traces ({title_suffix})',
            'xlabel'      : 'Time (s)',
            'xticks'      : xticks,
            'xticklabels' : xticklabels,
            'xlim'        : (0, len(next(iter(traces.values()))) - 1),
            'ylim'        : self.ylim,
            'legend'      : (ax_key != AxisKeys.TOP),
            'loc'         : 'upper right'
        }

        default_kwargs.update(kwargs)

        plotTraces(self.axes[ax_key], 
                traces, 
                self.colors, 
                self.labels, 
                **default_kwargs)
    
    # top axis
    def plotTracesZoomed(self):
        start, end = self.plot_range
        traces = self.getDownsampledTraces(start, end)
        self.plotTraces(AxisKeys.TOP, traces, "Zoomed", start, end, legend=False)
    # middle axis
    def plotTracesOverall(self):
        traces = self.getDownsampledTraces(0, self.plot_data_points)
        self.plotTraces(AxisKeys.MID, traces, "Overall", 0, self.plot_data_points)
        self.updateDownsampledRange()
        self.drawZoomRectangle()
    def drawZoomRectangle(self):
        y_range = self.config_manager.gui_defaults["CANVAS_SETTINGS"]["YLIM_RECTANGLE"]
        y_min, y_max = self.y_max * y_range[0], self.y_max * y_range[1]
        start, end = self.downsampled_range
        rect = patches.Rectangle((start, y_min), end - start, y_max - y_min,
                                 fill=False, edgecolor=PlotColors.RECTANGLE, linewidth=2, zorder=2)
        self.axes[AxisKeys.MID].add_patch(rect)
    # bottom axis
    def plotTracesMean(self):
        traces = self.data_manager.getTraces(self.key_app)
        mean_traces = {key: np.mean(trace, axis=0) for key, trace in traces.items()}
        self.plotTraces(AxisKeys.BOT, mean_traces, "Average", 0, self.plot_data_points, ylim=None, title="Average Traces")

    def getDownsampledTraces(self, start, end):
        traces = {key: trace[start:end] for key, trace in self.full_traces.items()}
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and end - start > self.downsample_threshold:
            return {key: downSampleTrace(trace, self.downsample_threshold) for key, trace in traces.items()}
        return traces

    def updatePlotWidth(self):
        min_width_seconds = float(self.widget_manager.dict_lineedit[f"{self.key_app}_plot_min_width"].text())
        self.min_plot_width = int(min_width_seconds * self.fs)
    def updateDownsampleThreshold(self):
        self.downsample_threshold = int(self.widget_manager.dict_lineedit["light_plot_mode_threshold"].text())
    def updatePlotRange(self, ax, clicked_x):
        current_range = self.plot_range[1] - self.plot_range[0]
        new_center = int(clicked_x * self.plot_data_points / ax.get_xlim()[1])
        new_start = max(0, new_center - current_range // 2)
        new_end = min(self.plot_data_points, new_start + current_range)
        self.plot_range = [new_start, new_end]
        self.updatePlot()
    def updateDownsampledRange(self):
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and self.plot_data_points > self.downsample_threshold:
            downsample_factor = self.plot_data_points / (self.downsample_threshold * 4)
            self.downsampled_range = [
                int(self.plot_range[0] / downsample_factor),
                int(self.plot_range[1] / downsample_factor)
            ]
        else:
            self.downsampled_range = self.plot_range

    """
    event Functions
    """
    def onScroll(self, event, ax):
        if event.inaxes == ax:
            self.plot_range = zoomXAxis(event, ax, *self.plot_range, self.plot_data_points, self.min_plot_width)
            self.updatePlot()

    def onPress(self, event, ax):
        if event.inaxes == ax:
            self.is_dragging = True
            self.drag_start_x = event.xdata

    def onRelease(self, event, ax):
        self.is_dragging = False

    def onMotion(self, event, ax):
        if self.is_dragging and event.inaxes == ax and event.xdata:
            dx = self.drag_start_x - event.xdata
            self.drag_start_x = event.xdata
            self.plot_range = moveXAxis(ax, self.plot_range, self.plot_data_points, self.min_plot_width, dx)
            self.updatePlot()

    def onClick(self, event, ax):
        if event.inaxes == ax:
            self.plot_range = moveToPlotCenter(ax, event.xdata, self.plot_range, self.plot_data_points)
            self.updatePlot()