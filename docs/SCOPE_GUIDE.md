# Global vs Local Scope - Complete Guide

## Core Concepts

### Global Scope
Functions and variables defined inside `global { language { ... } }` blocks:
- ✅ Accessible from ALL language blocks
- ✅ Can be multiple languages within one global block
- ✅ Persist throughout entire execution
- ✅ Registered in global function registry

### Local Scope  
Functions defined inside regular language blocks:
- ❌ Only accessible within that language
- ❌ Cannot be called from other languages
- ✅ Can use global functions from other languages
- ✅ Have access to global variables

---

## Syntax

### Global Block with Multiple Languages
```poly
global {
    python {
        def func1():
            pass
    }
    
    javascript {
        function func2() {}
    }
    
    variable1 = "value"
    variable2 = 42
}
```

### Local Block
```poly
python {
    def local_func():  # Only in Python
        pass
}

javascript {
    function local_js_func() {}  // Only in JavaScript
}
```

---

## Key Rules

### Rule 1: Global Functions Work Everywhere
```poly
global {
    python {
        def add(a, b):
            return a + b
    }
}

python {
    print(add(5, 10))  # ✅ Works
}

javascript {
    console.log("add function is in registry");  // ✅ Can access
}
```

### Rule 2: Local Functions Stay Local
```poly
python {
    def only_python_func():
        return "hello"
}

python {
    print(only_python_func())  # ✅ Works (same language)
}

javascript {
    // ❌ Cannot call only_python_func() here
}
```

### Rule 3: Global Variables Accessible Everywhere
```poly
global {
    config_timeout = 5000
    app_name = "MyApp"
    
    python {
        def get_config():
            return config_timeout
    }
}

python {
    print(app_name)       # ✅ "MyApp"
    print(config_timeout) # ✅ 5000
}

javascript {
    console.log(app_name);       // ✅ "MyApp"  
    console.log(config_timeout); // ✅ 5000
}
```

### Rule 4: Multiple Languages in Global
```poly
global {
    # Python utilities
    python {
        def py_func(x):
            return x * 2
    }
    
    # JavaScript utilities  
    javascript {
        function js_func(x) {
            return x * 3;
        }
    }
    
    # C utilities
    c {
        int c_func(int x) {
            return x + 10;
        }
    }
}
```

---

## Practical Examples

### Example 1: Global Utilities
```poly
global {
    python {
        def multiply(a, b):
            return a * b
        
        def divide(a, b):
            return a / b if b != 0 else 0
    }
}

python {
    print(multiply(5, 6))  # 30
    print(divide(20, 4))   # 5
}

javascript {
    console.log("Math functions are registered");
}
```

### Example 2: Config and Functions
```poly
global {
    # Global configuration
    max_retries = 3
    timeout = 5000
    api_url = "http://localhost"
    
    python {
        def connect(url, retries):
            return f"Connected to {url} with {retries} retries"
    }
}

python {
    print(f"Config - Timeout: {timeout}ms")
    print(f"Config - URL: {api_url}")
    
    result = connect(api_url, max_retries)
    print(result)
}
```

### Example 3: Mixed Languages
```poly
global {
    python {
        def process_data(data):
            return [x * 2 for x in data]
    }
    
    javascript {
        function format_output(data) {
            return JSON.stringify(data);
        }
    }
    
    debug = True
}

python {
    data = [1, 2, 3, 4]
    processed = process_data(data)
    
    if debug:
        print(f"Processed: {processed}")
}

javascript {
    console.log("JavaScript block executing");
    console.log("Debug mode: " + debug);
}
```

---

## Execution Order

```
┌─────────────────────────────┐
│ 1. First Pass: Global Blocks │
│ - Register all functions    │
│ - Set global variables      │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ 2. Second Pass: Local Blocks│
│ - Execute in order          │
│ - Access global functions   │
│ - Access global variables   │
└─────────────────────────────┘

global { python { def add() } }    ← First
                                    
python { print(add(5, 10)) }       ← Second
```

---

## Access Reference Table

| Item | Defined | Python | JavaScript | C |
|------|---------|--------|-----------|---|
| Global Python func | `global { python { def } }` | ✅ Direct | ⚠️ Registry | ⚠️ Registry |
| Global JS func | `global { javascript { function } }` | ⚠️ Registry | ✅ Direct | ⚠️ Registry |
| Global Variable | `global { var = val }` | ✅ Yes | ✅ Yes | ✅ Yes |
| Local Python func | `python { def }` | ✅ Yes | ❌ No | ❌ No |
| Local JS func | `javascript { function }` | ❌ No | ✅ Yes | ❌ No |
| Local C func | `c { int func() }` | ❌ No | ❌ No | ✅ Yes |

---

## Type Conversions

Automatic conversion between global function parameters:

| Python | JavaScript | C | C++ | Java |
|--------|-----------|---|-----|------|
| list | array | array | vector | ArrayList |  
| dict | object | struct | map | HashMap |
| str | string | char* | string | String |
| int | number | int | int | Integer |
| float | number | float | float | Float |
| bool | boolean | int | bool | Boolean |

---

## Best Practices

### ✅ Good Practices
```poly
# Define utilities in global
global {
    python {
        def utility_function():
            pass
    }
}

# Use throughout
python {
    result = utility_function()
}

# Store config globally
global {
    api_key = "secret"
    timeout = 5000
}
```

### ❌ Avoid
```poly
# Don't try to call local functions across languages
python {
    def local_func():
        pass
}

javascript {
    // ❌ This won't work
    // local_func()
}

# Don't define same function in global and local
global {
    python {
        def process():     # ✅ Global
            pass
    }
}

python {
    def process():        # ❌ Confusing - don't do this
        pass
}
```

---

## Running Examples

Try these example files:

```bash
# Global functions vs Local functions
poly examples\global_vs_local.poly

# Mixed languages in global scope
poly examples\mixed_global.poly

# Simple global functions
poly examples\global_functions.poly
```

---

## Summary

| Feature | Global | Local |
|---------|--------|-------|
| Definition | `global { language { ... } }` | `language { ... }` |
| Visibility | All languages | Single language only |
| Variables | ✅ Shared globally | Local to block |
| Functions | ✅ Registered globally | Internal only |
| Persistence | ✅ Entire program | Single execution |
| Best For | Utilities, Config | Language-specific code |
