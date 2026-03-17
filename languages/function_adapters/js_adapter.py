import subprocess
import json
import tempfile
from pathlib import Path
from core.function_signature import FunctionSignature

class JavaScriptAdapter:

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def call_js_function(self, function_name, args, js_code=None):
        try:

            wrapper_code = self._create_js_wrapper(function_name, args, js_code)

            wrapper_file = Path(self.temp_dir) / "js_wrapper.js"
            wrapper_file.write_text(wrapper_code)

            exec_result = subprocess.run(
                ["node", str(wrapper_file)],
                capture_output=True, text=True
            )

            if exec_result.returncode != 0:
                raise RuntimeError(f"JavaScript execution error: {exec_result.stderr}")

            try:
                return json.loads(exec_result.stdout)
            except:
                return exec_result.stdout.strip()

        except Exception as e:
            raise RuntimeError(f"Error calling JavaScript function {function_name}: {str(e)}")

    def _create_js_wrapper(self, function_name, args, js_code=None):
        args_str = json.dumps(args)

        code_section = f"// Function code will be executed here\n{js_code}" if js_code else ""

        return f"""
{code_section}

// Call the function and output result as JSON
try {{
    const args = {args_str};
    const result = {function_name}(...args);
    console.log(JSON.stringify({{result: result}}));
}} catch (error) {{
    console.error(JSON.stringify({{error: error.message}}));
    process.exit(1);
}}
"""

    def create_js_function_signature(self, function_name, param_count=0):
        params = []
        for i in range(param_count):
            params.append({'name': f'arg{i}', 'type': 'any'})

        return FunctionSignature(
            name=function_name,
            language='javascript',
            implementation=function_name,
            return_type='any',
            parameters=params
        )

    def convert_js_type(self, target_type, value):
        if target_type in ['number']:
            return int(value) if isinstance(value, float) and value.is_integer() else float(value)
        elif target_type in ['string']:
            return str(value)
        elif target_type in ['boolean']:
            return bool(value)
        elif target_type in ['array']:
            return list(value) if not isinstance(value, list) else value
        elif target_type in ['object']:
            return dict(value) if not isinstance(value, dict) else value
        else:
            return value

    def convert_from_js(self, js_type, value):
        if js_type in ['number']:
            return int(value) if isinstance(value, float) and value.is_integer() else float(value)
        elif js_type in ['string']:
            return str(value)
        elif js_type in ['boolean']:
            return bool(value)
        elif js_type in ['array']:
            return list(value) if isinstance(value, (list, tuple)) else [value]
        elif js_type in ['object']:
            return dict(value) if isinstance(value, dict) else value
        else:
            return value

    def extract_js_function_signature(self, js_code, function_name):
        import re

        patterns = [
            rf'function\s+{function_name}\s*\((.*?)\)',
            rf'const\s+{function_name}\s*=\s*\((.*?)\)',
            rf'let\s+{function_name}\s*=\s*\((.*?)\)',
            rf'{function_name}\s*:\s*\((.*?)\)'
        ]

        for pattern in patterns:
            match = re.search(pattern, js_code)
            if match:
                params = match.group(1).split(',')
                params = [p.strip() for p in params if p.strip()]

                return {
                    'name': function_name,
                    'parameters': params,
                    'parameter_count': len(params)
                }

        return {
            'name': function_name,
            'parameters': [],
            'parameter_count': 0
        }

def create_js_adapter():
    return JavaScriptAdapter()