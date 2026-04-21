import subprocess
import json
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context, registry=None):
    from core.polyobj import PolyObject
    js_vars = ''
    for key, value in context.all().items():
        if key.startswith('__'):
            continue
        try:
            # Convert PolyObject to plain dict for JSON serialization
            if isinstance(value, PolyObject):
                value = value.to_dict()
            js_value = json.dumps(value)
            js_vars += f'var {key} = {js_value};\n'
        except TypeError:
            continue
    
    # Add export function for polyglot framework
    export_function = '''
// ============================================================
// POLYGLOT EXPORT FRAMEWORK - JavaScript
// Unified export mechanism for inter-language communication
// Usage: export_js("variable_name", value)
// ============================================================

function export_js(name, value) {
    /**
     * Export a variable to the polyglot context.
     * Makes variables available to next language block.
     * 
     * @param {string} name - Variable name to export
     * @param {*} value - Value (primitives, arrays, objects, class instances)
     */
    if (typeof value === 'string') {
        console.error("POLY_EXPORT:" + name + "=" + value);
    } else if (typeof value === 'number' || typeof value === 'boolean') {
        console.error("POLY_EXPORT:" + name + "=" + value);
    } else if (Array.isArray(value)) {
        console.error("POLY_EXPORT:" + name + "=[" + value.join(',') + "]");
    } else if (value !== null && typeof value === 'object') {
        // Handle both plain objects and class instances
        // Check if object has toJSON method
        if (typeof value.toJSON === 'function') {
            console.error("POLY_EXPORT:" + name + "=" + JSON.stringify(value.toJSON()));
        } else {
            console.error("POLY_EXPORT:" + name + "=" + JSON.stringify(value));
        }
    } else {
        console.error("POLY_EXPORT:" + name + "=" + value);
    }
}

// Alias for export (can use either name)
function export_func(name, value) {
    export_js(name, value);
}

// poly_export: Phase_2_PLF-style export alias
function poly_export(name, value) {
    export_js(name, value);
}

// get_global: read a bridge value by name (mirrors Python get_global API)
function get_global(name, defaultValue) {
    try {
        var val = eval(name);
        return (val === undefined) ? (defaultValue !== undefined ? defaultValue : null) : val;
    } catch(e) {
        return (defaultValue !== undefined) ? defaultValue : null;
    }
}
    '''
    
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

    # Strip Python-style # comments (invalid in JS) and rewrite bare export(
    import re as _re
    clean_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            clean_lines.append('')   # keep line numbers intact
        else:
            clean_lines.append(line)
    code = '\n'.join(clean_lines)
    # Rewrite bare export(...) → poly_export(...) to avoid ES module clash
    code = _re.sub(r'(?<![.\w])export\s*\(', 'poly_export(', code)

    full_code = js_vars + export_function + registry_interface + classes_code + code
    try:
        result = subprocess.run(['node', '-e', full_code], capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            # Parse POLY_EXPORT markers
            _parse_js_exports(result.stderr, context)
            # Print remaining stderr
            for line in result.stderr.split('\n'):
                if not line.startswith('POLY_EXPORT:'):
                    if line.strip():
                        print('JS:', line)
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
            sig = FunctionSignature(name=func_name, language='javascript', parameters=parameters, return_type='any', scope='global', callable=None, doc=None, metadata={'code': code})
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

def _parse_js_exports(stderr_output, context):
    """Parse POLY_EXPORT markers from JavaScript stderr output and update context"""
    from core.polyobj import PolyObject
    for line in stderr_output.split('\n'):
        if line.startswith('POLY_EXPORT:'):
            try:
                export_data = line[len('POLY_EXPORT:'):]
                if '=' in export_data:
                    name, value_str = export_data.split('=', 1)
                    name = name.strip()
                    value_str = value_str.strip()
                    
                    # Parse value
                    if value_str.startswith('[') and value_str.endswith(']'):
                        # It's an array
                        inner = value_str[1:-1]
                        if inner:
                            try:
                                values = [float(x.strip()) for x in inner.split(',')]
                                context.set(name, values)
                            except ValueError:
                                values = [x.strip() for x in inner.split(',')]
                                context.set(name, values)
                        else:
                            context.set(name, [])
                    else:
                        # Try to parse as JSON first (for objects)
                        try:
                            value = json.loads(value_str)
                            # If it's a dict, wrap in PolyObject for both syntaxes
                            if isinstance(value, dict):
                                value = PolyObject(value)
                            context.set(name, value)
                        except json.JSONDecodeError:
                            # Try as number
                            try:
                                value = float(value_str)
                                if value == int(value):
                                    value = int(value)
                                context.set(name, value)
                            except ValueError:
                                # String value
                                context.set(name, value_str)
            except Exception as e:
                pass
