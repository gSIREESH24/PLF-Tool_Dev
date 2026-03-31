import subprocess
import json
import tempfile
import ctypes
import os
from pathlib import Path
from core.function_signature import FunctionSignature

class CppAdapter:

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.compiled_functions = {}

    def call_cpp_function(self, function_name, args, cpp_code=None):
        try:
            if function_name not in self.compiled_functions and cpp_code:
                self._compile_cpp_function(function_name, cpp_code)
            wrapper_code = self._create_cpp_wrapper(function_name, args)
            wrapper_file = Path(self.temp_dir) / 'cpp_wrapper.cpp'
            wrapper_file.write_text(wrapper_code)
            exe_file = wrapper_file.with_suffix('.exe')
            compile_result = subprocess.run(['g++', '-std=c++11', str(wrapper_file), '-o', str(exe_file)], capture_output=True, text=True)
            if compile_result.returncode != 0:
                raise RuntimeError(f'C++ compilation error: {compile_result.stderr}')
            exec_result = subprocess.run([str(exe_file)], capture_output=True, text=True)
            if exec_result.returncode != 0:
                raise RuntimeError(f'C++ execution error: {exec_result.stderr}')
            if exe_file.exists():
                exe_file.unlink()
            try:
                return json.loads(exec_result.stdout)
            except:
                return exec_result.stdout.strip()
        except Exception as e:
            raise RuntimeError(f'Error calling C++ function {function_name}: {str(e)}')

    def _compile_cpp_function(self, function_name, cpp_code):
        try:
            cpp_file = Path(self.temp_dir) / f'{function_name}.cpp'
            cpp_file.write_text(cpp_code)
            obj_file = cpp_file.with_suffix('.o')
            compile_result = subprocess.run(['g++', '-std=c++11', '-c', str(cpp_file), '-o', str(obj_file)], capture_output=True, text=True)
            if compile_result.returncode == 0:
                self.compiled_functions[function_name] = str(obj_file)
        except Exception as e:
            raise RuntimeError(f'Error compiling C++ function {function_name}: {str(e)}')

    def _create_cpp_wrapper(self, function_name, args):
        args_json = json.dumps(args)
        return f'\n\nextern "C" {{\n\n\n}}\n\nint main() {{\n    try {{\n\n        std::string argsJson = R"({args_json})";\n\n\n\n        std::cout << "{{ \\"result\\": 0 }}" << std::endl;\n\n        return 0;\n    }} catch (std::exception& e) {{\n        std::cerr << "Error: " << e.what() << std::endl;\n        return 1;\n    }}\n}}\n'

    def create_cpp_function_signature(self, function_name, return_type, param_types):
        params = []
        for i, ptype in enumerate(param_types):
            params.append({'name': f'arg{i}', 'type': ptype})
        return FunctionSignature(name=function_name, language='cpp', implementation=function_name, return_type=return_type, parameters=params)

    def convert_cpp_type(self, cpp_type, value):
        if cpp_type in ['int', 'int32_t', 'int64_t']:
            return int(value)
        elif cpp_type in ['float', 'double']:
            return float(value)
        elif cpp_type in ['std::string', 'string', 'char*']:
            return str(value)
        elif cpp_type in ['bool']:
            return bool(value)
        elif cpp_type in ['long', 'long long']:
            return int(value)
        else:
            return value

    def convert_from_cpp(self, cpp_type, value):
        if cpp_type in ['int', 'int32_t', 'int64_t', 'long', 'long long']:
            return int(value)
        elif cpp_type in ['float', 'double']:
            return float(value)
        elif cpp_type in ['std::string', 'string', 'char*']:
            return str(value)
        elif cpp_type in ['bool']:
            return bool(value)
        else:
            return value

    def create_extern_c_wrapper(self, cpp_code):
        return f'\n\nextern "C" {{\n{cpp_code}\n}}\n\nint main() {{\n\n    return 0;\n}}\n'

def create_cpp_adapter():
    return CppAdapter()
