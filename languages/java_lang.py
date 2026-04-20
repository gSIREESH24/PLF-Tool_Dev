import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context=None, registry=None, is_global=False):
    with tempfile.TemporaryDirectory() as temp_dir:
        classes_code = ''
        try:
            from core.class_registry import get_class_registry, generate_java_class
            cls_reg = get_class_registry()
            for cls in cls_reg.get_all():
                classes_code += generate_java_class(cls) + '\n'
        except Exception:
            pass
        context_vars = ""
        if context:
            from core.polyobj import PolyObject
            for key, value in context.all().items():
                if key.startswith('__') or hasattr(value, '__call__') or type(value).__name__ == 'type': 
                    continue
                try:
                    # Handle PolyObject by converting to dict
                    if isinstance(value, PolyObject):
                        value = value.to_dict()
                    
                    if isinstance(value, bool): 
                        java_type = "boolean"
                        java_val = "true" if value else "false"
                        context_vars += f"    public static {java_type} {key} = {java_val};\n"
                    elif isinstance(value, int): 
                        java_type = "int"
                        java_val = value
                        context_vars += f"    public static {java_type} {key} = {java_val};\n"
                    elif isinstance(value, float): 
                        java_type = "double"
                        java_val = value
                        context_vars += f"    public static {java_type} {key} = {java_val};\n"
                    elif isinstance(value, str): 
                        java_type = "String"
                        java_val = f'"{value}"'
                        context_vars += f"    public static {java_type} {key} = {java_val};\n"
                    elif isinstance(value, dict):
                        # Skip dict objects (class instances) - they'll be handled as class definitions
                        pass
                    elif isinstance(value, (list, tuple)):
                        # Create ArrayList of doubles
                        elements = ', '.join(str(float(v)) for v in value)
                        context_vars += f"    public static java.util.List<Double> {key};\n"
                        context_vars += f"    static {{\n"
                        context_vars += f"        {key} = new java.util.ArrayList<>();\n"
                        for elem in value:
                            context_vars += f"        {key}.add({float(elem)});\n"
                        context_vars += f"    }}\n"
                except Exception:
                    pass
        
        # Add export support
        export_helper = '''
    // ============================================================
    // POLYGLOT EXPORT FRAMEWORK - Java
    // Unified export mechanism for inter-language communication
    // Usage: export_java("variable_name", value)
    // ============================================================
    
    public static void export_java(String name, Object value) {
        /**
         * Export a variable to the polyglot context.
         * Makes variables available to next language block.
         * 
         * @param name Variable name to export
         * @param value Value (primitives, lists, objects, etc.)
         */
        if (value instanceof Boolean || value instanceof Integer || value instanceof Double) {
            System.err.println("POLY_EXPORT:" + name + "=" + value);
        } else if (value instanceof String) {
            System.err.println("POLY_EXPORT:" + name + "=" + value);
        } else if (value instanceof java.util.List) {
            java.util.List list = (java.util.List) value;
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) sb.append(",");
                sb.append(list.get(i));
            }
            sb.append("]");
            System.err.println("POLY_EXPORT:" + name + "=" + sb.toString());
        } else {
            // Check if object has toJson() method (for class instances)
            try {
                java.lang.reflect.Method toJsonMethod = value.getClass().getMethod("toJson");
                String jsonStr = (String) toJsonMethod.invoke(value);
                System.err.println("POLY_EXPORT:" + name + "=" + jsonStr);
            } catch (Exception e) {
                // Fallback to toString
                System.err.println("POLY_EXPORT:" + name + "=" + value.toString());
            }
        }
    }
    
    // Alias for export
    public static void export_func(String name, Object value) {
        export_java(name, value);
    }
'''
        
        context_vars = export_helper + context_vars

        if 'class ' not in code:
            class_name = 'PolyJavaRuntime'
            full_code = classes_code + f'\npublic class {class_name} {{\n{context_vars}\n    {code}\n\n    public static void main(String[] args) {{\n\n    }}\n}}\n'
        else:
            match = re.search('class\\s+(\\w+)', code)
            class_name = match.group(1) if match else 'PolyJavaRuntime'
            injected_code = re.sub(r'class\s+\w+\s*\{', lambda m: m.group(0) + '\n' + context_vars, code, count=1)
            full_code = classes_code + injected_code
        java_file = os.path.join(temp_dir, f'{class_name}.java')
        with open(java_file, 'w') as f:
            f.write(full_code)
        try:
            compile_result = subprocess.run(['javac', java_file], capture_output=True, text=True, cwd=temp_dir)
            if compile_result.returncode != 0:
                print(f'Java Compilation error: {compile_result.stderr}')
                return
            run_result = subprocess.run(['java', '-cp', temp_dir, class_name], capture_output=True, text=True, timeout=10)
            if run_result.stdout:
                print(run_result.stdout, end='')
            if run_result.stderr:
                # Parse POLY_EXPORT markers
                _parse_java_exports(run_result.stderr, context)
                # Print remaining stderr
                for line in run_result.stderr.split('\n'):
                    if not line.startswith('POLY_EXPORT:'):
                        if line.strip():
                            print(line)
        except FileNotFoundError:
            print('Warning: Java (javac/java) not found. Skipping Java execution.')
        except subprocess.TimeoutExpired:
            print('Error: Java execution timeout')
        except Exception as e:
            print(f'Error running Java: {e}')
    if registry:
        _extract_and_register_functions(code, registry, context)

def _extract_and_register_functions(code, registry, context):
    pattern = '(?:public|private|protected)?\\s*(?:static)?\\s+(\\w+)\\s+(\\w+)\\s*\\((.*?)\\)\\s*\\{'
    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)
        if func_name in ('main', 'equals', 'toString', 'hashCode'):
            continue
        parameters = _parse_java_params(params_str)
        sig = FunctionSignature(name=func_name, language='java', parameters=parameters, return_type=return_type, scope='global', callable=None, doc=None, metadata={'code': code})
        registry.register(sig, scope='global')

def _parse_java_params(params_str):
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
        param = _parse_single_java_param(part)
        if param:
            parameters.append(param)
    return parameters

def _parse_single_java_param(param_str):
    param_str = param_str.strip()
    if '...' in param_str:
        parts = param_str.replace('...', '').rsplit(None, 1)
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

def _parse_java_exports(stderr_output, context):
    """Parse POLY_EXPORT markers from Java stderr output and update context"""
    import json
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
                        # It's a list
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
                    elif value_str.startswith('{') and value_str.endswith('}'):
                        # It's a JSON object - parse it
                        try:
                            obj = json.loads(value_str)
                            # Wrap in PolyObject for both dict and attribute access
                            context.set(name, PolyObject(obj))
                        except json.JSONDecodeError:
                            # If JSON parsing fails, store as string
                            context.set(name, value_str)
                    else:
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
