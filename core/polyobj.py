"""
Poly Object Wrapper - Allows both dict and attribute access for exported objects
"""

class PolyObject:
    """Wrapper that allows both dict-style and attribute-style access"""
    
    def __init__(self, data):
        if isinstance(data, dict):
            self.__dict__.update(data)
        else:
            raise TypeError("PolyObject must be initialized with a dict")
    
    def __getitem__(self, key):
        """Dict-style access: obj['key']"""
        return self.__dict__.get(key)
    
    def __setitem__(self, key, value):
        """Dict-style setting: obj['key'] = value"""
        self.__dict__[key] = value
    
    def __repr__(self):
        return f"PolyObject({self.__dict__})"
    
    def to_dict(self):
        """Convert back to dict"""
        return dict(self.__dict__)
