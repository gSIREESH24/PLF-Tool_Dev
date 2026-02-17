class Context:
    def __init__(self):
        self.variables = {}

    def set(self, key, value):
        self.variables[key] = value

    def get(self, key):
        return self.variables.get(key)

    def all(self):
        return self.variables
