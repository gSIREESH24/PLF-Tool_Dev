import subprocess
import json
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context, registry=None):
    js_vars = ''
    for key, value in context.all().items():
        if key.startswith('__'):
            continue
        try:
            js_value = json.dumps(value)
            js_vars += f'var {key} = {js_value};\n'
        except TypeError:
            continue
    registry_interface = ''
    if registry:
        registry_interface = _create_registry_interface_js(registry)
    classes_code = ''
    try:
        from core.class_registry import get_class_registry, generate_js_class
        cls_reg = get_class_registry()
        for cls in cls_reg.get_all():
            classes_code += generate_js_class(cls) + '\n'
    except Exception:
        pass
    full_code = js_vars + registry_interface + classes_code + code
    try:
        result = subprocess.run(['node', '-e', full_code], capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print('Error:', result.stderr, file=__import__('sys').stderr)
    except FileNotFoundError:
        print('Warning: Node.js not found. Skipping JavaScript execution.')
    except subprocess.TimeoutExpired:
        print('Error: JavaScript execution timeout')
    if registry:
        _extract_and_register_functions(code, registry, context)

def _create_registry_interface_js(registry):
    js_code = "\n\nvar PolyRegistry = {\n    call: function(funcName, args) {\n\n        console.warn('Function call not implemented:', funcName);\n        return null;\n    },\n\n    get: function(funcName) {\n\n        console.warn('Function get not implemented:', funcName);\n        return null;\n    }\n};\n\nfunction polyCall(funcName, args) {\n    args = args || [];\n    return PolyRegistry.call(funcName, args);\n}\n"
    return js_code

def _extract_and_register_functions(code, registry, context):
    patterns = ['function\\s+(\\w+)\\s*\\((.*?)\\)\\s*\\{', 'const\\s+(\\w+)\\s*=\\s*function\\s*\\((.*?)\\)\\s*\\{', 'let\\s+(\\w+)\\s*=\\s*function\\s*\\((.*?)\\)\\s*\\{', 'const\\s+(\\w+)\\s*=\\s*\\((.*?)\\)\\s*=>', 'let\\s+(\\w+)\\s*=\\s*\\((.*?)\\)\\s*=>']
    for pattern in patterns:
        for match in re.finditer(pattern, code):
            func_name = match.group(1)
            params_str = match.group(2)
            parameters = _parse_js_params(params_str)
            sig = FunctionSignature(name=func_name, language='javascript', parameters=parameters, return_type='any', scope='global', callable=None, doc=None)
            registry.register(sig, scope='global')

def _parse_js_params(params_str):
    parameters = []
    if not params_str.strip():
        return parameters
    parts = params_str.split(',')
    for part in parts:
        param = _parse_single_js_param(part.strip())
        if param:
            parameters.append(param)
    return parameters

def _parse_single_js_param(param_str):
    param_str = param_str.strip()
    if '=' in param_str:
        name, default_str = param_str.split('=', 1)
        name = name.strip()
        default_str = default_str.strip()
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        name = param_str
        default = None
    return Parameter(name=name, type_hint='any', default=default)
