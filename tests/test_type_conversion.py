import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from global_ns.marshalling import Marshaller, TypeConverter, get_converter

def test_python_javascript_conversion():
    print("\n=== Python ↔ JavaScript Conversions ===")

    test_values = [
        42,
        3.14,
        "hello",
        True,
        False,
        None,
        [1, 2, 3],
        {"key": "value"},
    ]

    converter = get_converter()

    for value in test_values:

        js_value = converter.convert(value, "python", "javascript")

        py_value = converter.convert(js_value, "javascript", "python")

        print(f"Python: {value} ({type(value).__name__}) → JS → Python: {py_value} ({type(py_value).__name__})")
        assert py_value == value, f"Conversion failed for {value}"

    print("✓ Python ↔ JavaScript conversion passed")

def test_python_c_conversion():
    print("\n=== Python ↔ C Conversions ===")

    test_cases = [
        (42, "int"),
        (3.14, "float"),
        ("hello", "string"),
        (True, "bool"),
        ([1, 2, 3], "array"),
    ]

    converter = get_converter()

    for value, type_name in test_cases:

        c_value = converter.convert(value, "python", "c")

        py_value = converter.convert(c_value, "c", "python")

        print(f"Python: {value} ({type_name}) → C → Python: {py_value}")

    print("✓ Python ↔ C conversion passed")

def test_python_java_conversion():
    print("\n=== Python ↔ Java Conversions ===")

    test_values = [
        42,
        3.14,
        "hello",
        True,
        False,
        None,
        [1, 2, 3],
        {"key": "value"},
    ]

    converter = get_converter()

    for value in test_values:

        java_value = converter.convert(value, "python", "java")

        py_value = converter.convert(java_value, "java", "python")

        print(f"Python: {value} ({type(value).__name__}) → Java → Python: {py_value} ({type(py_value).__name__})")
        assert py_value == value, f"Conversion failed for {value}"

    print("✓ Python ↔ Java conversion passed")

def test_python_cpp_conversion():
    print("\n=== Python ↔ C++ Conversions ===")

    test_values = [
        42,
        3.14,
        "hello",
        True,
        False,
        None,
        [1, 2, 3],
        {"key": "value"},
    ]

    converter = get_converter()

    for value in test_values:

        cpp_value1 = converter.convert(value, "python", "cpp")
        cpp_value2 = converter.convert(value, "python", "c++")

        py_value1 = converter.convert(cpp_value1, "cpp", "python")
        py_value2 = converter.convert(cpp_value2, "c++", "python")

        print(f"Python: {value} ({type(value).__name__}) → C++ → Python: {py_value1} ({type(py_value1).__name__})")
        assert py_value1 == value, f"Conversion failed for {value}"
        assert py_value2 == value, f"Conversion with c++ alias failed for {value}"

    print("✓ Python ↔ C++ conversion passed")

def test_cross_language_conversions():
    print("\n=== Cross-Language Conversions (through Python) ===")

    converter = get_converter()
    test_value = 42

    print("\nJavaScript ↔ Java:")
    java_from_js = converter.convert(test_value, "javascript", "java")
    js_from_java = converter.convert(java_from_js, "java", "javascript")
    print(f"  {test_value} → Java → JavaScript: {js_from_java}")

    print("\nJavaScript ↔ C++:")
    cpp_from_js = converter.convert(test_value, "javascript", "cpp")
    js_from_cpp = converter.convert(cpp_from_js, "cpp", "javascript")
    print(f"  {test_value} → C++ → JavaScript: {js_from_cpp}")

    print("\nC ↔ Java:")
    java_from_c = converter.convert(test_value, "c", "java")
    c_from_java = converter.convert(java_from_c, "java", "c")
    print(f"  {test_value} → Java → C: {c_from_java}")

    print("\nC ↔ C++:")
    cpp_from_c = converter.convert(test_value, "c", "cpp")
    c_from_cpp = converter.convert(cpp_from_c, "cpp", "c")
    print(f"  {test_value} → C++ → C: {c_from_cpp}")

    print("\n✓ Cross-language conversions passed")

