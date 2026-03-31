# Poly (PLF-Tool) - The Ultimate Polyglot Framework

Welcome to the Poly Language Framework (PLF) - a revolutionary step forward in true polyglot software engineering. PLF breaks down language barriers, allowing you to execute Python, JavaScript, C++, Java, and C seamlessly in the same source file (`.poly`).

Not only does it allow you to write multiple languages cohesively, but it provides **transparent data bindings**, allowing variables, functions, and deeply-nested Object-Oriented classes to traverse across all these runtime boundaries magically.

---

## Table of Contents

1. [Introduction](#introduction)
2. [What Are The Uses of This Project?](#what-are-the-uses-of-this-project)
3. [Architecture and Design](#architecture-and-design)
4. [Project Structure](#project-structure)
5. [Syntax and Core Concepts](#syntax-and-core-concepts)
6. [Variable and Context Binding](#variable-and-context-binding)
7. [Cross-Language Functions](#cross-language-functions)
8. [Global and Local Object-Oriented Programming](#global-and-local-object-oriented-programming)
9. [Supported Languages Deep Dive](#supported-languages-deep-dive)
10. [Usage & CLI](#usage--cli)
11. [Extending PLF](#extending-plf)

---

## Introduction

Modern technology stacks frequently struggle with integrating disparate ecosystems. You might want the unmatched machine-learning capabilities of Python, the raw asynchronous I/O speed of Node.js (JavaScript), the extreme CPU-bound performance of C++, and the enterprise-level robustness of Java all in one single workflow.

Normally, developers have to set up REST APIs, gRPC, Microservices, or complex message queues like RabbitMQ or Kafka just to exchange a single data structure or orchestrate a multi-language pipeline.

The **Poly Language Framework (PLF)** solves this by introducing `.poly` files. A PLF script coordinates scripts via an advanced, abstracted AST parser, passing execution contexts, serializing objects behind the scenes, and bridging functions natively.

---

## What Are The Uses of This Project?

PLF is incredibly powerful and has a wide array of high-value use cases:

*   **Machine Learning + High-Performance Pipelines**: You can do heavy data processing in C++, feed the data immediately into Python to train a TensorFlow model, and then instantly serve the inferences using JavaScript.
*   **Legacy Code Migration & Modernization**: Interleave legacy C or Java code natively within a new Python orchestrator to slowly replace parts without breaking monolithic workflows or spending millions on an explicit rewrite.
*   **Prototyping & Rapid Development**: Instead of mocking dependencies across multiple languages or stitching APIs, you can write everything in one script file to prove a full-stack algorithmic concept works.
*   **Educational Environments**: Teaching a concept like Object-Oriented Programming (OOP) sequentially across Python, Java, JS, and C++ in a single file reduces cognitive load and allows immediate side-by-side comparison for students.
*   **Automated Testing & Integration**: Perform integration testing natively. You can trigger a C++ backend routine right from the script and instantly assert the database changes using Python within the identical context.
*   **Algorithm Optimization**: Write an algorithm in Python, port it over block-by-block to C++ or Java within the same file, and instantly compare the execution speed and accuracy of the output natively.

---

## Architecture and Design

PLF operates entirely on a single-pass orchestration model guided by an Interpreter and a powerful Context Engine.

1.  **Lexer & Parser**: The `core/parser.py` consumes `.poly` plain text files. Instead of a traditional grammar, it parses blocks scoped by `language { ... }` segments, segregating language-specific code into individual `BlockNode` structures.
2.  **Global AST & Context Engine**: The `core/context.py` holds execution variables iteratively. Variables defined in `global` or explicitly exported from `python` are captured and serialized via a highly robust marshalling engine based on JSON and dictionary translations.
3.  **Function Registry (`core/function_registry.py`)**: Intercepts `def` inside global configurations and extracts AST signatures dynamically allowing JS and Python blocks to call cross-platform routines seamlessly.
4.  **Class Registry (`core/class_registry.py`)**: Captures `class` definitions inside the abstract `global` scope, and dynamically generates the exact class schemas in Python (`class`), JavaScript ES6 (`class`), C++ (`class`, public struct mappings), and Java (`public class`).

---

## Project Structure

The filesystem structure ensures modularity and decoupling of the interpreter pipeline.

*   **`/`**: Root. Holds `poly.py` parser script and `poly.bat` convenience script.
*   **`core/`**: 
    *   `ast.py`, `lexer.py`, `parser.py`: Structural tree breakdown of the `.poly` script.
    *   `interpreter.py`: The heart of the program that sequences the `global` definitions and hands operations over to individual runners.
    *   `context.py`: Holds references to active exported variables and states.
    *   `function_registry.py` & `class_registry.py`: Manage state for functions and cross-language class bridging.
*   **`languages/`**:
    *   Contains `<lang>_lang.py` files for `python`, `js`, `cpp`, `java`, and `c`.
    *   Each file implements a `run()` method taking `code`, `context`, and `registry`. Standard Output is captured synchronously.
*   **`global_ns/`**:
    *   Houses internal bootstrapping capabilities and `marshalling.py` for advanced AST translations across boundaries.
*   **`examples/`**:
    *   Various sandbox environments and `.poly` files providing demonstrations of context bindings.

---

## Syntax and Core Concepts

A standard `.poly` file consists of `blocks`. A block explicitly specifies the language it intends to compile and run under.

```poly
global {
    my_shared_var = 12345
}

python {
    print("Python running. Variable:", my_shared_var)
    local_python_var = [1, 2, 3]
    export("nums", local_python_var)
}

javascript {
    console.log("JS running! Nums length:", nums.length);
}
```

The execution paradigm is completely synchronous. A Python block executes, halts, modifies the `Context`, and subsequently, the JS block boots, reads the Context, and proceeds.

---

## Variable and Context Binding

The most powerful feature of PLF is avoiding manually serializing data.
When in a block, you can modify the context:

*   **Python**: Automatically extracts all top-level variables and adds them to context if they aren't functions. Can explicitly use `export("name", value)`.
*   **JavaScript**: Variables from the Context are injected via Node.js AST templates statically as strings before `node -e` is invoked.

*Currently C++ and Java are structurally rigid; variables usually only cascade natively through object instantiations or function wrappers rather than loosely-typed JSON dumps directly into compiled routines, though this relies on the specific `Adapter` implementations.*

---

## Cross-Language Functions

The `function_registry` actively detects functions written in the global block.

```poly
global {
    python {
        def global_math_add(a, b):
            return a + b
    }
}
```

This function traverses the internal PLF AST and calculates its parameter signatures using `core/function_signature.py`. Once mapped, a pseudo-stub is natively mapped across local bounds so that other local python routines or inter-language calls (like JS `polyCall` adapters) can successfully resolve to the original procedure!

---

## Global and Local Object-Oriented Programming

A colossal achievement within the PLF project is the seamless integration of deeply structured Class typings and state mechanisms using the **ClassRegistry** framework.

**Global Scope Abstract Classes**
By declaring a pure `class` structure in the `global` block, PLF extracts the class blueprint. 
```poly
global {
    class Product {
        string name
        float price
    }
}
```

Behind the scenes, the `core/class_registry.py` processes this `Product` and generates equivalent boilerplate class codes for every single supported OOP language! 
1. **Python**: Creates a `class Product` with a standardized `__init__` constructor and an auto-generated `to_dict()` routine.
2. **JavaScript**: Renders an ES6 `class Product` with a native `constructor(...)` implementation.
3. **C++**: Compiles a standard class definition with inline constructors handling `std::string` bindings gracefully.
4. **Java**: Prepends a pure POJO (Plain Old Java Object) `class Product` outside of the primary `PolyJavaRuntime` domain to guarantee successful independent instantiations.

**Cross-Boundary Object Transfer**
You can instantiate a class locally, mapping it securely within the framework natively, OR you can instantiate it in the global context, exporting it identically across languages. Every boundary respects the local class blueprint internally without requiring manual `JSON.parse` or casting mechanisms manually.

---

## Supported Languages Deep Dive

### Python (`python_lang.py`)
Executed utilizing the native `exec()` command inside the existing orchestration python kernel. Thus, it can bind `local_env` extremely cleanly and capture internal variables directly via standard `dict.items()`. It handles OOP natively via Python's `inspect` capabilities to evaluate which artifacts are exported back to `Context`.

### JavaScript (`js_lang.py`)
Runs effectively by spawning an external Node.js process `subprocess.run(["node", "-e", code])`. The runner actively builds a massive JS prefix containing `var x = y;` JSON mappings to securely translate context into the Node engine. It also auto-hooks standard ES6 Classes into the preamble allowing JS to treat Global classes natively.

### C++ (`cpp_lang.py`)
Relies on spawning G++ processes (either directly via bash or via `tempfile` handling inside `.tmp` environments on Windows). The context explicitly renders `#include <string>` and `#include <iostream>` wrappers, constructs the C++ `class` abstractions natively above your `int main()` code block natively. Temporary binaries (`.exe` on NT) are instantly wiped gracefully upon task termination ensuring clean environments.

### Java (`java_lang.py`)
Acts upon explicit `javac` processes spawned dynamically from temp directories. If the user invokes Java without abstract classes, it injects them into a `PolyJavaRuntime` entrypoint. Otherwise, PLF correctly attaches abstract Global classes synchronously without messing with access modifiers like `public/private` improperly, preventing JVM strictness errors natively.

---

## Usage & CLI

There's no complex compilation configuration or `tsconfig.json` overhead. You write exactly what you need in the script and execute it immediately through the entrypoint.

Command Line Arguments:
```bash
# General formatting natively executed leveraging Python
python poly.py my_script.poly

# On Windows utilizing the dedicated batch script runtime
poly.bat my_script.poly
```

**Common Flags / Parameters:**
Currently, parameters are strict to file executions natively. Be sure your host operating system has `node`, `javac`, and `g++` added locally within its `$PATH` variable for executions outside Python to proceed fully undisturbed.

---

## Extending PLF

Extensibility relies intrinsically on the `languages/` plugins constraint module!

1. Create `languages/rust_lang.py`.
2. Define a solitary `def run(code, context, registry, is_global):` method.
3. Register the runner globally within `languages/__init__.py`.

By expanding `FunctionRegistry` and `ClassRegistry` endpoints, developers can actively orchestrate data serialization into virtually any high-capacity runtime safely!

---
*Created and maintained under the Poly_Env workspace. Pushing boundaries through true interoperability.*
