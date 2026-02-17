from core.context import Context
from languages import LANGUAGE_REGISTRY

def interpret(program_node):
    context = Context()

    for block in program_node.blocks:
        lang = block.language
        code = block.code

        print(f"\n=== Running {lang.upper()} ===")

        if lang == "global":
            process_global(code, context)
            continue

        runner = LANGUAGE_REGISTRY.get(lang)

        if runner:
            try:
                runner(code, context)
            except TypeError:
                runner(code)
        else:
            print(f"Unsupported language: {lang}")


def process_global(code, context):
    for line in code.splitlines():
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            context.set(key.strip(), eval(value.strip()))
