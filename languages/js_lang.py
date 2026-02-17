import subprocess
import json

def run(code, context):
    js_vars = ""

    for key, value in context.all().items():
        if key.startswith("__"):
            continue

        try:
            js_value = json.dumps(value)
            js_vars += f"var {key} = {js_value};\n"
        except TypeError:
            continue

    full_code = js_vars + code
    subprocess.run(["node", "-e", full_code])
