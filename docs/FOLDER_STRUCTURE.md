# Folder Structure & Purpose

This document explains what each folder does, what files it contains, and why it exists.

---

## 📋 Table of Contents

1. [Project Root](#project-root)
2. [core/ - Core Processing Engine](#core--core-processing-engine)
3. [languages/ - Language Support](#languages--language-support)
4. [global_ns/ - Global Namespace](#global_ns--global-namespace)
5. [examples/ - Example Programs](#examples--example-programs)
6. [tests/ - Unit Tests](#tests--unit-tests)
7. [docs/ - Documentation](#docs--documentation)
8. [Directory Tree](#directory-tree)
9. [Data Flow Between Folders](#data-flow-between-folders)

---

## Project Root

**Location:** `poly_runtime/`

**Contains:**
- `poly.py` - Main entry point script
- `poly.bat` - Windows batch wrapper
- `README.md` - Main documentation

**Purpose:**
- Entry point for running `.poly` files
- When user runs `python poly.py examples/basic.poly`, it starts from here

**Key Files:**

### `poly.py` (Main Entry Point)
```python
def main():
    file_path = sys.argv[1]  # Get .poly file path
    with open(file_path, "r") as f:
        source_code = f.read()
    program = parse(source_code)
    interpret(program)
```

**What it does:**
1. Accepts command-line argument (path to .poly file)
2. Reads the file contents
3. Sends to parser
4. Sends parsed result to interpreter
5. Interpreter executes the program

**Why:** Clean separation - keeps main script minimal and delegates to specialized modules

---

## core/ - Core Processing Engine

**Purpose:** Heart of the system - transforms `.poly` source code into executable actions

**Contains:** 7 files

### 1. `lexer.py` - Tokenization

**Purpose:** Convert raw text into tokens

**Input:** Raw .poly file content
```
global { message = "hello" }
python { print(message) }
```

**Output:** List of tokens
```
[KEYWORD("global"), LBRACE(), IDENTIFIER("message"), 
 EQUALS(), STRING("hello"), RBRACE(), KEYWORD("python"), ...]
```

**Why needed:**
- Raw text is hard to parse
- Tokens are structured and easier to analyze
- Handles special syntax (comments, strings, language keywords)

**Key methods:**
- `tokenize(source)` - Main method to tokenize

---

### 2. `parser.py` - AST Generation

**Purpose:** Convert token stream into Abstract Syntax Tree (AST)

**Input:** Tokens from lexer
```
[KEYWORD("global"), LBRACE(), IDENTIFIER("message"), ...]
```

**Output:** AST (Tree structure)
```
Program
├── GlobalSection
│   └── Assignment(target="message", value="hello")
├── LanguageSection(language="python", code="print(message)")
```

**Why needed:**
- Tokens are flat - hard to understand structure
- AST shows hierarchical relationships
- Easy to interpret/execute

**Key methods:**
- `parse(tokens)` - Converts tokens to AST
- Various `parse_*()` methods for different constructs

---

### 3. `interpreter.py` - Execution Engine

**Purpose:** Walk through AST and execute it

**Input:** AST from parser
```
Program
├── GlobalSection
│   └── Assignment(...)
├── LanguageSection(...)
```

**Output:** Executed program (prints output, registers functions)

**Why needed:**
- AST structure defines what should happen
- Interpreter decides HOW to make it happen
- Controls execution order
- Manages context

**Key method:**
- `interpret(ast_node)` - Main execution method

**Does:**
1. Creates execution context
2. Processes global section
3. Processes each language section
4. Delegates to appropriate executor

---

### 4. `executor.py` - Code Execution

**Purpose:** Execute code in specific languages

**Input:** Language name and code
```
language: "python"
code: "print('hello')"
```

**Output:** Executed result (return value + output)

**Why needed:**
- Different languages execute differently
- Python is direct, C needs compilation
- This module abstracts those differences

**Key method:**
- `execute(language, code)` - Execute code in specified language

---

### 5. `context.py` - Execution Context Manager

**Purpose:** Maintain global state during execution

**Stores:**
```python
context = {
    "global": {
        "message": "hello",
        "counter": 42
    },
    "python": {...},
    "javascript": {...},
    "c": {...},
    "java": {...},
    "cpp": {...}
}
```

**Why needed:**
- Global variables need to be stored
- Language-specific state needs management
- Variables must persist across language blocks

**Key features:**
- Get/set global variables
- Manage language-specific data
- Thread-safe access (if multithreading used)

---

### 6. `ast.py` - AST Node Definitions

**Purpose:** Define structure of AST nodes

**Contains classes:**
```python
class Program:
    sections: List[Section]

class Section:
    type: str  # "global" or language name

class GlobalSection(Section):
    statements: List[Statement]

class LanguageSection(Section):
    language: str  # "python", "c", etc.
    code: str

class Assignment:
    target: str
    value: Any
```

**Why needed:**
- Parser needs to know what AST structures exist
- Type checking for AST nodes
- Documentation of valid AST structure

---

### 7. `function_registry.py` - Global Function Storage

**Purpose:** Store all functions from all languages

**Stores:**
```python
registry = {
    "python": {
        "greet": <function_object>,
        "add": <function_object>
    },
    "javascript": {
        "calculateSum": <function_object>
    },
    "c": {...},
    "java": {...},
    "cpp": {...}
}
```

**Why needed:**
- Functions defined in one language must be callable from others
- Cross-language function calls need function reference
- Runtime function lookup

**Key methods:**
- `register(language, name, function)` - Add function
- `get(language, name)` - Retrieve function
- `call(language, name, args)` - Execute function

---

### 8. `function_signature.py` - Function Metadata

**Purpose:** Store metadata about functions

**Stores:**
```python
signature = {
    "name": "add",
    "language": "python",
    "parameters": ["a", "b"],
    "return_type": "int",
    "is_builtin": False
}
```

**Why needed:**
- Type conversion needs to know parameter types
- Cross-language calling needs signature info
- Runtime introspection

---

## languages/ - Language Support

**Purpose:** Handle execution of different programming languages

**Contains:**
- Language executor files (5 files)
- `function_adapters/` subfolder
- `__init__.py`

### Language Executor Files

Each language has a dedicated executor file:

#### `python_lang.py` - Python Executor

**Purpose:** Execute Python code

**How it works:**
```python
def execute(code):
    namespace = {}
    exec(code, namespace)
    return extract_functions(namespace)
```

**Why easy:** Python can execute code directly via `exec()`

**Speed:** ⚡⚡⚡ Fastest (direct execution)

---

#### `js_lang.py` - JavaScript Executor

**Purpose:** Execute JavaScript code via Node.js

**How it works:**
1. Write code to temporary `.js` file
2. Execute: `node temp_file.js`
3. Capture output
4. Delete temporary file
5. Extract functions from code

**Why complex:** JavaScript not natively available in Python

**Speed:** ⚡⚡ Medium (subprocess + Node.js startup)

**Dependencies:** Node.js must be installed

---

#### `c_lang.py` - C Executor

**Purpose:** Execute C code

**How it works:**
1. Write code to temporary `.c` file (with main function)
2. Compile: `gcc temp_file.c -o temp_binary`
3. Execute: `./temp_binary`
4. Capture output
5. Delete temporary files

**Why complex:** C must be compiled before execution

**Speed:** ⚡ Slow (compilation + execution)

**Dependencies:** gcc compiler must be installed

---

#### `java_lang.py` - Java Executor

**Purpose:** Execute Java code

**How it works:**
1. Write code to temporary `.java` file
2. Compile: `javac temp_file.java`
3. Execute: `java ClassName`
4. Capture output
5. Delete temporary files

**Why complex:** Java must be compiled, requires JVM

**Speed:** ⚡ Slow (JVM startup + compilation)

**Dependencies:** Java JDK/JRE must be installed

---

#### `cpp_lang.py` - C++ Executor

**Purpose:** Execute C++ code

**How it works:**
1. Write code to temporary `.cpp` file
2. Compile: `g++ temp_file.cpp -o temp_binary`
3. Execute: `./temp_binary`
4. Capture output
5. Delete temporary files

**Why complex:** C++ must be compiled

**Speed:** ⚡ Slow (compilation + execution)

**Dependencies:** g++ compiler must be installed

---

### `function_adapters/` Subfolder

**Purpose:** Type conversion & function calling for each language

**Contains:**
- `python_adapter.py` - Python type handling
- `js_adapter.py` - JavaScript type handling
- `c_adapter.py` - C type handling
- `java_adapter.py` - Java type handling
- `cpp_adapter.py` - C++ type handling

**Why needed:**
- Each language has different types
- Need to convert between Python and other languages
- Different function calling conventions
- Parameter passing is language-specific

#### Example: `java_adapter.py`

**What it does:**
```python
def convert_python_to_java(py_value, target_type):
    if target_type == "Integer":
        return int(py_value)
    elif target_type == "String":
        return str(py_value)
    elif target_type == "Boolean":
        return bool(py_value)
    # etc.

def call_java_function(function_name, python_args):
    # Convert python_args to Java types
    java_args = [convert_python_to_java(arg) for arg in python_args]
    # Call Java function
    result = execute_in_java(function_name, java_args)
    # Convert result back to Python
    return convert_java_to_python(result)
```

**Why needed:**
- Python int ≠ Java Integer
- Need automatic conversion
- Transparent to user

---

## global_ns/ - Global Namespace

**Purpose:** Shared utilities and type conversion

**Contains:** 3 files

### `marshalling.py` - Type Conversion Engine

**Purpose:** Convert types between all 5 languages

**Features:**
- Python ↔ JavaScript conversion
- Python ↔ C conversion
- Python ↔ Java conversion
- Python ↔ C++ conversion
- Cross-language conversions (via Python)
- Type validation
- Type inference

**Why needed:**
```python
# User calls Java function from Python
result = call_java("add", [10, 20])
# System needs to convert:
# Python int (10) → Java Integer
# Python int (20) → Java Integer
# Result: Java Integer → Python int
# All automatic via marshalling.py
```

**Type mappings:**
```
Python int        ↔ JavaScript number
Python str        ↔ JavaScript string
Python list       ↔ JavaScript array
Python int        ↔ Java Integer
Python list       ↔ Java ArrayList
Python int        ↔ C int
Python str        ↔ C++ std::string
etc. (50+ mappings)
```

---

### `builtins.py` - Built-in Functions

**Purpose:** Provide global functions available to all languages

**Examples:**
```python
def print_all(*args):
    """Print to console"""
    
def len_all(obj):
    """Get length of object"""
    
def type_of(obj):
    """Get type of object"""
```

**Why needed:**
- Common operations available globally
- Consistent interface across languages
- Don't repeat code in each language

---

### `__init__.py` - Module Initialization

**Purpose:** Make `global_ns` a Python package

**Why needed:** Allows importing from `global_ns`
```python
from global_ns.marshalling import convert
from global_ns.builtins import print_all
```

---

## examples/ - Example Programs

**Purpose:** Demonstrate system capabilities

**Contains:** 7+ example `.poly` files

### Example Files

1. **`basic_function_call.poly`**
   - Shows basic syntax
   - Demonstrates all 5 languages
   - Simple function definitions

2. **`all_languages_demo.poly`**
   - Comprehensive demo
   - Cross-language function calls
   - Global variables usage

3. **`math_functions.poly`**
   - Math operations
   - Function calls between languages
   - Type conversions

4. **`data_processing.poly`**
   - List and dictionary operations
   - String manipulation
   - Data transformations

5. **`type_conversion_demo.poly`**
   - Type conversion between all 5 languages
   - Type validation examples
   - Type inference demonstrations

**Why needed:**
- Users learn by example
- Testing system functionality
- Quick reference for syntax
- Verify system works

---

## tests/ - Unit Tests

**Purpose:** Verify system correctness

**Contains:**

### `test_type_conversion.py`

**What it tests:**
- Python ↔ JavaScript conversion
- Python ↔ C conversion
- Python ↔ Java conversion (NEW)
- Python ↔ C++ conversion (NEW)
- Cross-language conversions
- Type validation
- Type inference
- Language normalization

**How to run:**
```bash
python tests/test_type_conversion.py
```

**Why needed:**
- Ensures type conversion works
- Catches bugs early
- Provides confidence in system
- Regression testing

**Example test:**
```python
def test_python_java_conversion():
    python_value = 42
    java_value = convert(python_value, "python", "java")
    assert java_value == 42
    
    back_to_python = convert(java_value, "java", "python")
    assert back_to_python == 42
```

---

## docs/ - Documentation

**Purpose:** Explain how everything works

**Contains:** 10+ documentation files

### Key Documentation Files

1. **`PROJECT_FLOW.md`** (THIS FILE)
   - Explains execution flow
   - Shows what happens when `.poly` file runs
   - Step-by-step process
   - Examples

2. **`FOLDER_STRUCTURE.md`**
   - Describes each folder
   - Why each folder exists
   - What files it contains
   - Purpose of each file

3. **`TYPE_CONVERSION.md`**
   - Type mapping reference
   - Usage examples
   - Type validation guide
   - Advanced usage patterns

4. **`TYPE_CONVERSION_QUICK_REF.md`**
   - Quick API reference
   - Common operations
   - Code snippets

5. Other documentation
   - Architecture guide
   - Enhancement summaries
   - Setup instructions

**Why needed:**
- Users need to understand system
- Developers need to modify code
- Reference material
- Troubleshooting guide

---

## Directory Tree

```
poly_runtime/                               Root directory
│
├── poly.py                                 Main entry point
├── poly.bat                                Windows batch wrapper
├── README.md                               Main documentation
│
├── core/                                   ┐
│   ├── lexer.py           (Tokenization)   │ Core processing
│   ├── parser.py          (AST creation)   │ engine
│   ├── interpreter.py     (Execution)      │ (transforms source
│   ├── executor.py        (Code runner)    │  code to results)
│   ├── context.py         (State mgmt)     │
│   ├── ast.py             (Node defs)      │
│   ├── function_registry.py (Function DB) │
│   ├── function_signature.py (Metadata)   │
│   └── __pycache__/       (Compiled)       ┘
│
├── languages/                              ┐
│   ├── python_lang.py     (Python exec)    │ Language
│   ├── js_lang.py         (JS exec)        │ support
│   ├── c_lang.py          (C exec)         │ (each language
│   ├── java_lang.py       (Java exec)      │  has executor)
│   ├── cpp_lang.py        (C++ exec)       │
│   │                                        │
│   ├── function_adapters/                  │ Type conversion
│   │   ├── python_adapter.py               │ adapters
│   │   ├── js_adapter.py                   │
│   │   ├── c_adapter.py                    │
│   │   ├── java_adapter.py                 │
│   │   ├── cpp_adapter.py                  │
│   │   └── __init__.py                     │
│   │                                        │
│   ├── __init__.py                         │
│   └── __pycache__/                        ┘
│
├── global_ns/                              ┐
│   ├── marshalling.py    (Type conversion) │ Global utilities
│   ├── builtins.py       (Built-ins)       │
│   ├── __init__.py                         │
│   └── __pycache__/                        ┘
│
├── examples/                               ┐
│   ├── basic_function_call.poly            │ Example
│   ├── all_languages_demo.poly             │ .poly files
│   ├── math_functions.poly                 │
│   ├── data_processing.poly                │
│   ├── type_conversion_demo.poly           │
│   ├── cpp_functions.poly                  │
│   ├── java_functions.poly                 │
│   ├── __init__.py                         │
│   └── ... (more examples)                 ┘
│
├── tests/                                  ┐
│   ├── test_type_conversion.py             │ Unit tests
│   └── ... (more tests)                    ┘
│
├── docs/                                   ┐
│   ├── PROJECT_FLOW.md          (This)     │
│   ├── FOLDER_STRUCTURE.md      (This)     │ Documentation
│   ├── TYPE_CONVERSION.md                  │
│   ├── TYPE_CONVERSION_QUICK_REF.md        │
│   ├── TYPE_CONVERSION_ARCHITECTURE.md     │
│   ├── TYPE_CONVERSION_ENHANCEMENT.md      │
│   └── ... (more docs)                     ┘
│
└── .git/                                   Git version control
```

---

## Data Flow Between Folders

### Flow Diagram: How Folders Work Together

```
┌─────────────────┐
│ USER RUNS       │
│ poly.py         │ ← Entry point (root directory)
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ core/lexer.py                                │
│ Tokenize: .poly file → Token stream          │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ core/parser.py                               │
│ Parse: Token stream → AST                    │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ core/interpreter.py                          │
│ Interpret: Walk AST & execute                │
└────────┬─────────────────────────────────────┘
         │
         ├──────────────────────┬──────────────┬─────────────┐
         │                      │              │             │
         ▼                      ▼              ▼             ▼
    ┌─────────────┐      ┌──────────┐   ┌─────────┐    ┌──────────┐
    │ core/       │      │ languages│   │ global_ │    │ core/    │
    │ context.py  │      │ /        │   │ ns/     │    │ function_│
    │ (Store      │      │ *_lang.  │   │ *       │    │ registry_│
    │ globals)    │      │ py       │   │ .py     │    │ .py      │
    └─────────────┘      │ (Execute │   │(Convert │    │(Register │
                         │ language)│   │ types)  │    │functions)│
                         └──────────┘   └─────────┘    └──────────┘
         │                      │              │             │
         └──────────────────────┴──────────────┴─────────────┘
                           │
                           ▼
                   ┌──────────────────┐
                   │ Language exec    │
                   │ functions/       │
                   │ adapters/        │
                   │ *_adapter.py     │
                   │ (Type conversion)│
                   └──────────────────┘
                           │
                           ▼
                   ┌──────────────────┐
                   │ Output & Results │
                   │ Functions stored │
                   │ in registry      │
                   └──────────────────┘
```

### Module Dependencies

```
poly.py
  └─→ core/parser.py ────────────────→ core/ast.py
  └─→ core/interpreter.py ──────────→ core/context.py
                                    → core/executor.py
                                    → core/function_registry.py
                                    
core/executor.py ────────────────────→ languages/*_lang.py
                                    → languages/function_adapters/*_adapter.py
                                    → global_ns/marshalling.py
                                    
languages/*_adapter.py  ─────────────→ global_ns/marshalling.py
                                    → core/function_signature.py

global_ns/marshalling.py ────────────→ (Type conversion)
```

---

## Summary: Why Each Folder Exists

| Folder | Purpose | Key Responsibility |
|--------|---------|-------------------|
| **root** | Entry point | Start program |
| **core/** | Processing engine | Lex, parse, interpret |
| **languages/** | Language support | Execute each language |
| **global_ns/** | Utilities | Type conversion |
| **examples/** | Learning material | Show usage |
| **tests/** | Quality assurance | Verify correctness |
| **docs/** | Documentation | Explain system |

---

## Key Takeaways

1. **`core/`** = Brain of the system (thinking/parsing)
2. **`languages/`** = Hands of the system (doing/executing)
3. **`global_ns/`** = Glue of the system (connecting/converting)
4. **`examples/`** = Teaching material (learning)
5. **`tests/`** = Quality gate (verifying)
6. **`docs/`** = User guide (understanding)

Each folder has a specific role that contributes to the overall functionality of the Polyglot Runtime system.
