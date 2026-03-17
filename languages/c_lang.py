import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context=None, registry=None):
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as c_file:
        c_file.write(code.encode())
        c_file_name = c_file.name

    exe_file = c_file_name.replace(".c", ".exe") if os.name == 'nt' else c_file_name.replace(".c", "")

    try:

        compile_result = subprocess.run(
            ["gcc", c_file_name, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            print(f"Compilation error: {compile_result.stderr}")
            return

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

        try:
            if os.path.exists(c_file_name):
                os.remove(c_file_name)
            if os.path.exists(exe_file):
                os.remove(exe_file)
        except:
            pass

    if registry:
        _extract_and_register_functions(code, registry, context)

def _extract_and_register_functions(code, registry, context):

    pattern = r'(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)

        if func_name in ("main", "printf", "scanf", "malloc", "free"):
            continue

        parameters = _parse_c_params(params_str)

        sig = FunctionSignature(
            name=func_name,
            language="c",
            parameters=parameters,
            return_type=return_type,
            scope="global",
            callable=None,
            doc=None
        )

        registry.register(sig, scope="global")

def _parse_c_params(params_str):
    parameters = []

    if not params_str.strip() or params_str.strip() == "void":
        return parameters

    parts = params_str.split(",")

    for part in parts:
        param = _parse_single_c_param(part.strip())
        if param:
            parameters.append(param)

    return parameters

def _parse_single_c_param(param_str):
    param_str = param_str.strip()

    parts = param_str.rsplit(None, 1)

    if len(parts) == 2:
        type_hint = parts[0]
        name = parts[1].lstrip("*&")
    elif len(parts) == 1:

        name = parts[0].lstrip("*&")
        type_hint = "any"
    else:
        return None

    return Parameter(name=name, type_hint=type_hint)