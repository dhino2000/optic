from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict

# Manager controls class
class ControlManager:
    def __init__(self):
        self.table_controls  : Dict[AppKeys, TableControl] = {}
        self.view_controls   : Dict[AppKeys, ViewControl] = {}
        self.canvas_controls : Dict[AppKeys, CanvasControl] = {}
        """
        Dictionary to hold attributes shared between controls
        The first level key is `app_key`: "pri", "sec", etc.
        The second level key is `key_attr`: "selected_roi", etc.
        """
        self.shared_attr = defaultdict(dict)

    def setSharedAttr(self, app_key: AppKeys, key_attr: str, value: Any) -> None:
        self.shared_attr[app_key][key_attr] = value

    def getSharedAttr(self, app_key: AppKeys, key_attr: str) -> Any:
        return self.shared_attr[app_key].get(key_attr)

    def getAllSharedAttrs(self, app_key: AppKeys) -> Dict[str, Any]:
        return self.shared_attr[app_key]