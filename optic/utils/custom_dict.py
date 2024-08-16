# 何層下でも一気に定義する事が可能なdict
class CustomDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locked = False

    def __missing__(self, key):
        if self.locked:
            raise KeyError(key)
        self[key] = CustomDict()
        return self[key]

    # lockで後からの追加を防ぐ
    def lock(self):
        self.locked = True
        for value in self.values():
            if isinstance(value, CustomDict):
                value.lock()

    def unlock(self):
        self.locked = False
        for value in self.values():
            if isinstance(value, CustomDict):
                value.unlock()

def defaultdictRecursive():
    return CustomDict()