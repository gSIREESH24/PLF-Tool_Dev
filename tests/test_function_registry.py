from core.function_registry import FunctionRegistry, FunctionNotFoundError, InvalidFunctionCallError
from core.function_signature import FunctionSignature, Parameter

def test_register_and_get():
    registry = FunctionRegistry()

    def test_func(x):
        return x * 2

    sig = FunctionSignature(
        name="test",
        language="python",
        callable=test_func
    )

    registry.register(sig)

    retrieved = registry.get("test")
    assert retrieved.name == "test"
    assert retrieved.callable(5) == 10
    print("✓ test_register_and_get passed")

def test_function_not_found():
    registry = FunctionRegistry()

    try:
        registry.get("nonexistent")
        assert False, "Should raise FunctionNotFoundError"
    except FunctionNotFoundError:
        print("✓ test_function_not_found passed")

def test_call_function():
    registry = FunctionRegistry()

    def add(a, b):
        return a + b

    sig = FunctionSignature(
        name="add",
        language="python",
        parameters=[
            Parameter(name="a", type_hint="int"),
            Parameter(name="b", type_hint="int")
        ],
        return_type="int",
        callable=add
    )

    registry.register(sig)

    result = registry.call("add", [5, 10])
    assert result == 15
    print("✓ test_call_function passed")

def test_list_functions():
    registry = FunctionRegistry()

    def func1():
        return 1

    def func2():
        return 2

    sig1 = FunctionSignature(name="func1", language="python", callable=func1)
    sig2 = FunctionSignature(name="func2", language="python", callable=func2)

    registry.register(sig1)
    registry.register(sig2)

    functions = registry.list_functions()
    assert len(functions) == 2
    assert "func1" in functions
    assert "func2" in functions
    print("✓ test_list_functions passed")

def test_list_by_language():
    registry = FunctionRegistry()

    sig_py = FunctionSignature(name="py_func", language="python", callable=lambda: None)
    sig_js = FunctionSignature(name="js_func", language="javascript", callable=None)

    registry.register(sig_py)
    registry.register(sig_js)

    py_funcs = registry.list_by_language("python")
    js_funcs = registry.list_by_language("javascript")

    assert "py_func" in py_funcs
    assert "js_func" in js_funcs
    print("✓ test_list_by_language passed")

def test_function_info():
    registry = FunctionRegistry()

    def multiply(x, y):
        return x * y

    sig = FunctionSignature(
        name="multiply",
        language="python",
        parameters=[
            Parameter(name="x", type_hint="int"),
            Parameter(name="y", type_hint="int")
        ],
        return_type="int",
        callable=multiply,
        doc="Multiply two numbers"
    )

    registry.register(sig)
    info = registry.info("multiply")

    assert info["name"] == "multiply"
    assert info["language"] == "python"
    assert info["return_type"] == "int"
    assert info["arity"] == 2
    print("✓ test_function_info passed")

def test_arity():
    sig = FunctionSignature(
        name="test",
        language="python",
        parameters=[
            Parameter(name="a"),
            Parameter(name="b", default=10),
            Parameter(name="c", default=20)
        ]
    )

    assert sig.arity() == 1
    assert sig.max_arity() == 3
    print("✓ test_arity passed")

if __name__ == "__main__":
    print("Running Function Registry Tests...\n")

    test_register_and_get()
    test_function_not_found()
    test_call_function()
    test_list_functions()
    test_list_by_language()
    test_function_info()
    test_arity()

    print("\n✓ All tests passed!")