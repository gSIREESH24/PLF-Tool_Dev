# UNIFIED EXPORT MECHANISM - All 5 Languages

## Overview

All 5 languages now use the **same export pattern** for inter-language communication:
- Standardized function/macro naming
- Consistent POLY_EXPORT format
- Same types supported (primitives, arrays, objects)

---

## Quick Reference

| Language | Export Function | File | Usage |
|----------|-----------------|------|-------|
| **Python** | `export(name, value)` | `languages/python_lang.py` | `export("var", value)` |
| **C++** | `export_cpp(name, value)` | `languages/cpp_lang.py` | `export_cpp("var", value)` |
| **JavaScript** | `export_js(name, value)` | `languages/js_lang.py` | `export_js("var", value)` |
| **Java** | `export_java(name, value)` | `languages/java_lang.py` | `export_java("var", value)` |
| **C** | `EXPORT_DOUBLE/INT/STRING` | `languages/c_lang.py` | `EXPORT_DOUBLE("var", value)` |

---

## Detailed Usage by Language

### 1️⃣ PYTHON - Basic Export
**File:** `languages/python_lang.py`

```python
# Export primitives
export("count", 42)
export("name", "Hello")
export("values", [1, 2, 3])

# Export class instances (auto-converts to dict)
export("product", product_instance)

# Export dictionaries
export("config", {"key": "value"})
```

**What it stores in context:**
```python
context.variables = {
    "count": 42,
    "name": "Hello",
    "values": [1, 2, 3],
    "product": {"name": "Laptop", "price": 1200.50},
    "config": {"key": "value"}
}
```

---

### 2️⃣ C++ - Template-Based Export
**File:** `languages/cpp_lang.py`

```cpp
// Export primitives
export_cpp("count", 42);
export_cpp("value", 3.14);
export_cpp("flag", true);

// Export vectors
std::vector<double> data = {1.0, 2.0, 3.0};
export_cpp("data", data);

// Export strings
std::string name = "Hello";
export_cpp("name", name);

// Using EXPORT_VAR macro
EXPORT_VAR(result, calculated_value);
```

**Mechanism:**
- Outputs to stderr: `POLY_EXPORT:name=value`
- Parser captures and injects into context

**Example output:**
```
POLY_EXPORT:count=42
POLY_EXPORT:value=3.14
POLY_EXPORT:flag=1
POLY_EXPORT:data=[1,2,3]
POLY_EXPORT:name=Hello
```

---

### 3️⃣ JAVASCRIPT - JSON-Based Export
**File:** `languages/js_lang.py`

```javascript
// Export primitives
export_js("count", 42);
export_js("name", "Hello");
export_js("flag", true);

// Export arrays
export_js("values", [1, 2, 3, 4, 5]);

// Export objects
export_js("config", {key: "value", count: 10});

// Alternative naming
export_func("data", data);
```

**Mechanism:**
- Outputs to stderr via `console.error()`
- Arrays format: `[val1,val2,val3]`
- Objects format: `JSON.stringify(object)`

**Example output:**
```
POLY_EXPORT:count=42
POLY_EXPORT:name=Hello
POLY_EXPORT:values=[1,2,3,4,5]
POLY_EXPORT:config={"key":"value","count":10}
```

---

### 4️⃣ JAVA - StringBuilder Export
**File:** `languages/java_lang.py`

```java
// Export primitives
export_java("count", 42);
export_java("value", 3.14);
export_java("name", "Hello");

// Export ArrayList
ArrayList<Double> data = new ArrayList<>();
data.add(1.0); data.add(2.0); data.add(3.0);
export_java("data", data);

// Export objects
export_java("config", someObject);

// Alternative naming
export_func("result", result);
```

**Mechanism:**
- Outputs to stderr via `System.err.println()`
- Handles Integer, Double, Boolean, String, List
- Lists format: `[val1,val2,val3]`

**Example output:**
```
POLY_EXPORT:count=42
POLY_EXPORT:value=3.14
POLY_EXPORT:data=[1.0,2.0,3.0]
POLY_EXPORT:name=Hello
```

---

### 5️⃣ C - Macro-Based Export
**File:** `languages/c_lang.py`

