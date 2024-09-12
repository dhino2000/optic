class KeyFunctionMap:
    def __init__(self, key_function_config):
        self._key_function_map = key_function_config
 
    def getFunction(self, key):
        return self._key_function_map.get(key)

    def getAllMappings(self):
        return self._key_function_map.copy()