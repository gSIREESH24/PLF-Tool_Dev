"""
Test suite for Type Marshalling System
"""

from global_ns.marshalling import Marshaller, TypeConverter, get_converter


def test_python_to_js():
    """Test Python to JavaScript type conversion"""
    # Primitives
    assert Marshaller.python_to_js(None) is None
    assert Marshaller.python_to_js(True) is True
    assert Marshaller.python_to_js(42) == 42
    assert Marshaller.python_to_js(3.14) == 3.14
    assert Marshaller.python_to_js("hello") == "hello"
    
    # Collections
    assert Marshaller.python_to_js([1, 2, 3]) == [1, 2, 3]
    assert Marshaller.python_to_js({"key": "value"}) == {"key": "value"}
    
    print("✓ test_python_to_js passed")


def test_type_inference():
    """Test type inference"""
    assert Marshaller.infer_type(None) == "null"
    assert Marshaller.infer_type(True) == "bool"
    assert Marshaller.infer_type(42) == "int"
    assert Marshaller.infer_type(3.14) == "float"
    assert Marshaller.infer_type("hello") == "str"
    assert Marshaller.infer_type([1, 2]) == "list"
    assert Marshaller.infer_type({"a": 1}) == "dict"
    
    print("✓ test_type_inference passed")


def test_type_validation():
    """Test type validation"""
    # Valid types
    assert Marshaller.validate_type(42, "int") is True
    assert Marshaller.validate_type(3.14, "float") is True
    assert Marshaller.validate_type("hello", "str") is True
    assert Marshaller.validate_type(True, "bool") is True
    assert Marshaller.validate_type([1, 2], "list") is True
    assert Marshaller.validate_type({"a": 1}, "dict") is True
    
    # Invalid types
    assert Marshaller.validate_type(42, "str") is False
    assert Marshaller.validate_type("hello", "int") is False
    assert Marshaller.validate_type([1, 2], "dict") is False
    
    print("✓ test_type_validation passed")


def test_type_converter():
    """Test TypeConverter class"""
    converter = TypeConverter()
    
    # Python to JavaScript
    result = converter.convert([1, 2, 3], "python", "javascript")
    assert result == [1, 2, 3]
    
    # Same language
    result = converter.convert({"a": 1}, "python", "python")
    assert result == {"a": 1}
    
    print("✓ test_type_converter passed")


def test_get_converter():
    """Test global converter retrieval"""
    converter = get_converter()
    assert converter is not None
    
    # Same instance
    converter2 = get_converter()
    assert converter is converter2
    
    print("✓ test_get_converter passed")


def test_python_to_c():
    """Test Python to C type conversion"""
    assert Marshaller.python_to_c(None) == "NULL"
    assert Marshaller.python_to_c(True) == "true"
    assert Marshaller.python_to_c(False) == "false"
    assert Marshaller.python_to_c(42) == 42
    assert Marshaller.python_to_c(3.14) == 3.14
    assert Marshaller.python_to_c("hello") == '"hello"'
    
    print("✓ test_python_to_c passed")


if __name__ == "__main__":
    print("Running Marshalling Tests...\n")
    
    test_python_to_js()
    test_type_inference()
    test_type_validation()
    test_type_converter()
    test_get_converter()
    test_python_to_c()
    
    print("\n✓ All marshalling tests passed!")
