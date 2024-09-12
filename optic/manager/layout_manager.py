class LayoutManager:
    def __init__(self):
        self.dict_layout  = {}

    def setLayout(self, key, layout):
        self.dict_layout[key] = layout
        return self.dict_layout[key]

    def getLayout(self, key):
        return self.dict_layout.get(key)