"""
Function Registry - Central repository for cross-language function calls
"""

from typing import Any, Callable, Dict, List, Optional
from core.function_signature import FunctionSignature
import json


class FunctionNotFoundError(Exception):
    """Raised when a function is not found in the registry"""
    pass


class InvalidFunctionCallError(Exception):
    """Raised when a function call is invalid (wrong args, etc)"""
    pass


class FunctionRegistry:
    """
    Central registry for managing functions across languages.
    
    Features:
    - Register functions from any language
    - Call functions with automatic marshalling
    - Support local (block-scoped) and global functions
    - Type conversion between languages
    """
    
    def __init__(self):
        """Initialize the registry"""
        # Global functions: name -> FunctionSignature
        self.global_functions: Dict[str, FunctionSignature] = {}
        
        # Local functions: block_id -> {name -> FunctionSignature}
        self.local_functions: Dict[str, Dict[str, FunctionSignature]] = {}
        
        # Function adapters: language -> adapter_class
        self.adapters: Dict[str, Any] = {}
        
        # Call history for debugging
        self.call_history: List[Dict[str, Any]] = []
        
        # Marshalling handlers
        self.marshallers: Dict[tuple, Callable] = {}
    
    def register(self, signature: FunctionSignature, scope: str = "global",
                 block_id: Optional[str] = None) -> None:
        """
        Register a function in the registry.
        
        Args:
            signature: FunctionSignature object
            scope: 'global' or 'local'
            block_id: For local functions, the block identifier
        """
        if scope == "global":
            self.global_functions[signature.name] = signature
            print(f"[Registry] Registered global function: {signature.name}")
        elif scope == "local" and block_id:
            if block_id not in self.local_functions:
                self.local_functions[block_id] = {}
            self.local_functions[block_id][signature.name] = signature
            print(f"[Registry] Registered local function: {signature.name} (block: {block_id})")
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def get(self, name: str, block_id: Optional[str] = None) -> FunctionSignature:
        """
        Get a function signature by name.
        
        Lookup order:
        1. Local functions (if block_id provided)
        2. Global functions
        
        Args:
            name: Function name
            block_id: For local lookup priority
            
        Returns:
            FunctionSignature object
            
        Raises:
            FunctionNotFoundError: If function not found
        """
        # Check local functions first
        if block_id and block_id in self.local_functions:
            if name in self.local_functions[block_id]:
                return self.local_functions[block_id][name]
        
        # Check global functions
        if name in self.global_functions:
            return self.global_functions[name]
        
        raise FunctionNotFoundError(f"Function not found: {name}")
    
    def call(self, name: str, args: List[Any], kwargs: Dict[str, Any] = None,
             block_id: Optional[str] = None) -> Any:
        """
        Call a registered function by name.
        
        Args:
            name: Function name
            args: Positional arguments
            kwargs: Keyword arguments
            block_id: For local function lookup
            
        Returns:
            Function result
            
        Raises:
            FunctionNotFoundError: If function not found
            InvalidFunctionCallError: If call is invalid
        """
        kwargs = kwargs or {}
        
        try:
            signature = self.get(name, block_id)
        except FunctionNotFoundError as e:
            raise FunctionNotFoundError(
                f"Function not found: {name}\n"
                f"Available functions: {self.list_functions()}"
            ) from e
        
        # Validate arguments
        self._validate_arguments(signature, args, kwargs)
        
        # Call the function
        try:
            result = signature.callable(*args, **kwargs)
            
            # Record call history
            self.call_history.append({
                "function": name,
                "language": signature.language,
                "args": str(args),
                "kwargs": str(kwargs),
                "result": str(result),
                "success": True
            })
            
            return result
        except Exception as e:
            self.call_history.append({
                "function": name,
                "language": signature.language,
                "args": str(args),
                "kwargs": str(kwargs),
                "error": str(e),
                "success": False
            })
            raise InvalidFunctionCallError(
                f"Error calling function '{name}': {str(e)}"
            ) from e
    
    def register_marshaller(self, from_lang: str, to_lang: str,
                           marshaller: Callable[[Any], Any]) -> None:
        """
        Register a type converter between two languages.
        
        Args:
            from_lang: Source language
            to_lang: Target language
            marshaller: Function that converts values
        """
        self.marshallers[(from_lang, to_lang)] = marshaller
    
    def marshal(self, value: Any, from_lang: str, to_lang: str) -> Any:
        """
        Convert a value from one language to another.
        
        Args:
            value: Value to convert
            from_lang: Source language
            to_lang: Target language
            
        Returns:
            Converted value
        """
        if from_lang == to_lang:
            return value
        
        key = (from_lang, to_lang)
        if key in self.marshallers:
            return self.marshallers[key](value)
        
        # Default: return as-is
        return value
    
    def list_functions(self, scope: str = "all") -> List[str]:
        """
        List all registered functions.
        
        Args:
            scope: 'global', 'local', or 'all'
            
        Returns:
            List of function names
        """
        if scope == "global":
            return list(self.global_functions.keys())
        elif scope == "local":
            result = []
            for block_id, funcs in self.local_functions.items():
                for name in funcs.keys():
                    result.append(f"{name} [{block_id}]")
            return result
        elif scope == "all":
            global_list = self.list_functions("global")
            local_list = self.list_functions("local")
            return global_list + local_list
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def list_by_language(self, language: str) -> List[str]:
        """
        List all functions defined in a specific language.
        
        Args:
            language: Language name (python, javascript, c)
            
        Returns:
            List of function names
        """
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
        """
        Get detailed information about a function.
        
        Args:
            name: Function name
            
        Returns:
            Dictionary with function info
        """
        try:
            sig = self.get(name)
            return {
                "name": sig.name,
                "language": sig.language,
                "signature": str(sig),
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type_hint,
                        "default": p.default
                    }
                    for p in sig.parameters
                ],
                "return_type": sig.return_type,
                "scope": sig.scope,
                "doc": sig.doc,
                "arity": sig.arity(),
                "max_arity": sig.max_arity()
            }
        except FunctionNotFoundError:
            return None
    
    def _validate_arguments(self, signature: FunctionSignature,
                           args: List[Any], kwargs: Dict[str, Any]) -> None:
        """Validate function arguments against signature"""
        required_params = [p for p in signature.parameters if p.default is None]
        
        # Check minimum arguments
        if len(args) + len(kwargs) < len(required_params):
            param_names = [p.name for p in required_params]
            raise InvalidFunctionCallError(
                f"Function '{signature.name}' requires at least {len(required_params)} "
                f"arguments: {param_names}. Got {len(args)} positional and "
                f"{len(kwargs)} keyword arguments."
            )
    
    def clear_local(self, block_id: str) -> None:
        """Clear local functions for a block"""
        if block_id in self.local_functions:
            del self.local_functions[block_id]
    
    def export_to_json(self) -> str:
        """Export all function signatures as JSON"""
        result = {
            "global": {
                name: sig.to_dict()
                for name, sig in self.global_functions.items()
            },
            "local": {
                block_id: {
                    name: sig.to_dict()
                    for name, sig in funcs.items()
                }
                for block_id, funcs in self.local_functions.items()
            }
        }
        return json.dumps(result, indent=2)
    
    def summary(self) -> str:
        """Get a summary of registered functions"""
        global_count = len(self.global_functions)
        local_count = sum(len(funcs) for funcs in self.local_functions.values())
        
        lines = [
            f"Function Registry Summary",
            f"========================",
            f"Global Functions: {global_count}",
            f"Local Functions: {local_count}",
            f"Total: {global_count + local_count}",
            ""
        ]
        
        if self.global_functions:
            lines.append("Global Functions:")
            for name, sig in self.global_functions.items():
                lines.append(f"  - {sig}")
        
        if self.local_functions:
            lines.append("\nLocal Functions:")
            for block_id, funcs in self.local_functions.items():
                for name, sig in funcs.items():
                    lines.append(f"  - {sig} [block: {block_id}]")
        
        return "\n".join(lines)


# Global registry instance (can be used as singleton)
_registry: Optional[FunctionRegistry] = None


def get_registry() -> FunctionRegistry:
    """Get or create the global function registry"""
    global _registry
    if _registry is None:
        _registry = FunctionRegistry()
    return _registry


def create_registry() -> FunctionRegistry:
    """Create a new function registry (useful for testing)"""
    return FunctionRegistry()
