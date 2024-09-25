from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict

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

    def setSharedAttr(self, key_app: str, key_attr: str, value: Any) -> None:
        self.shared_attr[key_app][key_attr] = value

    def getSharedAttr(self, key_app: str, key_attr: str) -> Any:
        return self.shared_attr[key_app].get(key_attr)

    def getAllSharedAttrs(self, key_app: str) -> Dict[str, Any]:
        return self.shared_attr[key_app]