"""
Python Function Adapter
Provides interface for calling Python functions from other languages
"""

from core.function_signature import FunctionSignature


class PythonAdapter:
    """Adapter for calling Python functions from other languages"""
    
    def __init__(self):
        self.functions = {}
    
    def register_python_function(self, function_name, function):
        """
        Register a Python function for cross-language calls
        
        Args:
            function_name: Name to register the function as
            function: The actual Python function object
        """
        self.functions[function_name] = function
    
    def call_python_function(self, function_name, args, kwargs=None):
        """
        Call a registered Python function
        
        Args:
            function_name: Name of the Python function to call
            args: List of positional arguments
            kwargs: Dictionary of keyword arguments
            
        Returns:
            Result from Python function execution
        """
        if kwargs is None:
            kwargs = {}
        
        if function_name not in self.functions:
            raise RuntimeError(f"Python function '{function_name}' not found")
        
        try:
            function = self.functions[function_name]
            return function(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Error calling Python function '{function_name}': {str(e)}")
    
    def create_python_function_signature(self, function_name, function):
        """
        Create a function signature for a Python function using introspection
        
        Args:
            function_name: The function name
            function: The Python function object
            
        Returns:
            FunctionSignature object
        """
        import inspect
        
        sig = inspect.signature(function)
        params = []
        
        for param_name, param in sig.parameters.items():
            param_dict = {'name': param_name}
            
            if param.annotation != inspect.Parameter.empty:
                param_dict['type'] = str(param.annotation)
            
            if param.default != inspect.Parameter.empty:
                param_dict['default'] = param.default
            
            params.append(param_dict)
        
        return_type = 'Any'
        if sig.return_annotation != inspect.Signature.empty:
            return_type = str(sig.return_annotation)
        
        return FunctionSignature(
            name=function_name,
            language='python',
            implementation=function,
            return_type=return_type,
            parameters=params
        )
    
    def convert_python_type(self, target_type, value):
        """
        Convert value to appropriate Python type
        
        Args:
            target_type: Target Python type name
            value: Value to convert
            
        Returns:
            Converted value
        """
        if target_type in ['int', 'integer']:
            return int(value)
        elif target_type in ['float', 'double']:
            return float(value)
        elif target_type in ['str', 'string']:
            return str(value)
        elif target_type in ['bool', 'boolean']:
            return bool(value)
        elif target_type in ['list', 'List']:
            return list(value) if not isinstance(value, list) else value
        elif target_type in ['dict', 'Dict']:
            return dict(value) if not isinstance(value, dict) else value
        else:
            return value
    
    def get_function_metadata(self, function_name):
        """
        Get metadata about a registered Python function
        
        Args:
            function_name: Name of the function
            
        Returns:
            Dictionary with function metadata
        """
        import inspect
        
        if function_name not in self.functions:
            return None
        
        function = self.functions[function_name]
        sig = inspect.signature(function)
        
        return {
            'name': function_name,
            'language': 'python',
            'signature': str(sig),
            'doc': function.__doc__ or 'No documentation',
            'module': function.__module__
        }
    
    def list_functions(self):
        """
        List all registered Python functions
        
        Returns:
            Dictionary of function names and metadata
        """
        result = {}
        for name in self.functions:
            result[name] = self.get_function_metadata(name)
        return result


def create_python_adapter():
    """Factory function to create a Python adapter instance"""
    return PythonAdapter()
