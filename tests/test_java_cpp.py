"""
Test suite for Java and C++ Language Support
"""

from core.function_registry import FunctionRegistry
from core.function_signature import FunctionSignature, Parameter
from languages.java_lang import _parse_java_params, _parse_single_java_param
from languages.cpp_lang import _parse_cpp_params, _parse_single_cpp_param


def test_java_parameter_parsing():
    """Test Java parameter parsing"""
    
    # Test basic types
    param = _parse_single_java_param("int a")
    assert param.name == "a"
    assert param.type_hint == "int"
    
    # Test String type
    param = _parse_single_java_param("String name")
    assert param.name == "name"
    assert param.type_hint == "String"
    
    # Test generic types
    param = _parse_single_java_param("List<String> items")
    assert param.name == "items"
    assert "List" in param.type_hint
    
    # Test variadic
    param = _parse_single_java_param("int... numbers")
    assert param.name == "numbers"
    assert param.is_variadic is True
    
    print("✓ test_java_parameter_parsing passed")


def test_java_params_list():
    """Test parsing multiple Java parameters"""
    params_str = "int x, String name, double value"
    params = _parse_java_params(params_str)
    
    assert len(params) == 3
    assert params[0].name == "x"
    assert params[0].type_hint == "int"
    assert params[1].name == "name"
    assert params[1].type_hint == "String"
    assert params[2].name == "value"
    assert params[2].type_hint == "double"
    
    print("✓ test_java_params_list passed")


def test_cpp_parameter_parsing():
    """Test C++ parameter parsing"""
    
    # Test basic types
    param = _parse_single_cpp_param("int a")
    assert param.name == "a"
    assert param.type_hint == "int"
    
    # Test pointer
    param = _parse_single_cpp_param("int* ptr")
    assert param.name == "ptr"
    assert "int*" in param.type_hint
    
    # Test reference
    param = _parse_single_cpp_param("const std::string& text")
    assert param.name == "text"
    assert "string" in param.type_hint
    assert "&" in param.type_hint
    
    # Test template
    param = _parse_single_cpp_param("std::vector<int> arr")
    assert param.name == "arr"
    assert "vector" in param.type_hint
    
    # Test default value
    param = _parse_single_cpp_param("int count = 10")
    assert param.name == "count"
    assert param.default == 10
    
    print("✓ test_cpp_parameter_parsing passed")


def test_cpp_params_list():
    """Test parsing multiple C++ parameters"""
    params_str = "int x, const std::string& name, double y = 3.14"
    params = _parse_cpp_params(params_str)
    
    assert len(params) == 3
    assert params[0].name == "x"
    assert params[1].name == "name"
    assert params[2].name == "y"
    assert params[2].default == 3.14
    
    print("✓ test_cpp_params_list passed")


def test_java_function_signature():
    """Test Java function signature creation"""
    sig = FunctionSignature(
        name="add",
        language="java",
        parameters=[
            Parameter(name="a", type_hint="int"),
            Parameter(name="b", type_hint="int")
        ],
        return_type="int"
    )
    
    assert sig.name == "add"
    assert sig.language == "java"
    assert len(sig.parameters) == 2
    assert sig.arity() == 2
    
    print("✓ test_java_function_signature passed")


def test_cpp_function_signature():
    """Test C++ function signature creation"""
    sig = FunctionSignature(
        name="calculate",
        language="cpp",
        parameters=[
            Parameter(name="x", type_hint="double"),
            Parameter(name="y", type_hint="double", default=1.0)
        ],
        return_type="double"
    )
    
    assert sig.name == "calculate"
    assert sig.language == "cpp"
    assert len(sig.parameters) == 2
    assert sig.arity() == 1  # Only x is required
    assert sig.max_arity() == 2
    
    print("✓ test_cpp_function_signature passed")


def test_registry_with_java_cpp():
    """Test registry with Java and C++ functions"""
    registry = FunctionRegistry()
    
    # Register Java function
    java_sig = FunctionSignature(
        name="javaMultiply",
        language="java",
        parameters=[
            Parameter(name="a", type_hint="int"),
            Parameter(name="b", type_hint="int")
        ],
        return_type="int"
    )
    registry.register(java_sig)
    
    # Register C++ function
    cpp_sig = FunctionSignature(
        name="cppAdd",
        language="cpp",
        parameters=[
            Parameter(name="x", type_hint="double"),
            Parameter(name="y", type_hint="double")
        ],
        return_type="double"
    )
    registry.register(cpp_sig)
    
    # List by language
    java_funcs = registry.list_by_language("java")
    cpp_funcs = registry.list_by_language("cpp")
    
    assert "javaMultiply" in java_funcs
    assert "cppAdd" in cpp_funcs
    
    print("✓ test_registry_with_java_cpp passed")


def test_java_cpp_in_summary():
    """Test that Java and C++ functions appear in registry summary"""
    registry = FunctionRegistry()
    
    sig1 = FunctionSignature(
        name="javaFunc",
        language="java",
        return_type="int"
    )
    sig2 = FunctionSignature(
        name="cppFunc",
        language="cpp",
        return_type="void"
    )
    
    registry.register(sig1)
    registry.register(sig2)
    
    summary = registry.summary()
    
    assert "javaFunc" in summary
    assert "cppFunc" in summary
    assert "java" in summary.lower() or "Java" in summary
    assert "cpp" in summary.lower() or "C++" in summary
    
    print("✓ test_java_cpp_in_summary passed")


if __name__ == "__main__":
    print("Running Java and C++ Language Support Tests...\n")
    
    test_java_parameter_parsing()
    test_java_params_list()
    test_cpp_parameter_parsing()
    test_cpp_params_list()
    test_java_function_signature()
    test_cpp_function_signature()
    test_registry_with_java_cpp()
    test_java_cpp_in_summary()
    
    print("\n✓ All Java and C++ tests passed!")
