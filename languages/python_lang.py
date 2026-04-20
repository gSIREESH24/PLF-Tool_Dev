import inspect
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context, registry=None, is_global=False):

    def export(name, value):
        """
        Export a variable to the polyglot context.
        Available in all language blocks for inter-language communication.
        
        Args:
            name (str): Variable name to export
            value: Value to export (primitives, lists, dicts, class instances)
        
        For class instances: automatically converts to dict via to_dict()
        For primitives/lists: stored as-is
        """
        from core.polyobj import PolyObject
        if hasattr(value, 'to_dict'):
            # Convert class instance to dict
            value_dict = value.to_dict()
            # Wrap in PolyObject for both attribute and dict access
            context.set(name, PolyObject(value_dict))
        elif isinstance(value, dict):
            # Wrap plain dicts too
            context.set(name, PolyObject(value))
        else:
            context.set(name, value)

    def call(func_name, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if registry:
            return registry.call(func_name, args, kwargs)
        else:
            raise RuntimeError('Function registry not available')

    def get_function(func_name):
        if registry:
            sig = registry.get(func_name)
            return sig.callable
        else:
            raise RuntimeError('Function registry not available')
    try:
        from core.class_registry import get_class_registry, generate_python_class
        cls_reg = get_class_registry()
        classes_code = ''
        for cls in cls_reg.get_all():
            classes_code += generate_python_class(cls) + '\n'
        code = classes_code + code
    except Exception:
        pass
    local_env = context.all().copy()
    local_env['export'] = export
    local_env['call'] = call
    local_env['get_function'] = get_function
    exec(code, local_env)
    if registry:
        _extract_and_register_functions(code, local_env, registry, context, is_global=is_global)
    from core.polyobj import PolyObject
    for key, value in local_env.items():
        if not key.startswith('__') and key not in ('export', 'call', 'get_function'):
            if not inspect.isfunction(value) and (not inspect.isclass(value)):
                if hasattr(value, 'to_dict'):
                    # Convert class instance to dict wrapped in PolyObject
                    context.set(key, PolyObject(value.to_dict()))
                elif isinstance(value, dict) and not isinstance(value, PolyObject):
                    # Wrap plain dicts in PolyObject
                    context.set(key, PolyObject(value))
                else:
                    context.set(key, value)

def _extract_and_register_functions(code, local_env, registry, context, is_global=False):
    func_pattern = 'def\\s+(\\w+)\\s*\\((.*?)\\)'
    for match in re.finditer(func_pattern, code):
        func_name = match.group(1)
        params_str = match.group(2)
        if func_name in local_env and inspect.isfunction(local_env[func_name]):
            func_obj = local_env[func_name]
            parameters = _parse_python_params(params_str)
            return_annotation = func_obj.__annotations__.get('return', None)
            scope = 'global' if is_global else 'global'
            sig = FunctionSignature(name=func_name, language='python', parameters=parameters, return_type=return_annotation, scope=scope, callable=func_obj, doc=func_obj.__doc__)
            registry.register(sig, scope=scope)
            context.set(func_name, func_obj)

def _parse_python_params(params_str):
    parameters = []
    if not params_str.strip():
        return parameters
    parts = []
    current = ''
    depth = 0
    for char in params_str:
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(current.strip())
            current = ''
            continue
        current += char
    if current.strip():
        parts.append(current.strip())
    for part in parts:
        param = _parse_single_param(part)
        if param:
            parameters.append(param)
    return parameters

def _parse_single_param(param_str):
    param_str = param_str.strip()
    if param_str.startswith('*'):
        name = param_str.lstrip('*')
        return Parameter(name=name, is_variadic=True)
    if '=' in param_str:
        decl, default_str = param_str.split('=', 1)
        default_str = default_str.strip()
        try:
            default = eval(default_str)
        except:
            default = default_str
    else:
        decl = param_str
        default = None
    if ':' in decl:
        name, type_hint = decl.split(':', 1)
        name = name.strip()
        type_hint = type_hint.strip()
    else:
        name = decl.strip()
        type_hint = None
    return Parameter(name=name, type_hint=type_hint, default=default)
