"""
C++ Language Support - Cross-language function calling for C++

C++ functions are compiled and executed within the Poly Runtime.
Functions can be called from Python, JavaScript, C, and Java.
"""

import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter


def run(code, context=None, registry=None):
    """
    C++ runner with function registry support.
    
    Args:
        code: C++ code to execute
        context: Shared context object (optional)
        registry: FunctionRegistry for cross-language calls (optional)
    """
    
    with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as cpp_file:
        cpp_file.write(code.encode())
        cpp_file_name = cpp_file.name
    
    exe_file = cpp_file_name.replace(".cpp", ".exe") if os.name == 'nt' else cpp_file_name.replace(".cpp", "")
    
    try:
        # Compile C++ code
        compile_result = subprocess.run(
            ["g++", cpp_file_name, "-o", exe_file],
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode != 0:
            print(f"C++ Compilation error: {compile_result.stderr}")
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
            print("C++ Error:", run_result.stderr)
            
    except FileNotFoundError:
        print("Warning: G++ not found. Skipping C++ execution.")
    except subprocess.TimeoutExpired:
        print("Error: C++ execution timeout")
    finally:
        # Cleanup
        try:
            if os.path.exists(cpp_file_name):
                os.remove(cpp_file_name)
            if os.path.exists(exe_file):
                os.remove(exe_file)
        except:
            pass
    
    # Extract functions from C++ code if registry is available
    if registry:
        _extract_and_register_functions(code, registry, context)


def _extract_and_register_functions(code, registry, context):
    """
    Extract function definitions from C++ code and register them.
    
    Args:
        code: C++ source code
        registry: FunctionRegistry
        context: Shared context
    """
    # Pattern for C++ function definitions
    # Covers: int add(int a, int b) { ... }
    #         std::string greet(const std::string& name) { ... }
    #         void process() { ... }
    #         double calculate(int x, float y) { ... }
    pattern = r'(?:inline\s+)?(\w+(?:<.*?>)?(?:\s*\*)?)?\s+(\w+)\s*\((.*?)\)\s*(?:const)?\s*(?:noexcept)?\s*(?:override)?\s*\{'
    
    for match in re.finditer(pattern, code):
        return_type = match.group(1) or "void"
        func_name = match.group(2)
        params_str = match.group(3)
        
        # Skip constructors, destructors, and system methods
        if func_name in ("main", "std") or func_name.startswith("~"):
            continue
        
        # Parse parameters
        parameters = _parse_cpp_params(params_str)
        
        # Create signature
        sig = FunctionSignature(
            name=func_name,
            language="cpp",
            parameters=parameters,
            return_type=return_type,
            scope="global",
            callable=None,  # Can't directly call C++ functions from Python
            doc=None
        )
        
        # Register function metadata
        registry.register(sig, scope="global")
        print(f"      [C++] Registered function: {func_name}")


def _parse_cpp_params(params_str):
    """
    Parse C++ function parameters.
    
    Args:
        params_str: String like "int a, const std::string& b, double c = 0.0"
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    
    if not params_str.strip():
        return parameters
    
    # Split by comma, handling < > for templates
    parts = []
    current = ""
    depth = 0
    
    for char in params_str:
        if char in "<([":
            depth += 1
        elif char in ">)]}":
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
        param = _parse_single_cpp_param(part)
        if param:
            parameters.append(param)
    
    return parameters


def _parse_single_cpp_param(param_str):
    """
    Parse a single C++ parameter.
    
    Examples:
        "int a" → Parameter(name='a', type_hint='int')
        "const std::string& name" → Parameter(name='name', type_hint='const std::string&')
        "int arr[]" → Parameter(name='arr', type_hint='int[]')
        "int c = 10" → Parameter(name='c', type_hint='int', default=10)
        "std::vector<int> items" → Parameter(name='items', type_hint='std::vector<int>')
    
    Args:
        param_str: String representation of parameter
        
    Returns:
        Parameter object or None
    """
    param_str = param_str.strip()
    
    # Handle default values
    if "=" in param_str:
        decl, default_str = param_str.split("=", 1)
        decl = decl.strip()
        default_str = default_str.strip()
        
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        decl = param_str
        default = None
    
    # Find the parameter name (last word or word before [ or &)
    # Handle patterns like: int a, int* p, const string& s, int arr[]
    
    # Remove array brackets from the end to get the name
    name_match = re.search(r'(?:[\s\*&]+)?(\w+)\s*(?:\[\])?$', decl)
    
    if not name_match:
        return None
    
    name = name_match.group(1)
    
    # Extract type (everything before the parameter name)
    type_hint = decl[:name_match.start()].strip()
    
    if not type_hint:
        type_hint = "auto"
    
    return Parameter(name=name, type_hint=type_hint, default=default)
