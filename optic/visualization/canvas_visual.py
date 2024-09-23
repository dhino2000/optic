import numpy as np
from typing import Dict, Optional, Tuple, List
from matplotlib.axes import Axes

def plotTraces(ax          : Axes, 
               traces      : Dict[str, np.ndarray], 
               colors      : Dict[str, str], 
               labels      : Dict[str, str], 
               title       : Optional[str] = None,
               xlabel      : Optional[str] = None,
               ylabel      : Optional[str] = None,
               xticks      : Optional[np.ndarray] = None,
               xticklabels : Optional[np.ndarray] = None,
               xlim        : Optional[Tuple[float, float]] = None,
               ylim        : Optional[Tuple[float, float]] = None,
               legend      : bool = True,
               loc         : str = 'best'):
    ax.clear()
    
    for key, trace in traces.items():
        ax.plot(trace, color=colors[key], label=labels[key])
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xticks is not None and xticklabels is not None:
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if legend:
        ax.legend(loc=loc)

def zoomXAxis(event, 
              ax           : Axes,          
              plot_start   : float, 
              plot_end     : float, 
              total_points : float, 
              min_width    : int, 
              zoom_factor  : float = 1.5):
    current_range = plot_end - plot_start
    relative_x = event.xdata / ax.get_xlim()[1]  # イベントの相対的なx位置
    center = plot_start + int(relative_x * current_range)
    if event.button == 'up':  # ズームイン
        new_range = int(current_range / zoom_factor)
    else:  # ズームアウト
        new_range = int(current_range * zoom_factor)

    new_range = max(min_width, min(new_range, total_points))  # 最小幅を min_width に設定

    half_range = new_range // 2
    new_start = center - half_range
    new_end = center + half_range

    if new_start < 0:
        new_start = 0
        new_end = new_range
    elif new_end > total_points:
        new_end = total_points
        new_start = max(0, total_points - new_range)

    return new_start, new_end

def moveXAxis(ax: Axes,
              plot_range: List[int], 
              plot_data_points: int, 
              min_plot_width: int, 
              dx: float, 
              ) -> List[int]:
    current_range = plot_range[1] - plot_range[0]
    move_points = int(dx * current_range / ax.get_xlim()[1])
    
    new_start = max(0, plot_range[0] + move_points)
    new_end = min(plot_data_points, new_start + current_range)
    
    # 範囲の端に到達した場合、範囲を調整
    if new_start == 0:
        new_end = min(plot_data_points, current_range)
    elif new_end == plot_data_points:
        new_start = max(0, plot_data_points - current_range)
    
    return [new_start, new_end]

def moveToPlotCenter(ax: Axes, 
                     clicked_x: float, 
                     plot_range: List[int], 
                     plot_data_points: int) -> List[int]:
    current_range = plot_range[1] - plot_range[0]
    new_center = int(clicked_x * plot_data_points / ax.get_xlim()[1])
    new_start = max(0, new_center - current_range // 2)
    new_end = min(plot_data_points, new_start + current_range)
    return [new_start, new_end]