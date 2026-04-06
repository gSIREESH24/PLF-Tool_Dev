# EXPORT LOGIC - File & Line Reference

## The 3 Core Files for Export Logic

### 1️⃣ EXPORT FUNCTION DEFINITION
**File:** `languages/python_lang.py` (Lines 6-10)
```python
def export(name, value):
    if hasattr(value, 'to_dict'):
        context.set(name, value.to_dict())
    else:
        context.set(name, value)
```
**What it does:** 
- Takes a variable name and value
- If it's a class instance → converts to dictionary via `to_dict()`
- Passes to `context.set()` for storage

---

### 2️⃣ CONTEXT STORAGE
**File:** `core/context.py` (Lines 1-11)
```python
class Context:
    def __init__(self):
        self.variables = {}
    
    def set(self, key, value):
        self.variables[key] = value  # ← Actual Storage
    
    def get(self, key):
        return self.variables.get(key)
    
    def all(self):
        return self.variables  # ← Returns all stored variables
```
**What it does:**
- `set()` → stores variable in memory
- `all()` → returns all stored variables for next language block

---

### 3️⃣ CLASS CONVERSION (to_dict method)
**File:** `core/class_registry.py` (Lines 47-58)
```python
def generate_python_class(cls_def: ClassDefinition) -> str:
    lines = [f'class {cls_def.name}:']
    args = ', '.join([f'{f.name}' for f in cls_def.fields])
    lines.append(f'    def __init__(self, {args}):')
    for field in cls_def.fields:
        lines.append(f'        self.{field.name} = {field.name}')
    lines.append('    def to_dict(self):')           # ← KEY METHOD
    lines.append('        return {')
    for field in cls_def.fields:
        lines.append(f"            '{field.name}': self.{field.name},")
    lines.append('        }')
    return '\n'.join(lines) + '\n'
```
**What it does:**
- Auto-generates Python class with `to_dict()` method
- `to_dict()` converts class instance to dictionary
- This is called by `export()` function

---

## Execution Flow in classes_scope.poly

### Initial State
```
File: classes_scope.poly
Content:
    global {
        class Product {
            string name
            float price
        }
        python {
            global_product = Product("Laptop", 1200.50)
            export("global_product", global_product)
        }
    }
    python { ... }
    javascript { ... }
```

### What Happens Step-by-Step

#### Step 1: Parser Reads File
**File:** `core/parser.py`
- Detected: `class Product` in global scope
- Registered in: `ClassRegistry` (in `core/class_registry.py`)

#### Step 2: Generate Python Class Code
**File:** `core/class_registry.py` → `generate_python_class()`
```python
# Generated code:
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
        }
```

#### Step 3: Python Block Executes
**File:** `languages/python_lang.py`
```python
# Inside exec(code, local_env):
global_product = Product("Laptop", 1200.50)  # Create instance
export("global_product", global_product)      # Call export()
```

#### Step 4: Export Function Runs
**File:** `languages/python_lang.py` (Lines 6-10)
```python
def export(name, value):
    # Check: does value have to_dict?
    if hasattr(value, 'to_dict'):
        # YES → global_product has to_dict
        result = value.to_dict()  # {"name": "Laptop", "price": 1200.50}
        context.set(name, result)
    else:
        context.set(name, value)
```

#### Step 5: Store in Context
**File:** `core/context.py` (Line 8)
```python
def set(self, key, value):
    self.variables[key] = value
    # context.variables = {
    #     "global_product": {"name": "Laptop", "price": 1200.50}
    # }
```

#### Step 6: Next Language Gets It
**File:** `languages/javascript_lang.py` or `languages/cpp_lang.py`
```python
# In any language runner:
for key, value in context.all().items():
    # key = "global_product"
    # value = {"name": "Laptop", "price": 1200.50}
    # → Inject as JS var, C++ variable, etc.
```

---

## Visual: Data Transformation Through Export

```
Input (Python):
┌────────────────────────────┐
│ class instance:            │
│ Product("Laptop", 1200.50) │
├────────────────────────────┤
│ .name = "Laptop"           │
│ .price = 1200.50           │
└────────────────────────────┘
          │
          │ export() called
          ▼
┌────────────────────────────┐
│ to_dict() method          │
│ (from class_registry.py)  │
└────────────────────────────┘
          │
          ▼
Output (Dictionary):
┌────────────────────────────┐
│ {                          │
│   "name": "Laptop",       │
│   "price": 1200.50        │
│ }                          │
├────────────────────────────┤
│ Stored in:                 │
│ context.variables[key]     │
└────────────────────────────┘
          │
          │ context.all() called by next language
          ▼
Available to:
JavaScript, C++, Java, C
as their native types
```

---

## The 4 Key Functions in Export Chain

| Function | File | Line | Purpose |
|----------|------|------|---------|
| `export(name, value)` | `languages/python_lang.py` | 6 | Entry point for export |
| `hasattr(value, 'to_dict')` | Python builtin | - | Check if class instance |
| `value.to_dict()` | `core/class_registry.py` | 51 | Convert instance to dict |
| `context.set(key, value)` | `core/context.py` | 8 | Store in global context |

---

## Summary

**export() = Bridge between languages**

```
Python [export() function] → Context [storage] → Next Language [injection]
  ↓
Classes converted to dicts
  ↓
Stored as JSON-serializable data
  ↓
Accessible to all other languages
```

This is how `export("global_product", global_product)` makes data available across Python → JavaScript → C++ → Java boundaries!
