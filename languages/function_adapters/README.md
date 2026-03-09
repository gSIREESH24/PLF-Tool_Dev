# 🔗 Function Adapters - Cross-Language Function Calling

This folder contains language-specific adapters that enable seamless function calling across all 5 supported languages.

## 📋 What Are Function Adapters?

Function adapters provide a clean interface to:
- **Call functions** written in one language from another language
- **Convert types** automatically between languages
- **Register and discover** functions across the system
- **Manage function metadata** (signatures, parameters, return types)

---

## 📁 Adapter Files

### **python_adapter.py** 🐍
**Call Python functions from other languages**

```python
from languages.function_adapters import create_python_adapter

adapter = create_python_adapter()

# Register a Python function
def add(a, b):
    return a + b

adapter.register_python_function('add', add)

# Call it from another language
result = adapter.call_python_function('add', [5, 10])  # 15
```

**Features:**
- Automatic function registration via introspection
- Type hint detection and extraction
- Function metadata introspection
- Conversion to appropriate Python types

---

### **js_adapter.py** 📜
**Call JavaScript functions from other languages**

```python
from languages.function_adapters import create_js_adapter

adapter = create_js_adapter()

js_code = '''
function multiply(a, b) {
    return a * b;
}
'''

# Call JavaScript function
result = adapter.call_js_function('multiply', [4, 5], js_code)  # 20
```

**Features:**
- Execute JavaScript via Node.js
- Regex-based function signature extraction
- Automatic type conversion (number, string, array, object)
- JSON-based result serialization

---

### **c_adapter.py** 🔧
**Call C functions from other languages**

```python
from languages.function_adapters import create_c_adapter

adapter = create_c_adapter()

c_code = '''
int square(int x) {
    return x * x;
}
'''

# Call C function
result = adapter.call_c_function('square', [7], c_code)  # 49
```

**Features:**
- Compile C code with GCC
- Function signature parsing
- Type conversion for C primitives (int, float, char*, etc.)
- Automatic cleanup of compiled files

---

### **java_adapter.py** ☕
**Call Java functions from other languages**

```python
from languages.function_adapters import create_java_adapter

adapter = create_java_adapter()

# Call Java static method
result = adapter.call_java_function('square', [6])  # 36
```

**Features:**
- Compile Java code with javac
- Static method detection and calling
- Java type conversion (Integer, Float, String, etc.)
- Marshalling for complex types

---

### **cpp_adapter.py** ⚙️
**Call C++ functions from other languages**

```python
from languages.function_adapters import create_cpp_adapter

adapter = create_cpp_adapter()

cpp_code = '''
int add(int a, int b) {
    return a + b;
}
'''

# Call C++ function
result = adapter.call_cpp_function('add', [15, 25], cpp_code)  # 40
```

**Features:**
- Compile C++ with g++
- extern "C" wrapping for C linkage
- C++ type support (int, float, std::string, etc.)
- STL container handling

---

## 🎯 Adapter Registry

Use the adapter registry to get adapters by language name:

```python
from languages.function_adapters import get_adapter, ADAPTER_REGISTRY

# Get adapter for a specific language
python_adapter = get_adapter('python')
js_adapter = get_adapter('javascript')
c_adapter = get_adapter('c')
java_adapter = get_adapter('java')
cpp_adapter = get_adapter('cpp')

# View all available adapters
print(ADAPTER_REGISTRY.keys())  # dict_keys(['python', 'javascript', 'c', 'java', 'cpp'])
```

---

## 🔄 Type Conversion

Each adapter handles type conversion between Python and the target language:

### **Python ↔ JavaScript**
| Python | JavaScript | Python |
|--------|------------|--------|
| `int` | `number` | `int` |
| `float` | `number` | `float` |
| `str` | `string` | `str` |
| `bool` | `boolean` | `bool` |
| `list` | `array` | `list` |
| `dict` | `object` | `dict` |

### **Python ↔ C**
| Python | C | Python |
|--------|---|--------|
| `int` | `int` | `int` |
| `float` | `float` | `float` |
| `str` | `char*` | `str` |
| `None` | `void` | `None` |

