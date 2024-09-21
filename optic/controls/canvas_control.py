from __future__ import annotations
from typing import Any, Dict, Literal
from ..config.constants import AxisKeys, PlotColors, PlotLabels
from ..utils.data_utils import downSampleTrace
from ..visualization.canvas_visual import plotTraces, zoomXAxis
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
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
        self.plot_start:                            int = 0
        self.plot_end:                              int = self.plot_data_points

        self.setupAxes()
        self.bindEvents()

    def setupAxes(self):
        if self.ax_layout == 'single':
            self.axes[AxisKeys.TOP] = self.figure.add_subplot(111)
        elif self.ax_layout == 'triple':
            for i, key_ax in enumerate([AxisKeys.TOP, AxisKeys.MID, AxisKeys.BOT]):
                self.axes[key_ax] = self.figure.add_subplot(3, 1, i+1)
        
        self.figure.subplots_adjust(top=0.95, bottom=0.1, right=0.9, left=0.1, hspace=0.4)

    # Plot
    def updatePlot(self):
        self.plotTraces()

        self.canvas.draw_idle()

    def plotTraces(self):
        self.updatePlotRange()
        self.updateDownsampleThreshold()

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')
        full_traces = self.data_manager.getTracesOfSelectedROI(self.key_app, roi_selected_id)
        
        # データのトリミングとダウンサンプリング
        trimmed_traces = {key: trace[self.plot_start:self.plot_end] for key, trace in full_traces.items()}
        current_points = self.plot_end - self.plot_start
        
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and current_points > self.downsample_threshold:
            traces = {key: downSampleTrace(trace, self.downsample_threshold) for key, trace in trimmed_traces.items()}
            downsampling_factor = current_points / self.downsample_threshold
        else:
            traces = trimmed_traces
            downsampling_factor = 1

        colors = {"F": PlotColors.F, "Fneu": PlotColors.FNEU, "spks": PlotColors.SPKS}
        labels = {"F": PlotLabels.F, "Fneu": PlotLabels.FNEU, "spks": PlotLabels.SPKS}
        
        # 表示範囲の時間を計算
        start_time = self.time_array[self.plot_start]
        end_time = self.time_array[self.plot_end - 1]
        time_range = end_time - start_time

        # x軸の目盛りを1秒刻みで計算
        tick_interval = max(1, int(time_range / 10))  # 最小1秒間隔、最大10個程度の目盛り
        xticks = np.arange(start_time, end_time + 1, tick_interval)
        
        # ダウンサンプリングに合わせてxticksを調整
        xticks_indices = np.linspace(0, len(next(iter(traces.values()))) - 1, len(xticks), dtype=int)

        # yの範囲を計算
        y_max = max(np.max(trace) for trace in full_traces.values())
        ylim = (-y_max * 0.1, y_max * 1.1)

        plotTraces(self.axes[AxisKeys.TOP], 
                   traces, 
                   colors, 
                   labels, 
                   title=f'ROI {roi_selected_id}, Traces',
                   xlabel='Time (s)',
                   xticks=xticks_indices,
                   xticklabels=xticks.astype(int),
                   xlim=(0, len(next(iter(traces.values()))) - 1),
                   ylim=ylim)
        
    def updatePlotRange(self):
        min_width_seconds = float(self.widget_manager.dict_lineedit[f"{self.key_app}_plot_min_width"].text())
        self.min_plot_width = int(min_width_seconds * self.fs)
    def updateDownsampleThreshold(self):
        base_threshold = int(self.widget_manager.dict_lineedit["light_plot_mode_threshold"].text())
        self.downsample_threshold = base_threshold

    # Mouse Event
    def onScroll(self, event):
        if event.inaxes != self.axes[AxisKeys.TOP]:
            return

        self.plot_start, self.plot_end = zoomXAxis(
            event=event,
            ax=self.axes[AxisKeys.TOP],
            plot_start=self.plot_start,
            plot_end=self.plot_end,
            total_points=self.plot_data_points,
            min_width=self.min_plot_width
        )
        self.plotTraces()
        self.canvas.draw_idle()

    def bindEvents(self):
        self.canvas.mpl_connect('scroll_event', self.onScroll)
        

