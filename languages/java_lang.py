import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context=None, registry=None):

    with tempfile.TemporaryDirectory() as temp_dir:

        if "class " not in code:

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

            match = re.search(r'class\s+(\w+)', code)
            class_name = match.group(1) if match else "PolyJavaRuntime"
            full_code = code

        java_file = os.path.join(temp_dir, f"{class_name}.java")
        with open(java_file, 'w') as f:
            f.write(full_code)

        try:

            compile_result = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            if compile_result.returncode != 0:
                print(f"Java Compilation error: {compile_result.stderr}")
                return

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

    if registry:
        _extract_and_register_functions(code, registry, context)

def _extract_and_register_functions(code, registry, context):

    pattern = r'(?:public|private|protected)?\s*(?:static)?\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)

        if func_name in ("main", "equals", "toString", "hashCode"):
            continue

        parameters = _parse_java_params(params_str)

        sig = FunctionSignature(
            name=func_name,
            language="java",
            parameters=parameters,
            return_type=return_type,
            scope="global",
            callable=None,
            doc=None
        )

        registry.register(sig, scope="global")
        print(f"      [Java] Registered function: {func_name}")

def _parse_java_params(params_str):
    parameters = []

    if not params_str.strip():
        return parameters

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

    for part in parts:
        param = _parse_single_java_param(part)
        if param:
            parameters.append(param)

    return parameters

def _parse_single_java_param(param_str):
    param_str = param_str.strip()

    if "..." in param_str:
        parts = param_str.replace("...", "").rsplit(None, 1)
        if len(parts) == 2:
            type_hint = parts[0]
            name = parts[1]
        else:
            return None
        return Parameter(name=name, type_hint=type_hint, is_variadic=True)

    parts = param_str.rsplit(None, 1)

    if len(parts) == 2:
        type_hint = parts[0]
        name = parts[1]
    else:
        return None

    return Parameter(name=name, type_hint=type_hint)