from collections import defaultdict

# Manager controls class
class ControlManager:
    def __init__(self):
        self.table_controls = {}
        self.view_controls = {}
        """
        Dictionary to hold attributes shared between controls
        The first level key is `app_key`: "pri", "sec", etc.
        The second level key is `attr_key`: "selected_roi", etc.
        """
        self.shared_attr = defaultdict(dict)

    def setSharedAttr(self, app_key: str, attr_key: str, value):
        self.shared_attr[app_key][attr_key] = value

    def getSharedAttr(self, app_key: str, attr_key: str):
        return self.shared_attr[app_key].get(attr_key)

    def getAllSharedAttrs(self, app_key: str):
        return self.shared_attr[app_key]