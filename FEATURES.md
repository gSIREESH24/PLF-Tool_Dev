# Poly Runtime — Features Explained (Simple English)

This file explains each roadmap topic in simple English with short examples.

## Define language goals
- What it means: Decide what problems the language solves (web, data, scripts).
- Example: "Poly is for small web servers and scripting with easy syntax."

## Design syntax & grammar
- What it means: Choose how code looks and write a formal grammar (EBNF).
- Example grammar snippet:
```
program = { statement } ;
statement = "let" identifier "=" expression ";" ;
```

## Write formal spec
- What it means: A written document that says exactly how the language works.
- Example: Describe operator precedence and how `if` behaves.

## Implement lexer & parser
- What it means: Turn characters into tokens (lexer) and tokens into syntax tree (parser).
- Example tokens: `LET`, `IDENT`, `NUMBER`, `;`

## Build AST & IR
- What it means: AST = tree of code structure; IR = simpler form used by compiler or VM.
- Example AST node: `Let(name="x", value=Number(3))`

## Implement semantic analysis
- What it means: Check meaning - names exist, types match, no duplicate functions.
- Example check: Error if `print(x)` but `x` was never defined.

## Type system & inference
- What it means: Decide if language is typed; inference guesses types for you.
- Example: `let x = 1` means `x` is an integer without writing `int`.

## Runtime/VM implementation
- What it means: The program that runs compiled bytecode or interprets AST.
- Example: `vm.run(bytecode)` executes compiled instructions.

## Memory management/GC
- What it means: How the language frees unused memory (automatic GC or manual).
- Example policies: reference counting or mark-and-sweep tracing.

## Standard library core
- What it means: Basic helpers (print, strings, lists, file I/O) available to users.
- Example: `print("Hello")`, `List.map([1,2,3], fn)`

## Module & package system
- What it means: How code is organized into files and imported by name.
- Example: `import http` or `from utils import read_file`

## Package manager CLI
- What it means: Tool to add, remove, and publish third-party libraries.
- Example commands: `poly pkg init`, `poly pkg install http@1.0.0`

## REPL & CLI tooling
- What it means: Interactive shell and command-line tools to run scripts.
- Example REPL: `> let x = 2; x * 3` outputs `6`.

## Formatter & linter
- What it means: Auto-format code style and warn about possible bugs.
- Example: `poly fmt file.poly` or linter warning: "unused variable `y`."

## Language Server (LSP)
- What it means: Editor features like autocomplete, go-to-definition, and errors.
- Example: Typing `str.` shows available string methods.

## Debugger integration
- What it means: Set breakpoints, step through code, inspect variables.
- Example: `break main:10` pauses program at line 10 for inspection.

## Testing framework
- What it means: Tools to write and run unit and integration tests.
- Example test: `assert add(2,3) == 5`

## CI/CD pipelines
- What it means: Automated steps to run tests and build releases on each change.
- Example: On push, run `poly test` then build artifacts.

## Performance optimizer / JIT
- What it means: Make programs run faster (optimizations or just-in-time compilation).
- Example: Hot loop compiled to faster machine code at runtime.

## Foreign Function Interface
- What it means: Call code written in other languages like C.
- Example: `ffi.call("libc", "printf", "Hello %s", name)`

## Concurrency & scheduler
- What it means: How the language runs many tasks at once (threads, async).
- Example: `async fn fetch() { await http.get(url) }`

## Security & sandboxing
- What it means: Limit what programs can do (file access, network) for safety.
- Example: Run untrusted code with memory and time limits.

## Documentation site
- What it means: Public docs with guides, API reference, and tutorials.
- Example content: "Getting started", "Language reference", "Standard library".

## Example projects & demos
- What it means: Sample apps that show how to use the language.
- Example demos: simple web server, CLI tool, data parser.

## Cross-platform packaging
- What it means: Build runnable packages for Windows, macOS, and Linux.
- Example: `poly build --target=windows` produces an .exe bundle.

## Community & contribution guide
- What it means: Rules and steps for contributors (code style, PR process).
- Example: `CONTRIBUTING.md` explains how to open issues and tests required.

---
If you want any section expanded with longer examples or code in the actual `poly` language, tell me which items and I will add more detailed examples or create small demos in `languages/`.

## First — Important Features to Add Now (MVP + near-MVP)
These are the features to implement first so the language is useful and testable.

- **Function calls & expressions**
	- Why: Functions are the building blocks of programs.
	- Simple description: Support defining and calling functions, passing arguments, and returning values.
	- Example:
	```
	fn add(a, b) { return a + b }
	let x = add(2, 3)  # x == 5
	```
	- How to scale: Add closures (functions that capture variables), first-class functions (store and pass functions), method calls on objects, tail-call optimization, and efficient call frames in the VM.

- **Control flow (if, loops, switch)**
	- Why: Control flow lets programs make decisions and repeat work.
	- Simple description: Implement `if/else`, `while`/`for` loops, and a `match`/`switch` style later.
	- Example:
	```
	if x > 0 { print("positive") } else { print("non-positive") }
	```
	- How to scale: Add pattern matching, loop iterators, labeled breaks, and compile-time checks to optimize branches.

