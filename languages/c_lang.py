import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter


def run(code, context=None, registry=None):
    """
    Enhanced C runner with function registry support.
    
    Args:
        code: C code to execute
        context: Shared context object (optional)
        registry: FunctionRegistry for cross-language calls (optional)
    """
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as c_file:
        c_file.write(code.encode())
        c_file_name = c_file.name

    exe_file = c_file_name.replace(".c", ".exe") if os.name == 'nt' else c_file_name.replace(".c", "")

    try:
        # Compile
        compile_result = subprocess.run(
            ["gcc", c_file_name, "-o", exe_file],
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode != 0:
            print(f"Compilation error: {compile_result.stderr}")
            return
        
        # Execute
        run_result = subprocess.run(
            [exe_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if run_result.stdout:
            print(run_result.stdout, end="")
        if run_result.stderr:
            print("Error:", run_result.stderr)
            
    except FileNotFoundError:
        print("Warning: GCC not found. Skipping C execution.")
    except subprocess.TimeoutExpired:
        print("Error: C execution timeout")
    finally:
        # Cleanup
        try:
            if os.path.exists(c_file_name):
                os.remove(c_file_name)
            if os.path.exists(exe_file):
                os.remove(exe_file)
        except:
            pass
    
    # Extract functions from C code if registry is available
    if registry:
        _extract_and_register_functions(code, registry, context)


def _extract_and_register_functions(code, registry, context):
    """
    Extract function definitions from C code and register them.
    
    Args:
        code: C source code
        registry: FunctionRegistry
        context: Shared context
    """
    # Pattern for C function definitions
    # Examples: int add(int a, int b) { ... }
    #          void print(char* msg) { ... }
    pattern = r'(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    
    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)
        
        # Skip main and system functions
        if func_name in ("main", "printf", "scanf", "malloc", "free"):
            continue
        
        # Parse parameters
        parameters = _parse_c_params(params_str)
        
        # Create signature (C functions can't be directly callable from Python,
        # but we register metadata)
        sig = FunctionSignature(
            name=func_name,
            language="c",
            parameters=parameters,
            return_type=return_type,
            scope="global",
            callable=None,  # Can't directly call C functions from Python
            doc=None
        )
        
        # Register function metadata
        registry.register(sig, scope="global")
        print(f"      [C] Registered function: {func_name}")


def _parse_c_params(params_str):
    """
    Parse C function parameters.
    
    Args:
        params_str: String like "int a, int b, char* msg"
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    
    if not params_str.strip() or params_str.strip() == "void":
        return parameters
    
    # Split by comma
    parts = params_str.split(",")
    
    for part in parts:
        param = _parse_single_c_param(part.strip())
        if param:
            parameters.append(param)
    
    return parameters


def _parse_single_c_param(param_str):
    """
    Parse a single C parameter.
    
    Examples:
        "int a" → Parameter(name='a', type_hint='int')
        "char* msg" → Parameter(name='msg', type_hint='char*')
        "float x" → Parameter(name='x', type_hint='float')
    
    Args:
        param_str: String representation of parameter
        
    Returns:
        Parameter object or None
    """
    param_str = param_str.strip()
    
    # Find the last word (parameter name)
    parts = param_str.rsplit(None, 1)
    
    if len(parts) == 2:
        type_hint = parts[0]
        name = parts[1].lstrip("*&")
    elif len(parts) == 1:
        # No type hint, assume "any"
        name = parts[0].lstrip("*&")
        type_hint = "any"
    else:
        return None
    
    return Parameter(name=name, type_hint=type_hint)

