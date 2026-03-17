# Global Functions & Cross-Language Calling

## Overview
The Polyglot framework now supports **global scope functions** that can be defined once and used across all languages.

## Syntax

### Global Block with Nested Language
```poly
global {
    python {
        def add(a, b):
            return a + b
    }
}
```

### Accessing Global Functions
Once defined in a global block, functions are automatically registered and can be:

1. **Called directly in Python**:
```python
python {
    result = add(5, 10)  # Direct call
}
```

2. **Called via registry** (any language with call support):
```python
python {
    result = call('add', [5, 10])  # Registry call
}
```

## Function Scope

### Global Scope Functions
- Defined inside `global { language { ... } }` blocks
- Automatically registered globally
- Accessible from all language blocks
- Persist throughout execution

### Local Scope Functions
- Defined inside language blocks (not in global)
- Only accessible within that language block
- Can use registry to call other functions

## Type Conversions

The framework automatically converts types between languages:

| Python | JavaScript | C | C++ | Java |
|--------|-----------|---|-----|------|
| list | array | array | vector | ArrayList |
| dict | object | struct | map | HashMap |
| str | string | char* | string | String |
| int | number | int | int | Integer |
| float | number | float | float | Float |
| bool | boolean | int | bool | Boolean |

## Examples

### Example 1: Simple Global Function
```poly
global {
    python {
        def multiply(a, b):
            return a * b
    }
}

python {
    print(multiply(5, 6))  # 30
}
```

### Example 2: Array Processing
```poly
global {
    python {
        def sum_array(numbers):
            return sum(numbers)
        
        def average(numbers):
            return sum(numbers) / len(numbers)
    }
}

python {
    data = [10, 20, 30, 40]
    total = sum_array(data)      # 100
    avg = average(data)           # 25
    print(f"Sum: {total}, Avg: {avg}")
}
```

### Example 3: Cross-Language Execution
```poly
global {
    python {
        def process(x):
            return x * 2
    }
}

python {
    result = process(10)  # 20
    print(f"Result: {result}")
}

javascript {
    // Global functions are registered
    // JavaScript can access them via registry
    console.log("Processing complete");
}
```

## Best Practices

1. **Define reusable functions in global**:
   - Common utilities
   - Data converters
   - Validators

2. **Use Python for global definitions**:
   - Most flexible
   - Easiest to integrate
   - Best type inference

3. **Call via direct name in Python**:
   - Faster execution
   - Cleaner code
   - Full IDE support

4. **Use registry calls when needed**:
   - Multi-language scenarios
   - Dynamic function names
   - Cross-language integration

## Running Examples

```bash
# Simple global functions
poly examples\global_functions.poly

# Cross-language with conversions
poly examples\global_crosslang.poly
```

## Limitations & Future Work

### Current
- Global functions defined in any language are registered globally
- Python functions are fully callable from all scopes
- Type conversions handled by Marshaller

### Planned
- Direct C++ → Python function calls (with wrapper generation)
- Direct Java → Python FFI
- Custom type mapping per function
- Performance optimizations for repeated calls
