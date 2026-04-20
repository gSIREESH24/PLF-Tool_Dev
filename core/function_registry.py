from typing import Any, Callable, Dict, List, Optional
from core.function_signature import FunctionSignature
import json

class FunctionNotFoundError(Exception):
    pass

class InvalidFunctionCallError(Exception):
    pass

class FunctionRegistry:

    def __init__(self):
        self.global_functions: Dict[str, FunctionSignature] = {}
        self.local_functions: Dict[str, Dict[str, FunctionSignature]] = {}
        self.adapters: Dict[str, Any] = {}
        self.call_history: List[Dict[str, Any]] = []
        self.marshallers: Dict[tuple, Callable] = {}

    def register(self, signature: FunctionSignature, scope: str='global', block_id: Optional[str]=None) -> None:
        if scope == 'global':
            self.global_functions[signature.name] = signature
        elif scope == 'local' and block_id:
            if block_id not in self.local_functions:
                self.local_functions[block_id] = {}
            self.local_functions[block_id][signature.name] = signature
        else:
            raise ValueError(f'Invalid scope: {scope}')

    def get(self, name: str, block_id: Optional[str]=None) -> FunctionSignature:
        if block_id and block_id in self.local_functions:
            if name in self.local_functions[block_id]:
                return self.local_functions[block_id][name]
        if name in self.global_functions:
            return self.global_functions[name]
        raise FunctionNotFoundError(f'Function not found: {name}')

    def call(self, name: str, args: List[Any], kwargs: Dict[str, Any]=None, block_id: Optional[str]=None) -> Any:
        kwargs = kwargs or {}
        try:
            signature = self.get(name, block_id)
        except FunctionNotFoundError as e:
            raise FunctionNotFoundError(f'Function not found: {name}\nAvailable functions: {self.list_functions()}') from e
        self._validate_arguments(signature, args, kwargs)
        try:
            if signature.callable:
                result = signature.callable(*args, **kwargs)
            else:
                try:
                    from languages.function_adapters import get_adapter
                    adapter = get_adapter(signature.language)
                    code = signature.metadata.get('code', '')
                    if signature.language == 'javascript':
                        result = adapter.call_js_function(signature.name, args, js_code=code)
                    elif signature.language == 'c':
                        result = adapter.call_c_function(signature.name, args, c_code=code)
                    elif signature.language == 'cpp':
                        result = adapter.call_cpp_function(signature.name, args, cpp_code=code)
                    elif signature.language == 'java':
                        result = adapter.call_java_function(signature.name, args, java_code=code)
                    else:
                        raise NotImplementedError(f"Adapter error for {signature.language}")
                except Exception as ex:
                    raise InvalidFunctionCallError(f"Adapter execution failed: {ex}")
            self.call_history.append({'function': name, 'language': signature.language, 'args': str(args), 'kwargs': str(kwargs), 'result': str(result), 'success': True})
            return result
        except Exception as e:
            self.call_history.append({'function': name, 'language': signature.language, 'args': str(args), 'kwargs': str(kwargs), 'error': str(e), 'success': False})
            raise InvalidFunctionCallError(f"Error calling function '{name}': {str(e)}") from e

    def register_marshaller(self, from_lang: str, to_lang: str, marshaller: Callable[[Any], Any]) -> None:
        self.marshallers[from_lang, to_lang] = marshaller

    def marshal(self, value: Any, from_lang: str, to_lang: str) -> Any:
        if from_lang == to_lang:
            return value
        key = (from_lang, to_lang)
        if key in self.marshallers:
            return self.marshallers[key](value)
        return value

    def list_functions(self, scope: str='all') -> List[str]:
        if scope == 'global':
            return list(self.global_functions.keys())
        elif scope == 'local':
            result = []
            for block_id, funcs in self.local_functions.items():
                for name in funcs.keys():
                    result.append(f'{name} [{block_id}]')
            return result
        elif scope == 'all':
            global_list = self.list_functions('global')
            local_list = self.list_functions('local')
            return global_list + local_list
        else:
            raise ValueError(f'Invalid scope: {scope}')

    def list_by_language(self, language: str) -> List[str]:
        result = []
        for name, sig in self.global_functions.items():
            if sig.language == language:
                result.append(name)
        for block_funcs in self.local_functions.values():
            for name, sig in block_funcs.items():
                if sig.language == language:
                    result.append(name)
        return result

    def info(self, name: str) -> Dict[str, Any]:
        try:
            sig = self.get(name)
            return {'name': sig.name, 'language': sig.language, 'signature': str(sig), 'parameters': [{'name': p.name, 'type': p.type_hint, 'default': p.default} for p in sig.parameters], 'return_type': sig.return_type, 'scope': sig.scope, 'doc': sig.doc, 'arity': sig.arity(), 'max_arity': sig.max_arity()}
        except FunctionNotFoundError:
            return None

    def _validate_arguments(self, signature: FunctionSignature, args: List[Any], kwargs: Dict[str, Any]) -> None:
        required_params = [p for p in signature.parameters if p.default is None]
        if len(args) + len(kwargs) < len(required_params):
            param_names = [p.name for p in required_params]
            raise InvalidFunctionCallError(f"Function '{signature.name}' requires at least {len(required_params)} arguments: {param_names}. Got {len(args)} positional and {len(kwargs)} keyword arguments.")

    def clear_local(self, block_id: str) -> None:
        if block_id in self.local_functions:
            del self.local_functions[block_id]

    def export_to_json(self) -> str:
        result = {'global': {name: sig.to_dict() for name, sig in self.global_functions.items()}, 'local': {block_id: {name: sig.to_dict() for name, sig in funcs.items()} for block_id, funcs in self.local_functions.items()}}
        return json.dumps(result, indent=2)

    def summary(self) -> str:
        global_count = len(self.global_functions)
        local_count = sum((len(funcs) for funcs in self.local_functions.values()))
        lines = [f'Function Registry Summary', f'========================', f'Global Functions: {global_count}', f'Local Functions: {local_count}', f'Total: {global_count + local_count}', '']
        if self.global_functions:
            lines.append('Global Functions:')
            for name, sig in self.global_functions.items():
                lines.append(f'  - {sig}')
        if self.local_functions:
            lines.append('\nLocal Functions:')
            for block_id, funcs in self.local_functions.items():
                for name, sig in funcs.items():
                    lines.append(f'  - {sig} [block: {block_id}]')
        return '\n'.join(lines)
_registry: Optional[FunctionRegistry] = None

def get_registry() -> FunctionRegistry:
    global _registry
    if _registry is None:
        _registry = FunctionRegistry()
    return _registry

def create_registry() -> FunctionRegistry:
    return FunctionRegistry()
