import sys
from pathlib import Path

EXTERNAL_DIR = Path(__file__).parent.resolve()

# Add external package directory to sys.path
FGW_PATH = EXTERNAL_DIR / "FGW-master" / "lib"
if str(FGW_PATH) not in sys.path:
    sys.path.append(str(FGW_PATH))