```c
// Export using macros
EXPORT_DOUBLE("value", 3.14);
EXPORT_INT("count", 42);
EXPORT_STRING("name", "Hello");

// Using generic function (with type codes)
double val = 2.5;
export_c("result", &val, 0);  // 0 = double

int num = 10;
export_c("num", &num, 1);     // 1 = int

char* str = "text";
export_c("text", str, 2);     // 2 = string
```

**Mechanism:**
- Macros expand to `fprintf()` calls
- Outputs to stderr
- Supports macros for convenience

**Example output:**
```
POLY_EXPORT:value=3.140000
POLY_EXPORT:count=42
POLY_EXPORT:name=Hello
POLY_EXPORT:result=2.5
```

---

## Complete Example: All 5 Languages

### File: `examples/all_exports.poly`
```poly
global {
    python { dataset = [1, 2, 3, 4, 5] }
}

python {
    avg = sum(dataset) / len(dataset)
    export("average", avg)
    export("data_points", dataset)
}

cpp {
    export_cpp("cpp_result", data_points.size());
}

javascript {
    export_js("js_count", data_points.length);
}

java {
    export_java("java_size", data_points.size());
}

c {
    EXPORT_DOUBLE("c_value", average);
}

python {
    print(f"Average: {average}")
    print(f"Data: {data_points}")
    # Has access to all previous exports!
}
```

---

## Data Flow Diagram

```
┌──────────────────┐
│ Python Block 1   │
│ export("avg", 3) │
└────────┬─────────┘
         │ (POLY_EXPORT:avg=3)
         ▼
┌──────────────────┐
│ Context Store    │
│ avg = 3          │
└────────┬─────────┘
         │ (context.all())
         ▼
┌──────────────────┐
│ C++ Block        │
│ Has access to avg│
│ export_cpp(...)  │
└────────┬─────────┘
         │ (POLY_EXPORT:...)
         ▼
┌──────────────────┐
│ Context Store    │
│ (Updated)        │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
  JS Block  Java Block  C Block  Python Final
  (context available to all)
```

---

## Supported Data Types

| Type | Python | C++ | JS | Java | C |
|------|--------|-----|----|----|---|
| int | ✓ | ✓ | ✓ | ✓ | ✓ |
| float/double | ✓ | ✓ | ✓ | ✓ | ✓ |
| string | ✓ | ✓ | ✓ | ✓ | ✓ |
| list/array | ✓ | ✓ | ✓ | ✓ | ~ |
| bool | ✓ | ✓ | ✓ | ✓ | ~ |
| dict/object | ✓ | ~ | ✓ | ✓ | ~ |
| class instance | ✓ | ~ | ~ | ~ | ~ |

Legend: ✓ Full support | ~ Limited support | - No support

---

## Key Principles

1. **Consistent Naming**: All use `export_<lang>()` pattern
2. **Same Format**: All output `POLY_EXPORT:name=value`
3. **Same Types**: All support primitives + arrays
4. **Auto-Injection**: Next language automatically receives exported variables
5. **No Manual Passing**: Just use `export()`, framework handles the rest

---

## Common Patterns

### Pattern 1: Sequential Processing
```
Python (Process) → export → C++ (Analyze) → export → JS (Visualize)
```

### Pattern 2: Data Aggregation
```
All languages export → Python collects all results
```

### Pattern 3: Cross-Language Functions
```
Python (define logic) → JS/C++ (execute fast) → return results
```

---

## Troubleshooting

### "Variable not found in next language"
- Make sure you called `export()` in previous language
- Check variable name spelling
- Verify it's a supported type

### "POLY_EXPORT line in output"
- This is normal - it's the internal protocol
- Framework automatically filters these out
- Only visible in debug/stderr output

### "Class instance not converted"
- Works only in Python → other languages
- Other languages can't define classes easily
- Convert manually to dict first in those languages

---

## Design Pattern

```
def export(name, value):
    """
    Universal export pattern across all languages:
    
    1. Take variable (name + value)
    2. Output POLY_EXPORT:name=value to stderr
    3. Framework parses and injects into context
    4. Next language block receives via context.all()
    """
```

This creates **truly language-agnostic** data interchange! 🚀
