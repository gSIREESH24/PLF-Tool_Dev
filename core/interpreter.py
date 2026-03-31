from core.context import Context
from core.function_registry import FunctionRegistry
from global_ns.builtins import register_builtins
from languages import LANGUAGE_REGISTRY

def interpret(program_node, registry=None):
    context = Context()
    if registry is None:
        registry = FunctionRegistry()
    register_builtins(registry)
    global_blocks = [b for b in program_node.blocks if getattr(b, 'is_global', False)]
    for block in global_blocks:
        lang = block.language
        code = block.code
        runner = LANGUAGE_REGISTRY.get(lang)
        if runner:
            try:
                runner(code, context, registry, is_global=True)
            except TypeError:
                try:
                    runner(code, context, registry)
                except TypeError:
                    try:
                        runner(code, context)
                    except TypeError:
                        runner(code)
    local_blocks = [b for b in program_node.blocks if not getattr(b, 'is_global', False)]
    for block in local_blocks:
        lang = block.language
        code = block.code
        print(f'\n=== {lang.upper()} ===')
        if lang == 'global':
            process_global(code, context, registry)
            continue
        runner = LANGUAGE_REGISTRY.get(lang)
        if runner:
            try:
                runner(code, context, registry, is_global=False)
            except TypeError:
                try:
                    runner(code, context, registry)
                except TypeError:
                    try:
                        runner(code, context)
                    except TypeError:
                        runner(code)
        else:
            print(f'Unsupported language: {lang}')
    return (context, registry)

def process_global(code, context, registry):
    for line in code.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('--'):
            continue
        if line.endswith('{') and line.lower() in ('python {', 'javascript {', 'c {', 'java {', 'cpp {'):
            continue
        if '=' in line and (not line.startswith('//')):
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            try:
                context.set(key, eval(value))
            except Exception as e:
                pass
