import inspect
import re
from core.function_signature import FunctionSignature, Parameter


def run(code, context, registry=None):
    """
    Enhanced Python runner with function registry support.
    
    Args:
        code: Python code to execute
        context: Shared context object
        registry: FunctionRegistry for cross-language calls
    """
    # Define export function
    def export(name, value):
        context.set(name, value)
    
    # Define function calling mechanism for cross-language calls
    def call(func_name, args=None, kwargs=None):
        """Call a function from any language"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        if registry:
            return registry.call(func_name, args, kwargs)
        else:
            raise RuntimeError("Function registry not available")
    
    def get_function(func_name):
        """Get a function object by name"""
        if registry:
            sig = registry.get(func_name)
            return sig.callable
        else:
            raise RuntimeError("Function registry not available")
    
    # Prepare execution environment
    local_env = context.all().copy()
    local_env["export"] = export
    local_env["call"] = call
    local_env["get_function"] = get_function
    
    # Execute code
    exec(code, local_env)
    
    # Extract and register functions defined in this block
    if registry:
        _extract_and_register_functions(code, local_env, registry, context)
    
    # Update context with new variables (but not functions)
    for key, value in local_env.items():
        if not key.startswith("__") and key not in ("export", "call", "get_function"):
            # Don't overwrite functions as variables
            if not inspect.isfunction(value):
                context.set(key, value)


def _extract_and_register_functions(code, local_env, registry, context):
    """
    Extract function definitions from Python code and register them.
    
    Args:
        code: Python source code
        local_env: Local environment after execution
        registry: FunctionRegistry
        context: Shared context
    """
    # Find all function definitions
    func_pattern = r'def\s+(\w+)\s*\((.*?)\)'
    
    for match in re.finditer(func_pattern, code):
        func_name = match.group(1)
        params_str = match.group(2)
        
        # Get the actual function object
        if func_name in local_env and inspect.isfunction(local_env[func_name]):
            func_obj = local_env[func_name]
            
            # Parse parameters
            parameters = _parse_python_params(params_str)
            
            # Get return type annotation if available
            return_annotation = func_obj.__annotations__.get('return', None)
            
            # Create signature
            sig = FunctionSignature(
                name=func_name,
                language="python",
                parameters=parameters,
                return_type=return_annotation,
                scope="global",
                callable=func_obj,
                doc=func_obj.__doc__
            )
            
            # Register function
            registry.register(sig, scope="global")
            print(f"      [Python] Registered function: {func_name}")
            
            # Also export to context
            context.set(func_name, func_obj)


def _parse_python_params(params_str):
    """
    Parse Python function parameters to extract names, types, defaults.
    
    Args:
        params_str: String like "a: int, b: int = 5, *args"
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    
    if not params_str.strip():
        return parameters
    
    # Split by comma, handling nested parentheses
    parts = []
    current = ""
    depth = 0
    
    for char in params_str:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        
        current += char
    
    if current.strip():
        parts.append(current.strip())
    
    # Parse each parameter
    for part in parts:
        param = _parse_single_param(part)
        if param:
            parameters.append(param)
    
    return parameters


def _parse_single_param(param_str):
    """
    Parse a single parameter string.
    
    Examples:
        "a" → Parameter(name='a')
        "a: int" → Parameter(name='a', type_hint='int')
        "a: int = 5" → Parameter(name='a', type_hint='int', default=5)
        "*args" → Parameter(name='args', is_variadic=True)
    
    Args:
        param_str: String representation of parameter
        
    Returns:
        Parameter object or None
    """
    param_str = param_str.strip()
    
    # Handle variadic (*args, **kwargs)
    if param_str.startswith("*"):
        name = param_str.lstrip("*")
        return Parameter(name=name, is_variadic=True)
    
    # Split on default value
    if "=" in param_str:
        decl, default_str = param_str.split("=", 1)
        default_str = default_str.strip()
        
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        decl = param_str
        default = None
    
    # Split declaration on type annotation
    if ":" in decl:
        name, type_hint = decl.split(":", 1)
        name = name.strip()
        type_hint = type_hint.strip()
    else:
        name = decl.strip()
        type_hint = None
    
    return Parameter(name=name, type_hint=type_hint, default=default)

