import sys
from pathlib import Path

EXTERNAL_DIR = Path(__file__).parent.resolve()

# Add external package directory to sys.path
FGW_PATH = EXTERNAL_DIR / "FGW-master" / "lib"
SUITE2P_PATH = EXTERNAL_DIR / "suite2p"

if str(FGW_PATH) not in sys.path:
    sys.path.append(str(FGW_PATH))
if str(SUITE2P_PATH) not in sys.path:
    sys.path.append(str(SUITE2P_PATH))