# Project Flow - How Polyglot Runtime Works

This document explains what happens when you run a `.poly` file and how the entire system processes it.

---

## 📋 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Folder Structure](#folder-structure)
3. [Execution Flow](#execution-flow)
4. [Detailed Step-by-Step Process](#detailed-step-by-step-process)
5. [Example: Running a .poly File](#example-running-a-poly-file)
6. [How Different Sections Work](#how-different-sections-work)

---

## Quick Overview

When you run a `.poly` file:

```bash
python poly.py examples/basic_function_call.poly
```

The system performs these main steps:

1. **Read** the .poly file
2. **Lex** (tokenize) the source code
3. **Parse** (create AST - Abstract Syntax Tree)
4. **Interpret** (execute the program)
5. **Manage** multiple language contexts
6. **Register** functions in global registry
7. **Convert** types between languages
8. **Execute** code in appropriate language environments

---

## Folder Structure

```
poly_runtime/
├── poly.py                 ← Main Entry Point (You run this!)
├── poly.bat                ← Windows batch script
│
├── core/                   ← Core Processing Engine
│   ├── lexer.py           ← Tokenizes .poly files
│   ├── parser.py          ← Parses tokens into AST
│   ├── interpreter.py     ← Executes the AST
│   ├── ast.py             ← AST node definitions
│   ├── executor.py        ← Executes code sections
│   ├── context.py         ← Manages execution context
│   ├── function_registry.py ← Stores functions from all languages
│   └── function_signature.py ← Function metadata
│
├── languages/             ← Language Support
│   ├── python_lang.py     ← Python executor
│   ├── javascript_lang.py ← JavaScript executor
│   ├── c_lang.py          ← C executor
│   ├── java_lang.py       ← Java executor
│   ├── cpp_lang.py        ← C++ executor
│   └── function_adapters/ ← Type conversion per language
│       ├── python_adapter.py
│       ├── js_adapter.py
│       ├── c_adapter.py
│       ├── java_adapter.py
│       └── cpp_adapter.py
│
├── global_ns/             ← Global Namespace & Utilities
│   ├── marshalling.py     ← Type conversion between languages
│   └── builtins.py        ← Built-in functions
│
├── examples/              ← Example .poly files
│   ├── basic_function_call.poly
│   ├── all_languages_demo.poly
│   └── ...
│
├── tests/                 ← Unit tests
│   └── test_type_conversion.py
│
└── docs/                  ← Documentation
    ├── PROJECT_FLOW.md (This file)
    ├── FOLDER_STRUCTURE.md
    └── ...
```

---

## Execution Flow

### High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER RUNS: python poly.py examples/basic_function_call.poly
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FILE LOADING (poly.py)                                   │
│    - Read .poly file from disk                              │
│    - Store source code in memory                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LEXICAL ANALYSIS (core/lexer.py)                         │
│    - Tokenize source code                                   │
│    - Break into keywords, identifiers, symbols              │
│    - Handle language blocks (python {}, c {}, etc.)         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PARSING (core/parser.py)                                 │
│    - Convert tokens to AST (Abstract Syntax Tree)           │
│    - Identify sections: global {}, python {}, c {}, etc.    │
│    - Build tree structure                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. INTERPRETATION (core/interpreter.py)                     │
│    - Walk through AST                                       │
│    - Execute global block                                   │
│    - Execute language blocks in order                       │
│    - Manage execution context                               │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    Python Code      JavaScript Code    C Code
    │                │                   │
    ├──Register      ├──Register         ├──Compile
    │  functions     │  functions        │  (if needed)
    │  in registry   │  in registry      │
    └──Execute       └──Execute          └──Execute
       locally          via Node.js         via gcc
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. TYPE CONVERSION (global_ns/marshalling.py)               │
│    - Convert types between languages                        │
│    - Validate type compatibility                            │
│    - Handle Java, C++, JavaScript, C, Python types          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. FUNCTION REGISTRY (core/function_registry.py)            │
│    - Store all functions from all languages                 │
│    - Allow cross-language function calls                    │
│    - Manage function signatures                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. OUTPUT & CLEANUP                                         │
│    - Print results                                          │
│    - Clean up resources                                     │
│    - Exit program                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Process

### Step 1: User Invokes the Program

```bash
python poly.py examples/basic_function_call.poly
```

**What happens:**
- Entry point: `poly.py`
- Reads command-line arguments
- Loads the .poly file from disk

### Step 2: Lexical Analysis (Tokenization)

**File:** `core/lexer.py`

**Input:**
```
global {
    message = "Hello"
}

python {
    print(message)
}
```

**Output:** Stream of tokens
```
TOKEN: KEYWORD "global"
TOKEN: LBRACE "{"
TOKEN: IDENTIFIER "message"
TOKEN: EQUALS "="
TOKEN: STRING "Hello"
TOKEN: RBRACE "}"
TOKEN: KEYWORD "python"
TOKEN: LBRACE "{"
TOKEN: IDENTIFIER "print"
TOKEN: LPAREN "("
TOKEN: IDENTIFIER "message"
TOKEN: RPAREN ")"
TOKEN: RBRACE "}"
```

### Step 3: Parsing (AST Creation)

**File:** `core/parser.py`

**Input:** Token stream (from Step 2)

**Output:** Abstract Syntax Tree (AST)
```
Program
├── GlobalSection
│   └── Assignment
│       ├── Variable: "message"
│       └── Value: "Hello"
├── LanguageSection
│   ├── Language: "python"
│   └── Code: "print(message)"
```

### Step 4: Interpretation (Execution)

**File:** `core/interpreter.py`

**Process:**
1. Create execution context
2. Process global section (set global variables)
3. Process each language section in order
4. For each language:
   - Load language executor
   - Execute code in that language
   - Register functions in global registry
   - Handle output

### Step 5: Language Execution

For **Python** code → `languages/python_lang.py`
- Execute directly using Python interpreter
- Extract and register functions
- Store results in context

For **JavaScript** code → `languages/js_lang.py`
- Write code to temporary file
- Execute via Node.js process
- Capture output
- Register functions

For **C** code → `languages/c_lang.py`
- Write code to temporary file
- Compile with gcc
- Execute compiled binary
- Capture output
- Clean up temporary files

For **Java** code → `languages/java_lang.py`
- Write code to temporary file
- Compile with javac
- Execute with java
- Capture output

For **C++** code → `languages/cpp_lang.py`
- Write code to temporary file
- Compile with g++
- Execute compiled binary
- Capture output
- Clean up temporary files

### Step 6: Function Registry

**File:** `core/function_registry.py`

All functions are registered globally:
```python
{
    "python": {
        "greet": <function_object>,
        "add": <function_object>,
    },
    "javascript": {
        "calculateSum": <function_object>,
    },
    "c": {...},
    "java": {...},
    "cpp": {...}
}
```

### Step 7: Type Conversion

**File:** `global_ns/marshalling.py`

When cross-language calls occur:
```python
# Python calling Java function
java_result = call_java("myFunction", py_args)
# Auto-converts Python types → Java types
# Execute in Java
# Convert Java result → Python type
return py_result
```

---

## Example: Running a .poly File

### Example File: `basic_function_call.poly`

```
-- Basic Cross-Language Function Calls Example

global {
    message = "Poly Runtime"
}

python {
    def greet(name):
        return f"Hello, {name}!"
    
    def add(a, b):
        return a + b
    
    greeting = greet("World")
    print(f"Python Function Result: {greeting}")
    
    sum_result = add(10, 20)
    print(f"Python Add Result: {sum_result}")
}

javascript {
    console.log("✅ JavaScript Environment Loaded");
}

c {
    #include <stdio.h>
    
    int main() {
        printf("✅ C Environment Loaded\n");
        return 0;
    }
}

java {
    public class PolyDemo {
        public static void helloFromJava() {
            System.out.println("✅ Java Environment Loaded");
        }
    }
}

cpp {
    #include <iostream>
    
    int main() {
        std::cout << "✅ C++ Environment Loaded" << std::endl;
        return 0;
    }
}

python {
    print("\n=== Summary ===")
    print("✅ All languages successfully registered!")
}
```

### Step 1: Read File

**Command:**
```bash
python poly.py examples/basic_function_call.poly
```

**File loaded:**
```
-- Basic Cross-Language Function Calls Example
global { ... }
python { ... }
javascript { ... }
...
```

### Step 2: Tokenize

Lexer converts text to tokens:
```
COMMENT: "Basic Cross-Language..."
KEYWORD: "global"
LBRACE: "{"
IDENTIFIER: "message"
EQUALS: "="
STRING: "Poly Runtime"
RBRACE: "}"
KEYWORD: "python"
LBRACE: "{"
... (continues for all code)
```

### Step 3: Parse

Parser builds AST:
```
Program
├── GlobalSection
│   └── Assignment
│       ├── target: "message"
│       └── value: "Poly Runtime"
├── LanguageSection(language="python", code="def greet(...)...")
├── LanguageSection(language="javascript", code="console.log(...)")
├── LanguageSection(language="c", code="#include <stdio.h>...")
├── LanguageSection(language="java", code="public class PolyDemo...")
├── LanguageSection(language="cpp", code="#include <iostream>...")
└── LanguageSection(language="python", code="print(...)")
```

### Step 4: Interpret

Interpreter walks AST:

**Step 4a: Process Global Section**
```python
context["global"]["message"] = "Poly Runtime"
```

**Step 4b: Execute Python Block 1**
```python
def greet(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

greeting = greet("World")
# Output: Python Function Result: Hello, World!

sum_result = add(10, 20)
# Output: Python Add Result: 30

# Register functions:
function_registry["python"]["greet"] = greet_function
function_registry["python"]["add"] = add_function
```

**Step 4c: Execute JavaScript Block**
```javascript
console.log("✅ JavaScript Environment Loaded");
// Output: ✅ JavaScript Environment Loaded
```

**Step 4d: Execute C Block**
```c
// Compile and run:
gcc temp_c_code.c -o temp
./temp
// Output: ✅ C Environment Loaded
// Clean up temporary files
```

**Step 4e: Execute Java Block**
```java
// Compile and run:
javac PolyDemo.java
java PolyDemo
// (Java code would execute, but no output in this example)
```

**Step 4f: Execute C++ Block**
```cpp
// Compile and run:
g++ temp_cpp_code.cpp -o temp
./temp
// Output: ✅ C++ Environment Loaded
// Clean up temporary files
```

**Step 4g: Execute Python Block 2**
```python
print("\n=== Summary ===")
# Output: === Summary ===

print("✅ All languages successfully registered!")
# Output: ✅ All languages successfully registered!
```

### Step 5: Final Output

```
Python Function Result: Hello, World!
Python Add Result: 30
✅ JavaScript Environment Loaded
✅ C Environment Loaded
✅ Java Environment Loaded
✅ C++ Environment Loaded

=== Summary ===
✅ All languages successfully registered!
```

---

## How Different Sections Work

### 1. Global Section

```
global {
    var1 = 10
    var2 = "hello"
    status = true
}
```

**What it does:**
- Defines variables accessible from all language blocks
- Sets up global context
- Variables available in all subsequent blocks

**Storage:**
```
context["global"] = {
    "var1": 10,
    "var2": "hello",
    "status": True
}
```

### 2. Python Section

```
python {
    def my_function(x):
        return x * 2
    
    result = my_function(5)
    print(result)
}
```

**What it does:**
- Execute Python code directly
- Define functions available globally
- Print output immediately
- Access global variables

**How it works:**
1. Execute code in Python interpreter
2. Extract function definitions
3. Register in function_registry
4. Print any output

### 3. JavaScript Section

```
javascript {
    function multiply(a, b) {
        return a * b;
    }
    
    console.log(multiply(3, 4));
}
```

**What it does:**
- Execute JavaScript code via Node.js
- Define functions for cross-language calls
- Print output via console.log

**How it works:**
1. Write code to temporary file
2. Execute via Node.js
3. Capture console output
4. Register functions
5. Delete temporary file

### 4. C Section

```
c {
    int add(int a, int b) {
        return a + b;
    }
    
    int main() {
        printf("Result: %d\n", add(5, 3));
        return 0;
    }
}
```

**What it does:**
- Execute C code
- Define functions for cross-language calls
- Print output via printf

**How it works:**
1. Write code to .c file
2. Compile with gcc
3. Execute binary
4. Capture output
5. Register functions
6. Clean up files

### 5. Java Section

```
java {
    public class Calculator {
        public static int subtract(int a, int b) {
            return a - b;
        }
    }
}
```

**What it does:**
- Execute Java code
- Define classes and methods
- Register for cross-language calls

**How it works:**
1. Write code to .java file
2. Compile with javac
3. Execute with java
4. Register methods
5. Clean up files

### 6. C++ Section

```
cpp {
    #include <iostream>
    
    int main() {
        std::cout << "C++ running\n";
        return 0;
    }
}
```

**What it does:**
- Execute C++ code
- Define functions
- Print output

**How it works:**
1. Write code to .cpp file
2. Compile with g++
3. Execute binary
4. Capture output
5. Register functions
6. Clean up files

---

## Key Components in Action

### Lexer (`core/lexer.py`)

Converts raw text to tokens:
```
Input:  "python { print('hello') }"
Output: [KEYWORD("python"), LBRACE(), IDENTIFIER("print"), 
         LPAREN(), STRING("hello"), RPAREN(), RBRACE()]
```

### Parser (`core/parser.py`)

Converts tokens to AST:
```
Input:  Token stream
Output: LanguageSection(
          language="python",
          code="print('hello')"
        )
```

### Interpreter (`core/interpreter.py`)

Walks AST and executes:
```
For each LanguageSection:
  - Get language executor
  - Get code
  - Execute code in that language
  - Register functions
  - Capture output
```

### Language Executors

- `languages/python_lang.py` - Direct execution
- `languages/js_lang.py` - Via Node.js subprocess
- `languages/c_lang.py` - Via gcc compilation
- `languages/java_lang.py` - Via javac + java
- `languages/cpp_lang.py` - Via g++ compilation

### Function Registry (`core/function_registry.py`)

Stores all functions:
```
{
  "python": {"func1": ..., "func2": ...},
  "javascript": {"func3": ...},
  "c": {"func4": ...},
  "java": {"func5": ...},
  "cpp": {"func6": ...}
}
```

### Type Marshalling (`global_ns/marshalling.py`)

Converts between types:
```
Python int (42) → Java Integer (42)
JavaScript string ("hello") → C++ std::string ("hello")
```

---

## Threading & Execution Model

- **Sequential Execution**: Language blocks execute in order
- **No Parallel Execution**: Each block waits for previous to complete
- **Shared Context**: Global variables accessible across blocks
- **Function Registry**: All functions available after registration

---

## Error Handling

When an error occurs:
1. **Syntax Error**: Lexer/Parser catches it
2. **Runtime Error**: Language executor catches it
3. **Type Error**: Marshaller catches incompatible types
4. **File Error**: Handled gracefully

---

## Performance Characteristics

- **Python**: Fastest (direct execution)
- **JavaScript**: Medium (Node.js subprocess)
- **C**: Slow (compilation required)
- **Java**: Slow (compilation + JVM startup)
- **C++**: Slow (compilation required)

---

## Summary

When you run a `.poly` file:

1. **File is read** from disk
2. **Lexer tokenizes** the source code
3. **Parser creates** AST
4. **Interpreter walks** the AST
5. **Each language block executes** in its own environment
6. **Functions register** in global registry
7. **Types convert** automatically between languages
8. **Output prints** to console
9. **Program exits** cleanly

The system is designed to be:
- ✅ **Simple**: Write code in multiple languages in one file
- ✅ **Transparent**: Language switching is automatic
- ✅ **Safe**: Type checking and conversion built-in
- ✅ **Extensible**: Easy to add new languages
