import subprocess
import json
import tempfile
import ctypes
import os
from pathlib import Path
from core.function_signature import FunctionSignature

class CAdapter:

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.compiled_functions = {}

    def call_c_function(self, function_name, args, c_code=None):
        try:
            if function_name not in self.compiled_functions and c_code:
                self._compile_c_function(function_name, c_code)
            wrapper_code = self._create_c_wrapper(function_name, args)
            wrapper_file = Path(self.temp_dir) / 'c_wrapper.c'
            wrapper_file.write_text(wrapper_code)
            exe_file = wrapper_file.with_suffix('.exe')
            compile_result = subprocess.run(['gcc', str(wrapper_file), '-o', str(exe_file), '-lm'], capture_output=True, text=True)
            if compile_result.returncode != 0:
                raise RuntimeError(f'C compilation error: {compile_result.stderr}')
            exec_result = subprocess.run([str(exe_file)], capture_output=True, text=True)
            if exec_result.returncode != 0:
                raise RuntimeError(f'C execution error: {exec_result.stderr}')
            if exe_file.exists():
                exe_file.unlink()
            try:
                return json.loads(exec_result.stdout)
            except:
                return exec_result.stdout.strip()
        except Exception as e:
            raise RuntimeError(f'Error calling C function {function_name}: {str(e)}')

    def _compile_c_function(self, function_name, c_code):
        try:
            c_file = Path(self.temp_dir) / f'{function_name}.c'
            c_file.write_text(c_code)
            obj_file = c_file.with_suffix('.o')
            compile_result = subprocess.run(['gcc', '-c', str(c_file), '-o', str(obj_file)], capture_output=True, text=True)
            if compile_result.returncode == 0:
                self.compiled_functions[function_name] = str(obj_file)
        except Exception as e:
            raise RuntimeError(f'Error compiling C function {function_name}: {str(e)}')

    def _create_c_wrapper(self, function_name, args):
        args_json = json.dumps(args)
        return f'\n\nextern int {function_name}();\n\nint main() {{\n    try {{\n\n\n\n        int result = {function_name}();\n\n        printf("{{\\"result\\": %d}}", result);\n\n        return 0;\n    }} catch (...) {{\n        fprintf(stderr, "Error in C wrapper");\n        return 1;\n    }}\n}}\n'

    def create_c_function_signature(self, function_name, return_type, param_types):
        params = []
        for i, ptype in enumerate(param_types):
            params.append({'name': f'arg{i}', 'type': ptype})
        return FunctionSignature(name=function_name, language='c', implementation=function_name, return_type=return_type, parameters=params)

    def convert_c_type(self, c_type, value):
        if c_type in ['int', 'int32_t', 'int64_t']:
            return int(value)
        elif c_type in ['float', 'double']:
            return float(value)
        elif c_type in ['char*', 'const char*', 'char*']:
            return str(value).encode('utf-8')
        elif c_type in ['void']:
            return None
        else:
            return value

    def convert_from_c(self, c_type, value):
        if c_type in ['int', 'int32_t', 'int64_t']:
            return int(value)
        elif c_type in ['float', 'double']:
            return float(value)
        elif c_type in ['char*', 'const char*']:
            return value.decode('utf-8') if isinstance(value, bytes) else str(value)
        elif c_type in ['void']:
            return None
        else:
            return value

    def extract_c_function_signature(self, c_code, function_name):
        import re
        pattern = f'(\\w+)\\s+{function_name}\\s*\\((.*?)\\)'
        match = re.search(pattern, c_code)
        if match:
            return_type = match.group(1)
            params_str = match.group(2)
            params = []
            if params_str.strip() != 'void' and params_str.strip():
                param_list = params_str.split(',')
                for param in param_list:
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        params.append({'type': ' '.join(parts[:-1]), 'name': parts[-1]})
            return {'name': function_name, 'return_type': return_type, 'parameters': params, 'parameter_count': len(params)}
        return {'name': function_name, 'return_type': 'unknown', 'parameters': [], 'parameter_count': 0}

def create_c_adapter():
    return CAdapter()
