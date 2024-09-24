from typing import Tuple, Optional

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