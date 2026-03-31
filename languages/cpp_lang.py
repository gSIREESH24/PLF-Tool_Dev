import subprocess
import tempfile
import os
import re
import json
from core.function_signature import FunctionSignature, Parameter

def run(code, context=None, registry=None, is_global=False):
    wrapper_code = ''
    if registry and (not is_global):
        wrapper_code = _generate_cpp_wrappers(registry)
    enhanced_code = '#include <string>\n#include <vector>\n#include <map>\n' + wrapper_code + '\n'
    if context:
        from global_ns.marshalling import Marshaller
        for key, value in context.all().items():
            if key.startswith('__') or hasattr(value, '__call__') or type(value).__name__ == 'type': continue
            try:
                if isinstance(value, bool): cpp_type = "bool"; cpp_val = "true" if value else "false"
                elif isinstance(value, int): cpp_type = "int"; cpp_val = value
                elif isinstance(value, float): cpp_type = "float"; cpp_val = value
                elif isinstance(value, str): cpp_type = "std::string"; cpp_val = f'"{value}"'
                else: continue
                enhanced_code += f"{cpp_type} {key} = {cpp_val};\n"
            except Exception:
                pass
    try:
        from core.class_registry import get_class_registry, generate_cpp_class
        cls_reg = get_class_registry()
        for cls in cls_reg.get_all():
            enhanced_code += generate_cpp_class(cls) + '\n'
    except Exception:
        pass
    enhanced_code += code
    with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as cpp_file:
        cpp_file.write(enhanced_code.encode())
        cpp_file_name = cpp_file.name
    exe_file = cpp_file_name.replace('.cpp', '.exe') if os.name == 'nt' else cpp_file_name.replace('.cpp', '')
    try:
        compile_result = subprocess.run(['g++', cpp_file_name, '-o', exe_file], capture_output=True, text=True)
        if compile_result.returncode != 0:
            print(f'C++ Compilation error: {compile_result.stderr}')
            return
        run_result = subprocess.run([exe_file], capture_output=True, text=True, timeout=10)
        if run_result.stdout:
            print(run_result.stdout, end='')
        if run_result.stderr:
            print('C++ Error:', run_result.stderr)
    except FileNotFoundError:
        print('Warning: G++ not found. Skipping C++ execution.')
    except subprocess.TimeoutExpired:
        print('Error: C++ execution timeout')
    finally:
        try:
            if os.path.exists(cpp_file_name):
                os.remove(cpp_file_name)
            if os.path.exists(exe_file):
                os.remove(exe_file)
        except:
            pass
    if registry and is_global:
        _extract_and_register_functions(code, registry, context)

def _generate_cpp_wrappers(registry):
    wrappers = '#include <iostream>\n'
    wrappers += '// Auto-generated function wrappers\n\n'
    python_funcs = registry.global_functions
    for func_name, func_sig in python_funcs.items():
        if func_sig.language == 'python' and func_sig.callable:
            params = func_sig.parameters
            param_decls = ', '.join([f'int {p.name}' for p in params]) if params else ''
            wrapper = f'\n\nint {func_name}({param_decls}) {{\n\n\n    return 0;  // Placeholder\n}}\n'
            wrappers += wrapper
    return wrappers

def _extract_and_register_functions(code, registry, context):
    pattern = '(?:inline\\s+)?(\\w+(?:<.*?>)?(?:\\s*\\*)?)?\\s+(\\w+)\\s*\\((.*?)\\)\\s*(?:const)?\\s*(?:noexcept)?\\s*(?:override)?\\s*\\{'
    for match in re.finditer(pattern, code):
        return_type = match.group(1) or 'void'
        func_name = match.group(2)
        params_str = match.group(3)
        if func_name in ('main', 'std') or func_name.startswith('~'):
            continue
        parameters = _parse_cpp_params(params_str)
        sig = FunctionSignature(name=func_name, language='cpp', parameters=parameters, return_type=return_type, scope='global', callable=None, doc=None, metadata={'code': code})
        registry.register(sig, scope='global')

def _parse_cpp_params(params_str):
    parameters = []
    if not params_str.strip():
        return parameters
    parts = []
    current = ''
    depth = 0
    for char in params_str:
        if char in '<([':
            depth += 1
        elif char in '>)]}':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(current.strip())
            current = ''
            continue
        current += char
    if current.strip():
        parts.append(current.strip())
    for part in parts:
        param = _parse_single_cpp_param(part)
        if param:
            parameters.append(param)
    return parameters

def _parse_single_cpp_param(param_str):
    param_str = param_str.strip()
    if '=' in param_str:
        decl, default_str = param_str.split('=', 1)
        decl = decl.strip()
        default_str = default_str.strip()
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        decl = param_str
        default = None
    name_match = re.search('(?:[\\s\\*&]+)?(\\w+)\\s*(?:\\[\\])?$', decl)
    if not name_match:
        return None
    name = name_match.group(1)
    type_hint = decl[:name_match.start()].strip()
    if not type_hint:
        type_hint = 'auto'
    return Parameter(name=name, type_hint=type_hint, default=default)
