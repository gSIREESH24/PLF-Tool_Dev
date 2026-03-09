"""
Function Signature - Metadata about functions for cross-language calls
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Parameter:
    """Represents a function parameter"""
    name: str
    type_hint: Optional[str] = None
    default: Optional[Any] = None
    is_variadic: bool = False
    
    def __repr__(self):
        default_str = f" = {self.default}" if self.default is not None else ""
        type_str = f": {self.type_hint}" if self.type_hint else ""
        return f"{self.name}{type_str}{default_str}"


@dataclass
class FunctionSignature:
    """
    Metadata about a function for cross-language calls.
    
    Attributes:
        name: Function name
        language: Source language (python, javascript, c)
        parameters: List of Parameter objects
        return_type: Expected return type (optional)
        scope: 'global' or 'local'
        callable: The actual function object
        doc: Optional documentation string
    """
    name: str
    language: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    scope: str = "global"  # 'global' or 'local'
    callable: Optional[Callable] = None
    doc: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        params = ", ".join(str(p) for p in self.parameters)
        return_str = f" -> {self.return_type}" if self.return_type else ""
        return f"{self.name}({params}){return_str} [{self.language}]"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signature to dictionary for serialization"""
        return {
            "name": self.name,
            "language": self.language,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type_hint,
                    "default": p.default,
                    "variadic": p.is_variadic
                }
                for p in self.parameters
            ],
            "return_type": self.return_type,
            "scope": self.scope,
            "doc": self.doc
        }
    
    def arity(self) -> int:
        """Return number of required parameters (non-default)"""
        return sum(1 for p in self.parameters if p.default is None)
    
    def max_arity(self) -> int:
        """Return total number of parameters"""
        return len(self.parameters)


class FunctionSignatureBuilder:
    """Helper class to build function signatures"""
    
    def __init__(self, name: str, language: str):
        self.name = name
        self.language = language
        self.parameters: List[Parameter] = []
        self.return_type: Optional[str] = None
        self.scope = "global"
        self.callable: Optional[Callable] = None
        self.doc: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def add_parameter(self, name: str, type_hint: Optional[str] = None, 
                      default: Optional[Any] = None, variadic: bool = False) -> "FunctionSignatureBuilder":
        """Add a parameter to the function signature"""
        self.parameters.append(
            Parameter(name, type_hint, default, variadic)
        )
        return self
    
    def set_return_type(self, return_type: str) -> "FunctionSignatureBuilder":
        """Set the return type"""
        self.return_type = return_type
        return self
    
    def set_scope(self, scope: str) -> "FunctionSignatureBuilder":
        """Set the scope (global or local)"""
        self.scope = scope
        return self
    
    def set_callable(self, callable_obj: Callable) -> "FunctionSignatureBuilder":
        """Set the callable function object"""
        self.callable = callable_obj
        return self
    
    def set_doc(self, doc: str) -> "FunctionSignatureBuilder":
        """Set documentation"""
        self.doc = doc
        return self
    
    def add_metadata(self, key: str, value: Any) -> "FunctionSignatureBuilder":
        """Add custom metadata"""
        self.metadata[key] = value
        return self
    
    def build(self) -> FunctionSignature:
        """Build and return the FunctionSignature"""
        return FunctionSignature(
            name=self.name,
            language=self.language,
            parameters=self.parameters,
            return_type=self.return_type,
            scope=self.scope,
            callable=self.callable,
            doc=self.doc,
            metadata=self.metadata
        )
