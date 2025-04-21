from __future__ import annotations
from ..type_definitions import *
from collections import defaultdict

# Manager controls class
class ControlManager:
    def __init__(self):
        self.table_controls  : Dict[Union[AppKeys, str], TableControl] = {}
        self.view_controls   : Dict[Union[AppKeys, str], ViewControl] = {}
        self.canvas_controls : Dict[Union[AppKeys, str], CanvasControl] = {}
        """
        Dictionary to hold attributes shared between controls
        The first level key is `app_key`: "pri", "sec", etc.
        The second level key is `key_attr`: "selected_roi", etc.
        """
        self.shared_attr = defaultdict(dict)

    # set value of shared_attr
    def setSharedAttr(self, app_key: Union[AppKeys, str], key_attr: str, value: Any) -> None:
        self.shared_attr[app_key][key_attr] = value

    # set value of a dict in shared_attr
    def setSharedAttrDictValue(self, app_key: Union[AppKeys, str], key_attr: str, key_dict: str, value: Any) -> None:
        self.shared_attr[app_key][key_attr][key_dict] = value

    def getSharedAttr(self, app_key: Union[AppKeys, str], key_attr: str) -> Any:
        return self.shared_attr[app_key].get(key_attr)

    def getAllSharedAttrs(self, app_key: Union[AppKeys, str]) -> Dict[str, Any]:
        return self.shared_attr[app_key]
    
    # intialize controls
    def initializeSkipROITypes(self, app_key: Union[AppKeys, str], table_columns: TableColumns) -> None:
        skip_items = [key for key, value in table_columns.getColumns().items() if value['type'] in ['celltype', 'checkbox']]
        self.setSharedAttr(app_key, "skip_roi_types", {skip_item: False for skip_item in skip_items})