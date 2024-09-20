from typing import Dict, Any
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

def plotTraces(ax, traces: Dict[str, np.ndarray], colors: Dict[str, str], labels: Dict[str, str], title: str = ""):
    ax.clear()
    for key in traces.keys():
        ax.plot(traces[key], color=colors[key], label=labels[key])

    if title:
        ax.set_title(title)

    ax.legend()

def zoomXAxis(event, ax, canvas: FigureCanvasQTAgg, min_width: int, max_width: int, scale_factor: float = 1.5):
    if event.inaxes != ax:
        return

    current_xlim = ax.get_xlim()
    xdata = event.xdata

    # scrool up / down
    if event.button == 'up':
        scale_factor = 1 / scale_factor
    elif event.button == 'down':
        scale_factor = scale_factor
    else:
        return

    current_width = current_xlim[1] - current_xlim[0]
    new_width = current_width * scale_factor

    new_width = np.clip(new_width, min_width, max_width)

    relx = (current_xlim[1] - xdata) / current_width
    
    new_xlim = [xdata - new_width * (1-relx), xdata + new_width * relx]
    
    ax.set_xlim(new_xlim)
    canvas.draw_idle()