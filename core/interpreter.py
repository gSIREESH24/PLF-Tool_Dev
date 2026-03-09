from core.context import Context
from core.function_registry import FunctionRegistry
from global_ns.builtins import register_builtins
from languages import LANGUAGE_REGISTRY


def interpret(program_node, registry=None):
    """
    Enhanced interpreter with function registry support.
    
    Args:
        program_node: The parsed program AST
        registry: Optional FunctionRegistry instance (creates new if None)
    """
    context = Context()
    
    # Create or use provided registry
    if registry is None:
        registry = FunctionRegistry()
    
    # Register built-in functions
    register_builtins(registry)
    
    print("\n" + "="*50)
    print("POLY RUNTIME - Cross-Language Execution")
    print("="*50)
    
    for block in program_node.blocks:
        lang = block.language
        code = block.code

        print(f"\n=== Running {lang.upper()} ===")

        if lang == "global":
            process_global(code, context, registry)
            continue

        runner = LANGUAGE_REGISTRY.get(lang)

        if runner:
            try:
                # Pass both context and registry to the runner
                runner(code, context, registry)
            except TypeError:
                try:
                    # Try with just context
                    runner(code, context)
                except TypeError:
                    # Try with just code
                    runner(code)
        else:
            print(f"Unsupported language: {lang}")
    
    print("\n" + "="*50)
    print(f"Registry Summary:\n{registry.summary()}")
    print("="*50)
    
    return context, registry


def process_global(code, context, registry):
    """
    Process global block - shared variables and imports.
    
    Args:
        code: Code to process
        context: The shared context
        registry: The function registry
    """
    for line in code.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if "=" in line and not line.startswith("//"):
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            try:
                context.set(key, eval(value))
                print(f"  Set global: {key} = {value}")
            except Exception as e:
                print(f"  Error setting {key}: {e}")