- **Basic types & collections**
	- Why: Needed to store and manipulate data.
	- Simple description: Provide numbers, strings, booleans, lists/arrays, maps/dictionaries.
	- Example:
	```
	let nums = [1,2,3]
	let m = { "name": "sireesh" }
	```
	- How to scale: Add structs/records, enums, generics/templates, and immutable vs mutable types.

- **I/O and filesystem**
	- Why: Scripts and apps must read/write files and talk to the outside world.
	- Simple description: Provide simple APIs for reading/writing files and printing to console.
	- Example:
	```
	let text = fs.read("notes.txt")
	fs.write("out.txt", text)
	```
	- How to scale: Add async I/O, streaming APIs, buffered readers/writers, and secure file access controls.

- **Module & import system**
	- Why: Keeps code organized and reusable.
	- Simple description: Allow splitting code across files and importing names.
	- Example:
	```
	// utils.poly
	export fn read_all(path) { ... }

	// main.poly
	import utils
	let s = utils.read_all("a.txt")
	```
	- How to scale: Add package namespaces, versioned imports, import locking, and lazy loading.

- **REPL & CLI runner**
	- Why: Makes trying the language fast and useful for teaching and debugging.
	- Simple description: An interactive prompt plus a `poly run file.poly` command.
	- Example REPL session:
	```
	> let x = 10
	> x * 2
	20
	```
	- How to scale: Add history, tab completion, multi-line editing, and an embeddable REPL API.

- **Standard library (core)**
	- Why: Developers expect common helpers out of the box.
	- Simple description: Provide string manipulation, collections helpers, basic math, and time utilities.
	- Example: `String.split`, `List.map`, `Math.sqrt`
	- How to scale: Move parts of the stdlib to small modules so they can be versioned independently and replaced with native implementations for speed.

- **Testing framework**
	- Why: Ensures code works and lets contributors add features safely.
	- Simple description: A tiny unit-test runner with `assert` and test discovery.
	- Example:
	```
	test add_tests { assert add(1,2) == 3 }
	```
	- How to scale: Add fixtures, mocking, coverage reporting, and support for property-based tests.

- **Package manager (simple)**
	- Why: Share libraries and reuse code.
	- Simple description: A CLI tool to install dependencies and a small manifest file (like `poly.toml`).
	- Example: `poly pkg install http` adds `http` to project.
	- How to scale: Add a hosted registry, signing, dependency resolution, and lockfiles for reproducible builds.

- **Foreign Function Interface (FFI)**
	- Why: Use existing native libraries for performance or OS features.
	- Simple description: Allow calling C functions or embedding a JS/Python runtime.
	- Example (C):
	```
	ffi.import("libc", { printf: "int(char*)" })
	ffi.call("printf", "Hello %s\n", "Poly")
	```
	- How to scale: Define safe ABI boundaries, automatic type marshaling, versioned bindings, and sandboxing for untrusted native modules.

## Different-language function calls and interop
Supporting calls to other languages is important and should be planned from the start.

- **Why**: Access mature ecosystems (databases, crypto, graphics) and reuse libraries.
- **Simple approaches**:
	- C FFI: expose a C-compatible ABI; easiest and fastest.
	- Embedding: run a JS or Python runtime inside your VM and call between runtimes.
	- RPC: run services in other languages and communicate over IPC/HTTP for safer isolation.
- **Example: call JS function** (conceptual):
	```
	js.eval("function greet(n) { return 'hi '+n }")
	let s = js.call("greet", "Sireesh")  # s == "hi Sireesh"
	```
- **Scaling concerns**: data marshaling cost, async interruption, memory ownership, error boundary translation, and security. Prefer a layered approach: start with C-FFI, add an embedding bridge, and later design cross-language async/await patterns.

## How to design for scale (architecture & policies)
Here's simple, practical guidance to make the project grow without becoming unmanageable.

- **Modular compiler/runtime**
	- Keep lexer, parser, AST, IR, optimizer, codegen, and runtime as separate modules with clear interfaces.
	- Benefit: teams can improve parts independently and add alternate backends (bytecode, LLVM).

- **Pluggable stdlib and modules**
	- Ship a small core and provide optional modules as separate packages.
	- Benefit: users only install what they need; core stays small.

- **Stable public API & semantic versioning**
	- Define clear public APIs for runtime and toolchain; follow semver.
	- Benefit: external packages remain compatible across releases.

- **Tooling-first approach**
	- Build formatter, linter, and LSP early to improve contributor experience.
	- Benefit: easier onboarding and higher code quality.

- **Test & CI culture**
	- Require unit tests for features; run tests in CI on push/PR.
	- Benefit: prevents regressions and supports many contributors.

- **Performance & profiling**
	- Add benchmarks and a profiler from the start so performance regressions are visible.
	- Benefit: targeted optimization rather than guesswork.

- **Security & sandboxing**
	- Design a sandbox for running untrusted code (resource limits, syscalls filters).
	- Benefit: enables using the language in multi-tenant or education settings.

- **Community & contribution model**
	- Create `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and clear issue/PR templates.
	- Benefit: lowers friction for new contributors and keeps the project healthy.

## Simple scaling examples (practical)
- Add a new backend without touching the parser by using the IR as the contract: parser -> AST -> IR -> backend A (bytecode) or backend B (LLVM).
- Split the standard library into `core` and `extras` packages; `core` installs with runtime, `extras` come from package manager.
- Provide a small HTTP-based package registry for the package manager; later mirror to a CDN.