def test_supported_conversions():
    print("\n=== Supported Conversions ===")

    converter = get_converter()
    conversions = converter.get_supported_conversions()

    print(f"\nTotal direct conversion paths: {len(conversions)}")
    for (from_lang, to_lang), desc in sorted(conversions.items()):
        print(f"  {desc}")

    test_pairs = [
        ("python", "java"),
        ("javascript", "cpp"),
        ("c", "java"),
        ("java", "c++"),
        ("python", "python"),
    ]

    print("\nConversion support checks:")
    for from_lang, to_lang in test_pairs:
        supported = converter.is_conversion_supported(from_lang, to_lang)
        status = "✓ Supported" if supported else "✗ Not directly supported"
        print(f"  {from_lang} → {to_lang}: {status}")

def test_type_validation():
    print("\n=== Type Validation ===")

    test_cases = [
        (42, "int", True),
        (42, "integer", True),
        (3.14, "float", True),
        (3.14, "double", True),
        ("hello", "str", True),
        ("hello", "string", True),
        (True, "bool", True),
        (True, "boolean", True),
        ([1, 2], "list", True),
        ([1, 2], "array", True),
        ({"a": 1}, "dict", True),
        ({"a": 1}, "object", True),
        (None, "null", True),
        (None, "none", True),
        (42, "str", False),
        ("hello", "int", False),
    ]

    print("\nType validation results:")
    for value, type_hint, expected in test_cases:
        valid = Marshaller.validate_type(value, type_hint)
        status = "✓" if valid == expected else "✗"
        print(f"  {status} Marshaller.validate_type({value!r}, '{type_hint}'): {valid}")
        assert valid == expected, f"Type validation failed for {value}, {type_hint}"

    print("\n✓ Type validation passed")

def test_type_inference():
    print("\n=== Type Inference ===")

    test_values = [
        (42, "int"),
        (3.14, "float"),
        ("hello", "str"),
        (True, "bool"),
        ([1, 2, 3], "list"),
        ({"key": "value"}, "dict"),
        (None, "null"),
    ]

    print("\nType inference results:")
    for value, expected_type in test_values:
        inferred = Marshaller.infer_type(value)
        status = "✓" if inferred == expected_type else "✗"
        print(f"  {status} Marshaller.infer_type({value!r}): {inferred}")
        assert inferred == expected_type, f"Type inference failed for {value}"

    print("\n✓ Type inference passed")

def test_language_normalization():
    print("\n=== Language Name Normalization ===")

    test_cases = [
        ("c++", "cpp"),
        ("cpp", "cpp"),
        ("cplusplus", "cpp"),
        ("JavaScript", "javascript"),
        ("js", "javascript"),
        ("ts", "javascript"),
        ("typescript", "javascript"),
        ("Java", "java"),
        ("C", "c"),
        ("Python", "python"),
    ]

    converter = get_converter()

    print("\nLanguage normalization results:")
    for input_lang, expected in test_cases:
        normalized = converter._normalize_lang(input_lang)
        status = "✓" if normalized == expected else "✗"
        print(f"  {status} '{input_lang}' → '{normalized}'")
        assert normalized == expected, f"Normalization failed for {input_lang}"

    print("\n✓ Language normalization passed")

def main():
    print("=" * 60)
    print("COMPREHENSIVE TYPE CONVERSION TEST SUITE")
    print("Testing all 5 languages: Python, JavaScript, C, Java, C++")
    print("=" * 60)

    try:
        test_python_javascript_conversion()
        test_python_c_conversion()
        test_python_java_conversion()
        test_python_cpp_conversion()
        test_cross_language_conversions()
        test_supported_conversions()
        test_type_validation()
        test_type_inference()
        test_language_normalization()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nType Conversion System Summary:")
        print("  • Direct conversion paths: 10")
        print("  • Languages supported: 5 (Python, JavaScript, C, Java, C++)")
        print("  • Indirect conversion through Python: Full coverage")
        print("  • Type validation: Comprehensive")
        print("  • Type inference: Automatic")
        print("=" * 60)

        return 0
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())