from __future__ import annotations
from ..type_definitions import *
import random

# generate random color for ROI
def generateRandomColor(
    r_min :int = 100,
    r_max :int = 255,
    g_min :int = 100,
    g_max :int = 255,
    b_min :int = 100,
    b_max :int = 255
) -> Tuple[int, int, int]:
    return (random.randint(r_min, r_max), random.randint(g_min, g_max), random.randint(b_min, b_max))