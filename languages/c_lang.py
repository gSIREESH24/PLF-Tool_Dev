import subprocess
import tempfile
import os
import re
from core.function_signature import FunctionSignature, Parameter

def run(code, context=None, registry=None):
    enhanced_code = "#include <string.h>\n#include <stdlib.h>\n#include <stdbool.h>\n#include <stdio.h>\n"
    if context:
        from global_ns.marshalling import Marshaller
        from core.polyobj import PolyObject
        for key, value in context.all().items():
            if key.startswith('__') or hasattr(value, '__call__') or type(value).__name__ == 'type': 
                continue
            try:
                # Handle PolyObject by converting to dict
                if isinstance(value, PolyObject):
                    value = value.to_dict()
                
                if isinstance(value, bool): 
                    c_type = "bool"
                    c_val = Marshaller.python_to_c(value)
                    enhanced_code += f"{c_type} {key} = {c_val};\n"
                elif isinstance(value, int): 
                    c_type = "int"
                    c_val = value
                    enhanced_code += f"{c_type} {key} = {c_val};\n"
                elif isinstance(value, float): 
                    c_type = "double"
                    c_val = value
                    enhanced_code += f"{c_type} {key} = {c_val};\n"
                elif isinstance(value, str): 
                    c_type = "char*"
                    c_val = Marshaller.python_to_c(value)
                    enhanced_code += f"{c_type} {key} = {c_val};\n"
                elif isinstance(value, dict):
                    # Skip dict objects (class instances) - they'll be handled as class definitions
                    pass
                elif isinstance(value, (list, tuple)):
                    # Create double array from Python list
                    num_elements = len(value)
                    enhanced_code += f"double {key}[] = {{"
                    enhanced_code += ", ".join(str(float(v)) for v in value)
                    enhanced_code += f"}};\nint {key}_len = {num_elements};\n"
            except Exception:
                pass
    
    # Add C export helper
    export_helper = '''
// ============================================================
// POLYGLOT EXPORT FRAMEWORK - C
// Unified export mechanism for inter-language communication
// Usage: EXPORT_DOUBLE("variable_name", value), etc.
// ============================================================

#include <stdio.h>

void export_c(const char* name, void* value, int type) {
    /**
     * Export a variable to the polyglot context.
     * 
     * @param name Variable name to export
     * @param value Pointer to value
     * @param type 0=double, 1=int, 2=string
     */
    if (type == 0) {
        double* d = (double*) value;
        fprintf(stderr, "POLY_EXPORT:%s=%f\\n", name, *d);
    } else if (type == 1) {
        int* i = (int*) value;
        fprintf(stderr, "POLY_EXPORT:%s=%d\\n", name, *i);
    } else if (type == 2) {
        char* s = (char*) value;
        fprintf(stderr, "POLY_EXPORT:%s=%s\\n", name, s);
    }
}

// Convenience macros
#define EXPORT_DOUBLE(name, val) do { double _tmp = val; fprintf(stderr, "POLY_EXPORT:%s=%f\\n", name, _tmp); } while(0)
#define EXPORT_INT(name, val) do { int _tmp = val; fprintf(stderr, "POLY_EXPORT:%s=%d\\n", name, _tmp); } while(0)
#define EXPORT_STRING(name, val) fprintf(stderr, "POLY_EXPORT:%s=%s\\n", name, val)

'''
    
    enhanced_code += export_helper
    try:
        from core.class_registry import get_class_registry, generate_c_struct
        cls_reg = get_class_registry()
        for cls in cls_reg.get_all():
            enhanced_code += generate_c_struct(cls) + "\n"
    except Exception:
        pass
    enhanced_code += code
    with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as c_file:
        c_file.write(enhanced_code.encode())
        c_file_name = c_file.name
    exe_file = c_file_name.replace('.c', '.exe') if os.name == 'nt' else c_file_name.replace('.c', '')
    try:
        compile_result = subprocess.run(['gcc', c_file_name, '-o', exe_file], capture_output=True, text=True)
        if compile_result.returncode != 0:
            print(f'Compilation error: {compile_result.stderr}')
            return
        run_result = subprocess.run([exe_file], capture_output=True, text=True, timeout=10)
        if run_result.stdout:
            print(run_result.stdout, end='')
        if run_result.stderr:
            # Parse POLY_EXPORT markers
            _parse_c_exports(run_result.stderr, context)
            # Print remaining stderr
            for line in run_result.stderr.split('\n'):
                if not line.startswith('POLY_EXPORT:'):
                    if line.strip():
                        print(line)
    except FileNotFoundError:
        print('Warning: GCC not found. Skipping C execution.')
    except subprocess.TimeoutExpired:
        print('Error: C execution timeout')
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
    pattern = '(\\w+)\\s+(\\w+)\\s*\\((.*?)\\)\\s*\\{'
    for match in re.finditer(pattern, code):
        return_type = match.group(1)
        func_name = match.group(2)
        params_str = match.group(3)
        if func_name in ('main', 'printf', 'scanf', 'malloc', 'free'):
            continue
        parameters = _parse_c_params(params_str)
        sig = FunctionSignature(name=func_name, language='c', parameters=parameters, return_type=return_type, scope='global', callable=None, doc=None, metadata={'code': code})
        registry.register(sig, scope='global')

def _parse_c_params(params_str):
    parameters = []
    if not params_str.strip() or params_str.strip() == 'void':
        return parameters
    parts = params_str.split(',')
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
        name = parts[1].lstrip('*&')
    elif len(parts) == 1:
        name = parts[0].lstrip('*&')
        type_hint = 'any'
    else:
        return None
    return Parameter(name=name, type_hint=type_hint)

def _parse_c_exports(stderr_output, context):
    """Parse POLY_EXPORT markers from C stderr output and update context"""
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
