from collections import defaultdict
from typing import Any, Dict
from ..controls.table_control import TableControl
from ..controls.view_control import ViewControl
from ..controls.canvas_control import CanvasControl

# Manager controls class
class ControlManager:
    def __init__(self):
        self.table_controls  : Dict[str, TableControl] = {}
        self.view_controls   : Dict[str, ViewControl] = {}
        self.canvas_controls : Dict[str, CanvasControl] = {}
        """
        Dictionary to hold attributes shared between controls
        The first level key is `key_app`: "pri", "sec", etc.
        The second level key is `key_attr`: "selected_roi", etc.
        """
        self.shared_attr = defaultdict(dict)

    def setSharedAttr(self, key_app: str, key_attr: str, value: Any):
        self.shared_attr[key_app][key_attr] = value

    def getSharedAttr(self, key_app: str, key_attr: str):
        return self.shared_attr[key_app].get(key_attr)

    def getAllSharedAttrs(self, key_app: str):
        return self.shared_attr[key_app]