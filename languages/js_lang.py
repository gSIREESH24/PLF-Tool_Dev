import subprocess
import json
import re
from core.function_signature import FunctionSignature, Parameter


def run(code, context, registry=None):
    """
    Enhanced JavaScript runner with function registry support.
    
    Args:
        code: JavaScript code to execute
        context: Shared context object
        registry: FunctionRegistry for cross-language calls
    """
    js_vars = ""

    # Inject context variables
    for key, value in context.all().items():
        if key.startswith("__"):
            continue

        try:
            js_value = json.dumps(value)
            js_vars += f"var {key} = {js_value};\n"
        except TypeError:
            continue
    
    # Create function registry interface for JavaScript
    registry_interface = ""
    if registry:
        registry_interface = _create_registry_interface_js(registry)
    
    full_code = js_vars + registry_interface + code
    
    # Execute JavaScript
    try:
        result = subprocess.run(
            ["node", "-e", full_code],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print("Error:", result.stderr, file=__import__('sys').stderr)
            
    except FileNotFoundError:
        print("Warning: Node.js not found. Skipping JavaScript execution.")
    except subprocess.TimeoutExpired:
        print("Error: JavaScript execution timeout")
    
    # Extract functions from JavaScript code if registry is available
    if registry:
        _extract_and_register_functions(code, registry, context)


def _create_registry_interface_js(registry):
    """
    Create JavaScript code that provides registry interface.
    
    Args:
        registry: FunctionRegistry instance
        
    Returns:
        JavaScript code string
    """
    js_code = """
// Poly Function Registry Interface
var PolyRegistry = {
    call: function(funcName, args) {
        // This will be overridden by Python-side implementation
        console.warn('Function call not implemented:', funcName);
        return null;
    },
    
    get: function(funcName) {
        // This will be overridden by Python-side implementation
        console.warn('Function get not implemented:', funcName);
        return null;
    }
};

// Convenience function
function polyCall(funcName, args) {
    args = args || [];
    return PolyRegistry.call(funcName, args);
}
"""
    
    return js_code


def _extract_and_register_functions(code, registry, context):
    """
    Extract function definitions from JavaScript code and register them.
    
    Args:
        code: JavaScript source code
        registry: FunctionRegistry
        context: Shared context
    """
    # Pattern for: function name(...) or const name = function(...) or const name = (...) =>
    patterns = [
        r'function\s+(\w+)\s*\((.*?)\)\s*\{',
        r'const\s+(\w+)\s*=\s*function\s*\((.*?)\)\s*\{',
        r'let\s+(\w+)\s*=\s*function\s*\((.*?)\)\s*\{',
        r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
        r'let\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, code):
            func_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            parameters = _parse_js_params(params_str)
            
            # Create signature (JavaScript functions can't be directly called,
            # so we store metadata for potential future use)
            sig = FunctionSignature(
                name=func_name,
                language="javascript",
                parameters=parameters,
                return_type="any",
                scope="global",
                callable=None,  # Can't directly call JS functions from Python
                doc=None
            )
            
            # Register function metadata
            registry.register(sig, scope="global")
            print(f"      [JavaScript] Registered function: {func_name}")


def _parse_js_params(params_str):
    """
    Parse JavaScript function parameters.
    
    Args:
        params_str: String like "a, b, c = 5"
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    
    if not params_str.strip():
        return parameters
    
    # Split by comma
    parts = params_str.split(",")
    
    for part in parts:
        param = _parse_single_js_param(part.strip())
        if param:
            parameters.append(param)
    
    return parameters


def _parse_single_js_param(param_str):
    """
    Parse a single JavaScript parameter.
    
    Examples:
        "a" → Parameter(name='a')
        "a = 5" → Parameter(name='a', default=5)
    
    Args:
        param_str: String representation of parameter
        
    Returns:
        Parameter object or None
    """
    param_str = param_str.strip()
    
    if "=" in param_str:
        name, default_str = param_str.split("=", 1)
        name = name.strip()
        default_str = default_str.strip()
        
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        name = param_str
        default = None
    
    return Parameter(name=name, type_hint="any", default=default)

