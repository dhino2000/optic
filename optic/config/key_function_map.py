from __future__ import annotations
from ..type_definitions import *

class KeyFunctionMap:
    def __init__(self, key_function_config: Dict[Qt.Key, Any]):
        self._key_function_map = key_function_config
 
    def getFunction(self, key: Qt.Key) -> Any:
        return self._key_function_map.get(key)

    def getAllMappings(self):
        return self._key_function_map.copy()