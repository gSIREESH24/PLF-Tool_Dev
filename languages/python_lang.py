import inspect
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context, registry=None, is_global=False):

    # ── Bridge helpers ────────────────────────────────────────────────────

    def export(name, value):
        try:
            from core.polyobj import PolyObject
            if hasattr(value, 'to_dict'):
                context.set(name, PolyObject(value.to_dict()))
            elif isinstance(value, dict) and not isinstance(value, PolyObject):
                context.set(name, PolyObject(value))
            else:
                context.set(name, value)
        except Exception:
            context.set(name, value)

    def export_function(name, func, param_types=None, return_type=None):
        """Register a Python callable in the bridge function table."""
        context.export_function(name, func, language="python",
                                param_types=param_types, return_type=return_type)
        # Also register in the old registry if present
        if registry:
            try:
                import inspect, re as _re
                from core.function_signature import FunctionSignature
                parameters = _parse_python_params(
                    str(inspect.signature(func))[1:-1])
                sig = FunctionSignature(name=name, language='python',
                                        parameters=parameters,
                                        return_type=return_type,
                                        scope='global', callable=func,
                                        doc=func.__doc__)
                registry.register(sig, scope='global')
            except Exception:
                pass

    def call(func_name, *args):
        """Call a registered bridge function."""
        # Try context first (new path), fall back to old registry
        if context.has_function(func_name):
            return context.call(func_name, *args)
        if registry:
            try:
                return registry.call(func_name, list(args), {})
            except Exception:
                pass
        raise NameError(f"[Bridge] Function '{func_name}' is not registered.")

    def get_global(name, default=None):
        v = context.get(name)
        return default if v is None else v

    def get_function(func_name):
        fn = context.get_function(func_name)
        if fn:
            return fn
        if registry:
            try:
                sig = registry.get(func_name)
                return sig.callable
            except Exception:
                pass
        raise NameError(f"[Bridge] Function '{func_name}' not found.")

    def store_object(obj) -> int:
        return context.store_object(obj)

    def load_object(handle: int):
        return context.load_object(handle)

    def delete_object(handle: int):
        context.delete_object(handle)

    # ── Inject class definitions if class registry exists ────────────────
    try:
        from core.class_registry import get_class_registry, generate_python_class
        cls_reg = get_class_registry()
        classes_code = ''
        for cls in cls_reg.get_all():
            classes_code += generate_python_class(cls) + '\n'
        code = classes_code + code
    except Exception:
        pass

    # ── Build execution environment ───────────────────────────────────────
    local_env = context.all().copy()
    _helpers = {
        'export':          export,
        'export_function': export_function,
        'call':            call,
        'get_global':      get_global,
        'get_function':    get_function,
        'store_object':    store_object,
        'load_object':     load_object,
        'delete_object':   delete_object,
    }
    local_env.update(_helpers)

    exec(code, local_env)

    # ── Register any defined functions in the old registry ────────────────
    if registry:
        _extract_and_register_functions(code, local_env, registry, context,
                                        is_global=is_global)

    # ── Sync new plain variables back into the bridge ─────────────────────
    _skip = set(_helpers.keys()) | {'__builtins__'}
    try:
        from core.polyobj import PolyObject
        _polyobj = PolyObject
    except Exception:
        _polyobj = None

    for key, value in local_env.items():
        if key.startswith('__') or key in _skip:
            continue
        if inspect.isfunction(value) or inspect.isclass(value):
            continue
        if _polyobj and isinstance(value, dict) and not isinstance(value, _polyobj):
            context.set(key, _polyobj(value))
        elif _polyobj and hasattr(value, 'to_dict'):
            context.set(key, _polyobj(value.to_dict()))
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
