class Context:

    def __init__(self):
        self.variables = {}
        self._functions = {}          # name -> callable
        self._object_store = {}       # int handle -> object
        self._next_handle = 1

    # ── Values ────────────────────────────────────────────────────────────

    def set(self, key, value):
        self.variables[key] = value

    def get(self, key, default=None):
        return self.variables.get(key, default)

    def all(self):
        return self.variables

    # ── Functions ─────────────────────────────────────────────────────────

    def export_function(self, name, func, language="python",
                        param_types=None, return_type=None):
        """Register a Python callable in the bridge function table."""
        self._functions[name] = func
        self.variables[name] = func   # also visible as a plain variable

    def has_function(self, name):
        return name in self._functions

    def get_function(self, name):
        return self._functions.get(name)

    def call(self, name, *args):
        if name not in self._functions:
            raise NameError(f"[Bridge] Function '{name}' is not registered.")
        return self._functions[name](*args)

    # ── Object handle store ───────────────────────────────────────────────

    def store_object(self, obj) -> int:
        handle = self._next_handle
        self._next_handle += 1
        self._object_store[handle] = obj
        return handle

    def load_object(self, handle: int):
        if handle not in self._object_store:
            raise KeyError(f"[Bridge] No object for handle {handle}")
        return self._object_store[handle]

    def delete_object(self, handle: int):
        self._object_store.pop(handle, None)
