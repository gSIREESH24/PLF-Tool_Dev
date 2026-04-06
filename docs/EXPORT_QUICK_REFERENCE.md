# QUICK REFERENCE - Unified Export Across All 5 Languages

## One-Liner Summary
🎯 **All 5 languages now use standardized `export()` functions** with the same pattern: take variable → convert to standard format → inject to next language.

---

## Export Syntax by Language

### Python
```python
export("name", value)          # Primitives, lists, dicts, class instances
```

### C++
```cpp
export_cpp("name", value);     // int, double, std::vector, std::string
EXPORT_VAR(name, value);       // Alternative: auto-stringifies variable name
```

### JavaScript
```javascript
export_js("name", value);      // Numbers, strings, arrays, objects
export_func("name", value);    // Alternative name
```

### Java
```java
export_java("name", value);    // Integer, Double, String, ArrayList, objects
export_func("name", value);    // Alternative name
```

### C
```c
EXPORT_DOUBLE("name", value);  // Doubles
EXPORT_INT("name", value);     // Integers
EXPORT_STRING("name", value);  // Strings
export_c("name", &value, type); // Generic: type 0=double, 1=int, 2=string
```

---

## What Gets Stored in Context

After `export()` is called:
```
✓ Primitives (int, float, bool, string) → As-is
✓ Arrays/Lists → JSON arrays [1,2,3]
✓ Objects/Dicts → JSON objects {"key":"value"}
✓ Class instances → Converted to dict (Python → all languages)
```

---

## Data Flow

```
Block 1: export("x", 42)
    ↓ stores as POLY_EXPORT:x=42
    ↓ parsed and injected
Block 2: Can use variable x (=42)
    ↓ export("y", x+8)
    ↓ stores as POLY_EXPORT:y=50
Block 3: Can use y (=50)
```

---

## Supported Type Conversions

| Type | Python | C++ | JS | Java | C |
|------|--------|-----|----|----|---|
| int | ✓ | ✓ | ✓ | ✓ | ✓ |
| float/double | ✓ | ✓ | ✓ | ✓ | ✓ |
| string | ✓ | ✓ | ✓ | ✓ | ✓ |
| array | ✓ | ✓ | ✓ | ✓ | ✓ |
| bool | ✓ | ✓ | ✓ | ✓ | ~ |
| dict/object | ✓ | ~ | ✓ | ✓ | ~ |
| class instance | ✓ | ~ | ~ | ~ | ~ |

---

## Common Usage Patterns

### Pattern 1: Preprocess → Analyze → Visualize
```poly
python { data = [1,2,3]; export("data", data) }
cpp { export_cpp("result", analyze(data)) }
javascript { visualize(result) }
```

### Pattern 2: Sequential Transformation
```poly
python { x = raw_input; export("x", x) }
cpp { y = transform(x); export_cpp("y", y) }
java { z = process(y); export_java("z", z) }
python { final = aggregate(z) }
```

### Pattern 3: Multi-Language Parallel
```poly
python { export("shared", value) }
cpp { use shared }
javascript { use shared }
java { use shared }
c { use shared }
```

---

## Internal Format (POLY_EXPORT)

The framework uses a special marker system internally:
```
POLY_EXPORT:variable_name=value
POLY_EXPORT:x=42
POLY_EXPORT:data=[1,2,3]
POLY_EXPORT:config={"a":1,"b":2}
```

You don't manually use this - it's automatic! Just call `export()` and the framework handles it.

---

## Files to Know

| File | Role |
|------|------|
| `languages/python_lang.py` | Defines `export()` function |
| `languages/cpp_lang.py` | Defines `export_cpp()` templates |
| `languages/js_lang.py` | Defines `export_js()` function |
| `languages/java_lang.py` | Defines `export_java()` method |
| `languages/c_lang.py` | Defines `EXPORT_*` macros |
| `core/context.py` | Storage backend (context.variables) |
| `docs/UNIFIED_EXPORT_GUIDE.md` | Complete reference guide |

---

## Example: Full 5-Language Pipeline

```poly
global { python { data = [2.5, 3.7, 5.2] } }

python {
    avg = sum(data) / len(data)
    export("average", avg)
    export("values", data)
}

cpp {
    double variance = 0;
    for(auto v : values) variance += pow(v-average, 2);
    export_cpp("variance", variance);
}

javascript {
    let stddev = Math.sqrt(variance);
    export_js("stddev", stddev);
}

java {
    double z_score = (values.get(0) - average) / stddev;
    export_java("zscore", z_score);
}

c {
    printf("Z-score: %f\n", zscore);
    EXPORT_DOUBLE("complete", 1);
}

python { print(f"Pipeline complete! {complete}") }
```

**Output:** Data flows through all 5 languages seamlessly! 🚀

---

## Troubleshooting

**Q: Variable not found in next language?**  
A: Make sure you called `export()` in the previous language block.

**Q: POLY_EXPORT lines appearing in output?**  
A: That's normal - it's the internal protocol. Framework filters them automatically.

**Q: Type mismatch error?**  
A: Check the type mapping table above. Not all types convert between all languages.

**Q: Class instance can't be exported from compiled languages?**  
A: Only Python can export class instances (auto-converts to dict). Convert manually first in other languages.

---

## Key Principle

> **Same Function, Same Behavior, All Languages**
> 
> Whether you call `export()`, `export_cpp()`, `export_js()`, `export_java()`, or `EXPORT_DOUBLE()`,
> the result is identical: your variable becomes available to the next language block.

---

## Learn More

- **Full Guide**: `docs/UNIFIED_EXPORT_GUIDE.md`
- **Architecture**: `docs/EXPORT_LOGIC_EXPLAINED.md`
- **File Reference**: `docs/EXPORT_FILE_REFERENCE.md`

---

Last Updated: April 6, 2026 | All 5 Languages Unified ✓
