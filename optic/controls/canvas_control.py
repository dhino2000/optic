from __future__ import annotations
from typing import Any, Dict, Literal
from ..config.constants import AxisKeys, PlotColors, PlotLabels
from ..utils.data_utils import downSampleTrace
from ..visualization.canvas_visual import plotTraces, zoomXAxis
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
        self.plot_start:                            int = 0
        self.plot_end:                              int = self.plot_data_points
        self.downsampled_start:                     int = 0
        self.downsampled_end:                       int = 0
        self.is_dragging:                          bool = False
        self.drag_start_x:                        float = None


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
        self.prepareTraceData()
        self.plotTracesZoomed()
        self.plotTracesOverall()
        self.canvas.draw_idle()

    def prepareTraceData(self):
        self.updatePlotRange()
        self.updateDownsampleThreshold()

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')
        self.full_traces = self.data_manager.getTracesOfSelectedROI(self.key_app, roi_selected_id)
        
        self.colors = {"F": PlotColors.F, "Fneu": PlotColors.FNEU, "spks": PlotColors.SPKS}
        self.labels = {"F": PlotLabels.F, "Fneu": PlotLabels.FNEU, "spks": PlotLabels.SPKS}
        
        self.y_max = max(np.max(trace) for trace in self.full_traces.values())
        self.ylim = (-self.y_max * 0.1, self.y_max * 1.1)
    # top axis
    def plotTracesZoomed(self):
        trimmed_traces = {key: trace[self.plot_start:self.plot_end] for key, trace in self.full_traces.items()}
        current_points = self.plot_end - self.plot_start
        
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and current_points > self.downsample_threshold:
            traces = {key: downSampleTrace(trace, self.downsample_threshold) for key, trace in trimmed_traces.items()}
        else:
            traces = trimmed_traces

        start_time = self.time_array[self.plot_start]
        end_time = self.time_array[self.plot_end - 1]
        time_range = end_time - start_time

        tick_interval = max(1, int(time_range / 10))
        xticks = np.arange(start_time, end_time + 1, tick_interval)
        xticks_indices = np.linspace(0, len(next(iter(traces.values()))) - 1, len(xticks), dtype=int)

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')
        plotTraces(self.axes[AxisKeys.TOP], 
                   traces, 
                   self.colors, 
                   self.labels, 
                   title=f'ROI {roi_selected_id}, Traces (Zoomed)',
                   xlabel='Time (s)',
                   xticks=xticks_indices,
                   xticklabels=xticks.astype(int),
                   xlim=(0, len(next(iter(traces.values()))) - 1),
                   ylim=self.ylim)
    # middle axis
    def plotTracesOverall(self):
        original_length = len(next(iter(self.full_traces.values())))
        
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and original_length > self.downsample_threshold:
            traces = {key: downSampleTrace(trace, self.downsample_threshold) for key, trace in self.full_traces.items()}
            downsample_factor = original_length / (self.downsample_threshold * 4)
        else:
            traces = self.full_traces
            downsample_factor = 1

        total_downsampled_points = len(next(iter(traces.values())))

        # ダウンサンプル後の最も近い値を計算
        self.downsampled_start = int(self.plot_start / downsample_factor)
        self.downsampled_end = int(self.plot_end / downsample_factor)

        roi_selected_id = self.control_manager.getSharedAttr(self.key_app, 'roi_selected_id')

        # 正確な開始時刻と終了時刻を取得
        start_time = self.time_array[0]
        end_time = self.time_array[-1]

        # x軸の目盛りとラベルを計算
        num_ticks = 10  # 目盛りの数
        xticks = np.linspace(0, total_downsampled_points - 1, num_ticks).astype(int)
        xticklabels = np.linspace(start_time, end_time, num_ticks).astype(int)

        plotTraces(self.axes[AxisKeys.MID], 
                traces, 
                self.colors, 
                self.labels, 
                title=f'ROI {roi_selected_id}, Traces (Overall)',
                xlabel='Time (s)',
                xticks=xticks,
                xticklabels=xticklabels,
                xlim=(0, total_downsampled_points - 1),
                ylim=self.ylim)

        # ズーム範囲を示す紫の四角形を描画
        y_min = -self.y_max * 0.05
        y_max = self.y_max * 1.05

        rect = patches.Rectangle(
            (self.downsampled_start, y_min),  # (x, y)
            self.downsampled_end - self.downsampled_start,  # width
            y_max - y_min,  # height
            fill=False,
            edgecolor='purple',
            linewidth=2,
            zorder=2,
        )
        self.axes[AxisKeys.MID].add_patch(rect)
        
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
        self.updatePlot()
        self.canvas.draw_idle()


    def onPress(self, event):
        if event.inaxes == self.axes[AxisKeys.TOP]:
            self.is_dragging = True
            self.drag_start_x = event.xdata

    def onRelease(self, event):
        self.is_dragging = False

    def onMotion(self, event):
        if self.is_dragging and event.inaxes == self.axes[AxisKeys.TOP] and event.xdata:
            dx = self.drag_start_x - event.xdata
            self.drag_start_x = event.xdata

            move_points = int(dx * (self.plot_end - self.plot_start) / self.axes[AxisKeys.TOP].get_xlim()[1])
            self.plot_start = max(0, min(self.plot_start + move_points, self.plot_data_points - self.min_plot_width))
            self.plot_end = min(self.plot_data_points, max(self.plot_end + move_points, self.plot_start + self.min_plot_width))

            self.updatePlot()
            self.canvas.draw_idle()

    def bindEvents(self):
        self.canvas.mpl_connect('scroll_event', self.onScroll)
        self.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.mpl_connect('motion_notify_event', self.onMotion)

