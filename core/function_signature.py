from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class Parameter:
    name: str
    type_hint: Optional[str] = None
    default: Optional[Any] = None
    is_variadic: bool = False

    def __repr__(self):
        default_str = f' = {self.default}' if self.default is not None else ''
        type_str = f': {self.type_hint}' if self.type_hint else ''
        return f'{self.name}{type_str}{default_str}'

@dataclass
class FunctionSignature:
    name: str
    language: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    scope: str = 'global'
    callable: Optional[Callable] = None
    doc: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        params = ', '.join((str(p) for p in self.parameters))
        return_str = f' -> {self.return_type}' if self.return_type else ''
        return f'{self.name}({params}){return_str} [{self.language}]'

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'language': self.language, 'parameters': [{'name': p.name, 'type': p.type_hint, 'default': p.default, 'variadic': p.is_variadic} for p in self.parameters], 'return_type': self.return_type, 'scope': self.scope, 'doc': self.doc}

    def arity(self) -> int:
        return sum((1 for p in self.parameters if p.default is None))

    def max_arity(self) -> int:
        return len(self.parameters)

class FunctionSignatureBuilder:

    def __init__(self, name: str, language: str):
        self.name = name
        self.language = language
        self.parameters: List[Parameter] = []
        self.return_type: Optional[str] = None
        self.scope = 'global'
        self.callable: Optional[Callable] = None
        self.doc: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def add_parameter(self, name: str, type_hint: Optional[str]=None, default: Optional[Any]=None, variadic: bool=False) -> 'FunctionSignatureBuilder':
        self.parameters.append(Parameter(name, type_hint, default, variadic))
        return self

    def set_return_type(self, return_type: str) -> 'FunctionSignatureBuilder':
        self.return_type = return_type
        return self

    def set_scope(self, scope: str) -> 'FunctionSignatureBuilder':
        self.scope = scope
        return self

    def set_callable(self, callable_obj: Callable) -> 'FunctionSignatureBuilder':
        self.callable = callable_obj
        return self

    def set_doc(self, doc: str) -> 'FunctionSignatureBuilder':
        self.doc = doc
        return self

    def add_metadata(self, key: str, value: Any) -> 'FunctionSignatureBuilder':
        self.metadata[key] = value
        return self

    def build(self) -> FunctionSignature:
        return FunctionSignature(name=self.name, language=self.language, parameters=self.parameters, return_type=self.return_type, scope=self.scope, callable=self.callable, doc=self.doc, metadata=self.metadata)
