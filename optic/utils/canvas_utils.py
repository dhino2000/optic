from __future__ import annotations
from ..type_definitions import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

# export figure
def exportFigure(
    figure: Figure,
    path_dst: str,
    dpi: int = 300
) -> None:
    figure.savefig(path_dst, dpi=dpi)

# export Axes
def exportAxes(
    axes: Axes,
    path_dst: str,
    dpi: int = 300
) -> None:
    axes.figure.savefig(path_dst, dpi=dpi)