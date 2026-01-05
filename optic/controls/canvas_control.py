from __future__ import annotations
from ..type_definitions import *
from ..config.constants import AxisKeys, PlotColors, PlotLabels, Extension
from ..utils.data_utils import downSampleTrace, extractEventOnsetIndices, extractEventAlignedData
from ..visualization.canvas_visual import plotTraces, zoomXAxis, moveXAxis, moveToPlotCenter, plotEventAlignedTrace
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.axes import Axes
import matplotlib.patches as patches
import numpy as np

class CanvasControl:
    def __init__(self, 
                 app_key         : str, 
                 figure          : Figure, 
                 canvas          : FigureCanvasQTAgg, 
                 data_manager    : DataManager, 
                 widget_manager  : WidgetManager, 
                 config_manager  : ConfigManager, 
                 control_manager : ControlManager, 
                 ax_layout       : Literal["triple", "single"] ='triple',
                 plot_trace      : bool = True):
        self.app_key                                    = app_key
        self.figure                                     = figure
        self.canvas                                     = canvas
        self.data_manager                               = data_manager
        self.widget_manager                             = widget_manager
        self.config_manager                             = config_manager
        self.control_manager                            = control_manager
        self.ax_layout                                  = ax_layout

        self.axes:                      Dict[str, Axes] = {}
        self.setupAxes()
        # F, Fneu, spks plotting
        if plot_trace:
            self.fs:                                  float = self.data_manager.getFs(self.app_key)
            self.plot_data_points:                      int = self.data_manager.getLengthOfData(self.app_key)
            self.downsample_threshold:                  int = 1000
            self.time_array:                       np.array = np.arange(self.plot_data_points) / self.fs
            self.plot_range:                 List[int, int] = [0, self.plot_data_points]
            self.downsampled_range:          List[int, int] = [0, 0]
            self.is_dragging:                          bool = False
            self.drag_start_x:                        float = None  
            self.plot_ffneu:                           bool = True
            self.plot_dff0:                            bool = True
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
    Data preparation
    """
    def preprocessTraceData(self, full_traces: Dict[str, np.ndarray[np.float32]]) -> Dict[str, np.ndarray[np.float32]]:
        fneu_factor = float(self.widget_manager.dict_lineedit[f"{self.app_key}_eventfile_prop_ffneu"].text()) # hardcoded !!!
        f0_percentile = float(self.widget_manager.dict_lineedit[f"{self.app_key}_eventfile_prop_dff0"].text()) # hardcoded !!!
        full_traces['F_event'] = full_traces['F']

        if self.plot_ffneu:
            f = full_traces['F_event'] - full_traces['Fneu'] * fneu_factor
            full_traces['F_event'] = f
        if self.plot_dff0 and f0_percentile > 0 and f0_percentile < 100:
            f = full_traces['F_event']
            f0 = np.percentile(f, f0_percentile)
            dff0 = (f - f0) / f0
            full_traces['F_event'] = dff0
        return full_traces

    def prepareTraceData(self):
        self.updatePlotWidth()
        self.updateDownsampleThreshold()

        roi_selected_id = self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')
        self.full_traces = self.data_manager.getTracesOfSelectedROI(self.app_key, roi_selected_id, n_channels=self.data_manager.getNChannels(self.app_key))
        
        if self.data_manager.getDataType(self.app_key) == Extension.MAT:
            if self.data_manager.getNChannels(self.app_key) == 1:
                self.colors = {key: getattr(PlotColors, key.upper()) for key in ["F", "Fneu", "spks"]}
                self.labels = {key: getattr(PlotLabels, key.upper()) for key in ["F", "Fneu", "spks"]}
            elif self.data_manager.getNChannels(self.app_key) == 2:
                self.colors = {key: getattr(PlotColors, key.upper()) for key in ["F", "Fneu", "spks", "F_chan2", "Fneu_chan2"]}
                self.labels = {key: getattr(PlotLabels, key.upper()) for key in ["F", "Fneu", "spks", "F_chan2", "Fneu_chan2"]}
        elif self.data_manager.getDataType(self.app_key) == Extension.HDF5:
            self.colors = {key: getattr(PlotColors, key.upper()) for key in ["F", "spks"]}
            self.labels = {key: getattr(PlotLabels, key.upper()) for key in ["F", "spks"]}
        elif self.data_manager.getDataType(self.app_key) == Extension.NPY:
            self.colors = {key: getattr(PlotColors, key.upper()) for key in ["F"]}
            self.labels = {key: getattr(PlotLabels, key.upper()) for key in ["F"]}

        self.y_max = max(np.max(trace) for trace in self.full_traces.values())
        ylim_config = self.config_manager.gui_defaults['CANVAS_SETTINGS']['YLIM']
        self.ylim = (self.y_max * ylim_config[0], self.y_max * ylim_config[1])

        # get and preprocess eventfile
        eventfile_name = self.control_manager.getSharedAttr(self.app_key, 'eventfile_name')
        try:
            self.eventfile = self.data_manager.getDictEventfile(self.app_key).get(eventfile_name)
        except AttributeError:
            self.eventfile = None
        if self.eventfile is not None:
            self.full_traces['event'] = self.eventfile * self.y_max
            # convert F trace to (F - Fneu) or DF/F0
            self.full_traces = self.preprocessTraceData(self.full_traces)
            self.colors['event'] = PlotColors.EVENT
            self.labels['event'] = PlotLabels.EVENT

        # get and preprocess cascade spike_prob and spike
        try:
            self.cascade_spike_prob = self.data_manager.getCascadeSpikeProbability(self.app_key)[roi_selected_id]
            self.cascade_spike_events = self.data_manager.getCascadeSpikeEvents(self.app_key)[roi_selected_id]
        except (AttributeError, TypeError):
            self.cascade_spike_prob = None
            self.cascade_spike_events = None
        if self.cascade_spike_prob is not None and self.cascade_spike_events is not None:
            self.full_traces['cascade_spike_prob'] = self.cascade_spike_prob
            self.full_traces['cascade_spike_events'] = self.cascade_spike_events
            self.colors['cascade_spike_prob'] = PlotColors.CASCADE_SPIKE_PROB
            self.colors['cascade_spike_events'] = PlotColors.CASCADE_SPIKE_EVENTS
            self.labels['cascade_spike_prob'] = PlotLabels.CASCADE_SPIKE_PROB
            self.labels['cascade_spike_events'] = PlotLabels.CASCADE_SPIKE_EVENTS

    def prepareEventAlignedData(self):
        if self.eventfile is None:
            return None, None

        event_indices = extractEventOnsetIndices(self.eventfile)
        
        range_str = self.widget_manager.dict_lineedit[f"{self.app_key}_eventfile_prop_range"].text() # hardcoded !!!
        pre_sec, post_sec = map(int, range_str.strip('()').split(','))
        pre_frames, post_frames = int(pre_sec * self.fs), int(post_sec * self.fs)

        event_segments = extractEventAlignedData(self.eventfile, event_indices, pre_frames, post_frames)
        trace_segments = extractEventAlignedData(self.full_traces['F_event'], event_indices, pre_frames, post_frames)

        self.event_segments = event_segments
        self.trace_segments = trace_segments

        return event_segments, trace_segments

    """
    Plot
    """
    def initializePlot(self):
        self.prepareTraceData()
        if self.ax_layout == 'triple':
            self.plotTracesMean()
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def updatePlotWithROISelect(self):
        self.prepareTraceData()
        self.plotTracesZoomed()
        if self.ax_layout == 'triple':
            self.plotTracesOverall()
            if self.widget_manager.dict_checkbox[f"{self.app_key}_plot_eventfile"].isChecked():
                self.plotEventAlignedTrace()
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def updatePlotWithMouseEvent(self):
        self.prepareTraceData()
        self.plotTracesZoomed()
        if self.ax_layout == 'triple':
            self.plotTracesOverall()
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plotTraces(self, ax_key, traces, title_suffix, start, end, **kwargs):
        start_time = self.time_array[start]
        end_time = self.time_array[end - 1]
        num_ticks = self.config_manager.gui_defaults['CANVAS_SETTINGS']['PLOT_POINTS']
        xticks = np.linspace(0, len(next(iter(traces.values()))) - 1, num_ticks, dtype=int)
        xticklabels = np.linspace(start_time, end_time, num_ticks).astype(int)

        roi_selected_id = self.control_manager.getSharedAttr(self.app_key, 'roi_selected_id')

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
        
    def plotEventAlignedTrace(self):
        event_segments, trace_segments = self.prepareEventAlignedData()
        if event_segments is None or trace_segments is None:
            return

        range_str = self.widget_manager.dict_lineedit[f"{self.app_key}_eventfile_prop_range"].text() # hardcoded !!!
        pre_sec, post_sec = map(float, range_str.strip('()').split(','))
        pre_frame, post_frame = pre_sec * self.fs, post_sec * self.fs

        mean_trace = np.mean(trace_segments, axis=0)

        traces = {
            'trace': np.array(trace_segments),
            'event': np.array(event_segments) * np.max(trace_segments),
            'mean': mean_trace
        }

        colors = {
            'trace': 'gray',
            'event': PlotColors.EVENT,
            'mean': 'red'
        }

        labels = {
            'trace': 'Individual Traces',
            'event': 'Event',
            'mean': 'Mean Trace'
        }

        xticks = [0, pre_frame, pre_frame + post_frame]
        xticklabels = [-pre_sec, 0, post_sec]

        plotEventAlignedTrace(
            self.axes[AxisKeys.BOT],
            traces,
            colors,
            labels,
            xlabel='Time (s)',
            title=self.getTitleOfEventAlignedTrace(),
            xticks=xticks,
            xticklabels=xticklabels,
            legend=False,
            alpha=0.3,
            idx_zero=pre_frame,
        )
    
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
        traces = self.data_manager.getTraces(self.app_key, n_channels=self.data_manager.getNChannels(self.app_key))
        mean_traces = {key: np.mean(trace, axis=0) for key, trace in traces.items()}
        self.plotTraces(AxisKeys.BOT, mean_traces, "Average", 0, self.plot_data_points, ylim=None, title="Average Traces")

    def getDownsampledTraces(self, start, end):
        traces = {key: trace[start:end] for key, trace in self.full_traces.items() if key != 'F_event'}
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and end - start > self.downsample_threshold:
            return {key: downSampleTrace(trace, self.downsample_threshold) for key, trace in traces.items()}
        return traces

    def updatePlotWidth(self):
        min_width_seconds = float(self.widget_manager.dict_lineedit[f"{self.app_key}_plot_min_width"].text())
        self.min_plot_width = int(min_width_seconds * self.fs)
    def updateDownsampleThreshold(self):
        self.downsample_threshold = int(self.widget_manager.dict_lineedit["light_plot_mode_threshold"].text())
    def updateDownsampledRange(self):
        if self.widget_manager.dict_checkbox["light_plot_mode"].isChecked() and self.plot_data_points > self.downsample_threshold and self.downsample_threshold >= 1:
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
            self.updatePlotWithMouseEvent()

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
            self.updatePlotWithMouseEvent()

    def onClick(self, event, ax):
        if event.inaxes == ax:
            self.plot_range = moveToPlotCenter(ax, event.xdata, self.plot_range, self.plot_data_points)
            self.updatePlotWithMouseEvent()

    """
    Processing
    """
    def calculateCorrelationTraceEvent(self):
        event_flatten = self.eventfile.flatten()
        trace_flatten = self.full_traces['F'].flatten()
        corr = np.corrcoef(event_flatten, trace_flatten)[0, 1]
        return corr
    
    def getTitleOfEventAlignedTrace(self):
        eventfile_name = self.control_manager.getSharedAttr(self.app_key, "eventfile_name")
        corr = self.calculateCorrelationTraceEvent()
        title = f"Event-aligned Data\n{eventfile_name}\n(r: {corr:.2f})"
        return title