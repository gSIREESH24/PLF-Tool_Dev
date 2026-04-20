# EXPORT LOGIC FLOW - How `export()` Works in Poly

## Quick Summary
When you call `export("global_product", global_product)` in a Python block, it stores the value in **Context**, which is then passed to the next language block.

---

## File Structure & Logic Flow

```
.poly file (classes_scope.poly)
    ↓
poly.py (Entry point)
    ↓
core/interpreter.py (Orchestrates execution)
    ↓
languages/python_lang.py
    ├─ Defines export() function
    └─ Calls context.set()
    ↓
core/context.py
    └─ Stores variable in memory
    ↓
Next language block gets access via context.all()
```

---

## Step-by-Step Breakdown

### STEP 1: Define the Global Class
**File: `examples/classes_scope.poly`**
```
global {
    class Product {
        string name
        float price
    }
    
    python {
        global_product = Product("Laptop", 1200.50)
        export("global_product", global_product)  ← EXPORT CALL
    }
}
```

### STEP 2: Parser Extracts Class Definition
**File: `core/parser.py`**
- Recognizes `class Product { ... }` inside global scope
- Registers it in `ClassRegistry` (core/class_registry.py)
- Fields: `name` (string), `price` (float)

### STEP 3: Export Function Gets Defined
**File: `languages/python_lang.py` → Lines 6-10**
```python
def export(name, value):
    if hasattr(value, 'to_dict'):
        context.set(name, value.to_dict())  # Convert object to dict
    else:
        context.set(name, value)             # Store primitive as-is
```

**Key Logic:**
- If value is a **class instance** with `to_dict()` method → convert to dictionary
- If value is a **primitive** → store directly

### STEP 4: Context Stores Value
**File: `core/context.py` → Lines 7-8**
```python
class Context:
    def __init__(self):
        self.variables = {}   # Global storage
    
    def set(self, key, value):
        self.variables[key] = value  # Store: "global_product" → result
```

### STEP 5: Export Gets Injected into Python Environment
**File: `languages/python_lang.py` → Line 36**
```python
local_env = context.all().copy()        # Get existing variables
local_env['export'] = export             # Make export() available
local_env['call'] = call
local_env['get_function'] = get_function

exec(code, local_env)                    # Run Python code with these functions
```

### STEP 6: Next Language Gets Access
**File: `languages/[js/cpp/java/c]_lang.py`**

When JavaScript/C++/Java/C block runs:

```python
if context:
    for key, value in context.all().items():  # ← Gets global_product!
        # Inject as language-specific type
```

For example, in JavaScript:
```python
for key, value in context.all().items():
    js_value = json.dumps(value)
    js_vars += f'var {key} = {js_value};\n'
    # Results in: var global_product = {"name": "Laptop", "price": 1200.50};
```

---

## Complete Flow Diagram for `export("global_product", global_product)`

```
┌─────────────────────────────────────────────────────────────┐
│ PYTHON BLOCK (classes_scope.poly)                          │
│                                                              │
│ global_product = Product("Laptop", 1200.50)                │
│ export("global_product", global_product) ← CALLED          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ EXPORT FUNCTION (languages/python_lang.py Line 6-10)       │
│                                                              │
│ def export(name, value):                                    │
│     if hasattr(value, 'to_dict'):                          │
│         context.set(name, value.to_dict())  ◄─ CONVERTS   │
│                                              │  class to    │
│                                              │  dictionary  │
│     else:                                                   │
│         context.set(name, value)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ CONTEXT STORAGE (core/context.py)                          │
│                                                              │
│ self.variables = {                                          │
│     "global_product": {"name": "Laptop", "price": 1200.50} │
│ }                                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ NEXT LANGUAGE BLOCK (e.g., JavaScript)                     │
│                                                              │
│ context.all() returns the variables dict                     │
│ Values injected as language-specific types:                 │
│ var global_product = {"name":"Laptop","price":1200.5};     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files & Their Roles

| File | Role | Key Function |
|------|------|--------------|
| `core/interpreter.py` | Main orchestrator | Calls language runners sequentially |
| `languages/python_lang.py` | Python executor | Defines & injects `export()` function |
| `core/context.py` | Global state storage | Stores/retrieves variables across languages |
| `core/class_registry.py` | Class definitions | Generates language-specific class code |
| `core/parser.py` | Parses .poly files | Extracts classes & code blocks |
| `global_ns/marshalling.py` | Type conversion | Converts between language types |

---

## Example: How export() with a Class Works

### In Python (classes_scope.poly)
```python
global_product = Product("Laptop", 1200.50)
export("global_product", global_product)
```

### What Happens Inside export()
```python
# Check if it's a class instance
hasattr(global_product, 'to_dict')  # True!

# Convert to dictionary
result = global_product.to_dict()
# → {"name": "Laptop", "price": 1200.50}

# Store in context
context.set("global_product", result)
# → context.variables["global_product"] = {"name": "Laptop", "price": 1200.50}
```

### Next Block Gets It
```python
# JavaScript block
context.all() → {"global_product": {"name": "Laptop", "price": 1200.50}}

# Injected as:
var global_product = {"name":"Laptop","price":1200.50};
```

---

## Why This Design?

1. **Separation of Concerns**: Each language has its own runner, but shares context
2. **Type Flexibility**: Classes can be converted to dicts for JSON serialization
3. **Bidirectional**: Any language can export, next language receives automatically
4. **Global State**: Context persists across all language blocks in sequence

---

## To Modify Export Behavior

**To add custom export logic**, edit these files:
- Add custom logic: `languages/python_lang.py` (line 6-10)
- Change storage: `core/context.py` (line 7-8)
- Change marshalling: `global_ns/marshalling.py` (conversion rules)
