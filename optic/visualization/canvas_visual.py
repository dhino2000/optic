from typing import Dict, Any, Optional, List, Tuple
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

def plotTraces(ax, 
               traces      : Dict[str, np.ndarray], 
               colors      : Dict[str, str], 
               labels      : Dict[str, str], 
               title       : Optional[str] = None,
               xlabel      : Optional[str] = None,
               ylabel      : Optional[str] = None,
               xticks      : Optional[List[float]] = None,
               xticklabels : Optional[np.ndarray] = None,
               xlim        : Optional[Tuple[float, float]] = None,
               ylim        : Optional[Tuple[float, float]] = None,
               legend      : bool = True,):
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
        ax.legend()

def zoomXAxis(event, ax, plot_start: float, plot_end: float, total_points: float, min_width: int, zoom_factor: float = 1.5):
    current_range = plot_end - plot_start
    relative_x = event.xdata / ax.get_xlim()[1]  # イベントの相対的なx位置
    center = plot_start + int(relative_x * current_range)
    if event.button == 'up':  # ズームイン
        new_range = int(current_range / zoom_factor)
    else:  # ズームアウト
        new_range = int(current_range * zoom_factor)

    new_range = max(min_width, min(new_range, total_points))

    # 新しい範囲の半分
    half_range = new_range // 2

    # センターを基準に新しい開始位置と終了位置を計算
    new_start = center - half_range
    new_end = center + half_range

    # 範囲が全体のデータ範囲内に収まるように調整
    if new_start < 0:
        new_start = 0
        new_end = new_range
    elif new_end > total_points:
        new_end = total_points
        new_start = max(0, new_end - new_range)

    return int(new_start), int(new_end)