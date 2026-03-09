"""
Java Language Support - Cross-language function calling for Java

Java functions are compiled and executed within the Poly Runtime.
Functions can be called from Python, JavaScript, C, and C++.
"""

import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter


def run(code, context=None, registry=None):
    """
    Java runner with function registry support.
    
    Args:
        code: Java code to execute
        context: Shared context object (optional)
        registry: FunctionRegistry for cross-language calls (optional)
    """
    
    # Create a temp directory for Java files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Wrap code in a class if not already wrapped
        if "class " not in code:
            # Generate a unique class name
            class_name = "PolyJavaRuntime"
            full_code = f"""
public class {class_name} {{
    {code}
    
    public static void main(String[] args) {{
        // Entry point for execution
    }}
}}
"""
        else:
            # Extract class name from code
            match = re.search(r'class\s+(\w+)', code)
            class_name = match.group(1) if match else "PolyJavaRuntime"
            full_code = code
        
        # Write Java file
        java_file = os.path.join(temp_dir, f"{class_name}.java")
        with open(java_file, 'w') as f:
            f.write(full_code)
        
        try:
            # Compile Java code
            compile_result = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            if compile_result.returncode != 0:
                print(f"Java Compilation error: {compile_result.stderr}")
                return
            
            # Run Java code
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, class_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if run_result.stdout:
                print(run_result.stdout, end="")
            if run_result.stderr:
                print("Java Error:", run_result.stderr)
                
        except FileNotFoundError:
            print("Warning: Java (javac/java) not found. Skipping Java execution.")
        except subprocess.TimeoutExpired:
            print("Error: Java execution timeout")
        except Exception as e:
            print(f"Error running Java: {e}")
    
    # Extract functions from Java code if registry is available
    if registry:
        _extract_and_register_functions(code, registry, context)


def _extract_and_register_functions(code, registry, context):
    """
    Extract function definitions from Java code and register them.
    
    Args:
        code: Java source code
        registry: FunctionRegistry
        context: Shared context
    """
    # Pattern for Java methods: public/private static return_type method_name(...)
    # Covers: public static int add(int a, int b)
    #         private static String greet(String name)
    #         public int calculate(int x)
    pattern = r'(?:public|private|protected)?\s*(?:static)?\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'
    
    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)
        
        # Skip main and system methods
        if func_name in ("main", "equals", "toString", "hashCode"):
            continue
        
        # Parse parameters
        parameters = _parse_java_params(params_str)
        
        # Create signature
        sig = FunctionSignature(
            name=func_name,
            language="java",
            parameters=parameters,
            return_type=return_type,
            scope="global",
            callable=None,  # Can't directly call Java functions from Python
            doc=None
        )
        
        # Register function metadata
        registry.register(sig, scope="global")
        print(f"      [Java] Registered function: {func_name}")


def _parse_java_params(params_str):
    """
    Parse Java function parameters.
    
    Args:
        params_str: String like "int a, String b, double c"
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    
    if not params_str.strip():
        return parameters
    
    # Split by comma (handling generics with < >)
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
        param = _parse_single_java_param(part)
        if param:
            parameters.append(param)
    
    return parameters


def _parse_single_java_param(param_str):
    """
    Parse a single Java parameter.
    
    Examples:
        "int a" → Parameter(name='a', type_hint='int')
        "String name" → Parameter(name='name', type_hint='String')
        "List<String> items" → Parameter(name='items', type_hint='List<String>')
        "int... numbers" → Parameter(name='numbers', type_hint='int', is_variadic=True)
    
    Args:
        param_str: String representation of parameter
        
    Returns:
        Parameter object or None
    """
    param_str = param_str.strip()
    
    # Handle variadic (int... args)
    if "..." in param_str:
        parts = param_str.replace("...", "").rsplit(None, 1)
        if len(parts) == 2:
            type_hint = parts[0]
            name = parts[1]
        else:
            return None
        return Parameter(name=name, type_hint=type_hint, is_variadic=True)
    
    # Split on last whitespace to separate type from name
    parts = param_str.rsplit(None, 1)
    
    if len(parts) == 2:
        type_hint = parts[0]
        name = parts[1]
    else:
        return None
    
    return Parameter(name=name, type_hint=type_hint)
