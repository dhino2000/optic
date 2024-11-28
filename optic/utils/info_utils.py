from __future__ import annotations
from ..type_definitions import *

# "(0, 100)" -> 0, 100
def extractRangeValues(input_string: str) -> Optional[Tuple[float, float]]:
    cleaned_string = input_string.strip().strip('()')
    parts = cleaned_string.split(',')
    
    if len(parts) != 2:
        return None
    
    try:
        start = float(parts[0].strip())
        end = float(parts[1].strip())
        
        return start, end
    except ValueError:
        return None
    
# get thresholds of ROI filter
def getThresholdsOfROIFilter(dict_q_lineedit: Dict[str, QLineEdit]) -> Dict[str, Tuple[float, float]]:
    thresholds = {}
    for key, q_lineedit in dict_q_lineedit.items():
        thresholds[key] = extractRangeValues(q_lineedit.text())
    return thresholds