import subprocess
import json
import tempfile
from pathlib import Path
from core.function_signature import FunctionSignature

class JavaAdapter:

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def call_java_function(self, function_name, args, java_class=None):
        try:
            wrapper_code = self._create_java_wrapper(function_name, args, java_class)
            wrapper_file = Path(self.temp_dir) / 'JavaWrapper.java'
            wrapper_file.write_text(wrapper_code)
            compile_result = subprocess.run(['javac', str(wrapper_file)], capture_output=True, text=True)
            if compile_result.returncode != 0:
                raise RuntimeError(f'Java wrapper compilation error: {compile_result.stderr}')
            exec_result = subprocess.run(['java', '-cp', str(self.temp_dir), 'JavaWrapper'], capture_output=True, text=True)
            if exec_result.returncode != 0:
                raise RuntimeError(f'Java execution error: {exec_result.stderr}')
            try:
                return json.loads(exec_result.stdout)
            except:
                return exec_result.stdout.strip()
        except Exception as e:
            raise RuntimeError(f'Error calling Java function {function_name}: {str(e)}')

    def _create_java_wrapper(self, function_name, args, java_class):
        args_json = json.dumps(args)
        return f'''\nimport java.util.*;\n\npublic class JavaWrapper {{\n    public static void main(String[] args) {{\n        try {{\n\n            String argsJson = '{args_json}';\n\n            Object result = callFunction("{function_name}", argsJson);\n\n            System.out.println(jsonEncode(result));\n        }} catch (Exception e) {{\n            e.printStackTrace();\n        }}\n    }}\n\n    private static Object callFunction(String name, String argsJson) throws Exception {{\n\n\n        return null;\n    }}\n\n    private static String jsonEncode(Object obj) {{\n        if (obj == null) return "null";\n        if (obj instanceof String) return "\\"" + obj + "\\"";\n        if (obj instanceof Number) return obj.toString();\n        if (obj instanceof List) {{\n            List<?> list = (List<?>) obj;\n            StringBuilder sb = new StringBuilder("[");\n            for (int i = 0; i < list.size(); i++) {{\n                if (i > 0) sb.append(",");\n                sb.append(jsonEncode(list.get(i)));\n            }}\n            sb.append("]");\n            return sb.toString();\n        }}\n        return obj.toString();\n    }}\n}}\n'''

    def create_java_function_signature(self, java_class, method_name, return_type, param_types):
        params = []
        for i, ptype in enumerate(param_types):
            params.append({'name': f'arg{i}', 'type': ptype})
        return FunctionSignature(name=method_name, language='java', implementation=f'{java_class}.{method_name}', return_type=return_type, parameters=params)

    def convert_java_type(self, java_type, value):
        if java_type in ['int', 'Integer']:
            return int(value)
        elif java_type in ['float', 'Float', 'double', 'Double']:
            return float(value)
        elif java_type in ['String']:
            return str(value)
        elif java_type in ['boolean', 'Boolean']:
            return bool(value)
        elif java_type in ['long', 'Long']:
            return int(value)
        elif java_type in ['short', 'Short']:
            return int(value)
        else:
            return value

    def convert_from_java(self, java_type, value):
        if java_type in ['int', 'Integer', 'long', 'Long', 'short', 'Short']:
            return int(value)
        elif java_type in ['float', 'Float', 'double', 'Double']:
            return float(value)
        elif java_type in ['String']:
            return str(value)
        elif java_type in ['boolean', 'Boolean']:
            return bool(value)
        else:
            return value

def create_java_adapter():
    return JavaAdapter()
