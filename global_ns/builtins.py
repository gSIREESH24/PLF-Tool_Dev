"""
Global Namespace - Built-in functions and utilities available to all languages
"""

from core.function_registry import FunctionRegistry
from core.function_signature import FunctionSignature, Parameter


def register_builtins(registry: FunctionRegistry) -> None:
    """
    Register built-in functions available to all languages.
    
    Args:
        registry: The FunctionRegistry instance
    """
    
    # Built-in: print (proxy)
    def builtin_print(*args):
        """Print values to console"""
        output = " ".join(str(arg) for arg in args)
        print(output)
        return None
    
    builtin_print_sig = FunctionSignature(
        name="builtin_print",
        language="python",
        parameters=[Parameter(name="args", is_variadic=True)],
        return_type="None",
        scope="global",
        callable=builtin_print,
        doc="Print values to console (variadic)"
    )
    registry.register(builtin_print_sig, scope="global")
    
    # Built-in: len
    def builtin_len(obj):
        """Get length of object"""
        return len(obj)
    
    builtin_len_sig = FunctionSignature(
        name="builtin_len",
        language="python",
        parameters=[Parameter(name="obj")],
        return_type="int",
        scope="global",
        callable=builtin_len,
        doc="Return the length of an object"
    )
    registry.register(builtin_len_sig, scope="global")
    
    # Built-in: type
    def builtin_type(obj):
        """Get type of object"""
        return type(obj).__name__
    
    builtin_type_sig = FunctionSignature(
        name="builtin_type",
        language="python",
        parameters=[Parameter(name="obj")],
        return_type="str",
        scope="global",
        callable=builtin_type,
        doc="Return the type of an object"
    )
    registry.register(builtin_type_sig, scope="global")
    
    # Built-in: abs
    def builtin_abs(x):
        """Return absolute value"""
        return abs(x)
    
    builtin_abs_sig = FunctionSignature(
        name="builtin_abs",
        language="python",
        parameters=[Parameter(name="x", type_hint="int|float")],
        return_type="int|float",
        scope="global",
        callable=builtin_abs,
        doc="Return the absolute value of a number"
    )
    registry.register(builtin_abs_sig, scope="global")
    
    # Built-in: max
    def builtin_max(*args):
        """Return maximum value"""
        return max(args)
    
    builtin_max_sig = FunctionSignature(
        name="builtin_max",
        language="python",
        parameters=[Parameter(name="args", is_variadic=True)],
        return_type="any",
        scope="global",
        callable=builtin_max,
        doc="Return the maximum value from arguments"
    )
    registry.register(builtin_max_sig, scope="global")
    
    # Built-in: min
    def builtin_min(*args):
        """Return minimum value"""
        return min(args)
    
    builtin_min_sig = FunctionSignature(
        name="builtin_min",
        language="python",
        parameters=[Parameter(name="args", is_variadic=True)],
        return_type="any",
        scope="global",
        callable=builtin_min,
        doc="Return the minimum value from arguments"
    )
    registry.register(builtin_min_sig, scope="global")
    
    # Built-in: sum
    def builtin_sum(iterable, start=0):
        """Sum values in an iterable"""
        return sum(iterable, start)
    
    builtin_sum_sig = FunctionSignature(
        name="builtin_sum",
        language="python",
        parameters=[
            Parameter(name="iterable"),
            Parameter(name="start", type_hint="int", default=0)
        ],
        return_type="int|float",
        scope="global",
        callable=builtin_sum,
        doc="Return the sum of values in an iterable"
    )
    registry.register(builtin_sum_sig, scope="global")
