from typing import Dict, Any
import numpy as np

def plotTraces(ax, traces: Dict[str, np.ndarray], colors: Dict[str, str], labels: Dict[str, str], title: str=""):
    ax.clear()
    for key in traces.keys():
        ax.plot(traces[key], color=colors[key], label=labels[key])

    if title:
        ax.set_title(title)

    ax.legend()