### **Python ↔ Java**
| Python | Java | Python |
|--------|------|--------|
| `int` | `Integer` | `int` |
| `float` | `Double` | `float` |
| `str` | `String` | `str` |
| `bool` | `Boolean` | `bool` |
| `list` | `ArrayList` | `list` |

### **Python ↔ C++**
| Python | C++ | Python |
|--------|-----|--------|
| `int` | `int` | `int` |
| `float` | `double` | `float` |
| `str` | `std::string` | `str` |
| `bool` | `bool` | `bool` |
| `list` | `vector<T>` | `list` |

---

## 📝 Creating a Function Signature

All adapters can create function signatures for introspection:

```python
# Python adapter
sig = adapter.create_python_function_signature('my_func', my_func_obj)

# JavaScript adapter
sig = adapter.create_js_function_signature('my_func', param_count=3)

# C adapter
sig = adapter.create_c_function_signature('my_func', 'int', ['int', 'int'])

# Java adapter
sig = adapter.create_java_function_signature('MyClass', 'square', 'int', ['int'])

# C++ adapter
sig = adapter.create_cpp_function_signature('multiply', 'int', ['int', 'int'])
```

---

## 🔍 Extracting Signatures

Adapters can parse code to extract function signatures:

```python
# JavaScript: Extract from code
info = js_adapter.extract_js_function_signature(js_code, 'functionName')

# C: Extract from code
info = c_adapter.extract_c_function_signature(c_code, 'functionName')
```

---

## 🚀 Integration with Function Registry

Adapters work with the central `FunctionRegistry`:

```python
from core.function_registry import FunctionRegistry
from languages.function_adapters import create_python_adapter

# Get registry and adapter
registry = FunctionRegistry.get_instance()
py_adapter = create_python_adapter()

# Register a Python function
def greet(name):
    return f"Hello, {name}!"

py_adapter.register_python_function('greet', greet)

# Now other languages can call it via registry
result = registry.call('greet', ['World'])  # "Hello, World!"
```

---

## 💡 Common Usage Patterns

### **Pattern 1: Direct Function Calling**
```python
adapter = get_adapter('java')
result = adapter.call_java_function('square', [5])
```

### **Pattern 2: Function Registration**
```python
py_adapter = get_adapter('python')
py_adapter.register_python_function('add', lambda a, b: a + b)
```

### **Pattern 3: Type Conversion**
```python
adapter = get_adapter('c')
c_value = adapter.convert_c_type('int', 42)  # Convert from Python
python_value = adapter.convert_from_c('int', c_value)  # Convert back
```

### **Pattern 4: Cross-Language Call Chain**
```python
# Define function in Python
py_adapter.register_python_function('process', my_process_func)

# Call from JavaScript
js_result = registry.call('process', [data_from_js])

# Use result in C
c_adapter.call_c_function('analyze', [js_result])
```

---

## 🧪 Testing Adapters

Each adapter is tested in `tests/test_java_cpp.py`:

```python
# Run tests
python tests/test_java_cpp.py

# Results show:
# ✓ Python → Java function calling
# ✓ JavaScript → C++ function calling
# ✓ Type conversion across all pairs
# ✓ Complex type handling
```

---

## 📚 API Reference

### **Common Adapter Methods**

All adapters implement these core methods:

```python
# Call a function
result = adapter.call_<language>_function(name, args, [code])

# Create signature
sig = adapter.create_<language>_function_signature(...)

# Convert types
converted = adapter.convert_<language>_type(type_name, value)

# Convert from language type
python_value = adapter.convert_from_<language>(type_name, value)
```

---

## ✅ Completeness

All adapters are:
- ✅ Fully implemented
- ✅ Type-safe with automatic conversion
- ✅ Integrated with function registry
- ✅ Tested thoroughly
- ✅ Well-documented

---

## 🎯 Next Steps

1. **Use adapters** in your cross-language projects
2. **Create function signatures** for introspection
3. **Register functions** in the global registry
4. **Call functions** from any language
5. **Extend adapters** for custom requirements

---

*Last Updated: March 10, 2026*
*Status: ✅ Complete for all 5 languages*
