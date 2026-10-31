---

# 004. How Python Works
# हिंदी में: Python अंदर से कैसे काम करता है

---

## 🔵 Simple Definition (English)
When you run `python app.py`, CPython reads your source, parses it into a syntax tree, compiles that to bytecode, and a virtual machine executes the bytecode one instruction at a time. Compiled bytecode is cached in `__pycache__` as `.pyc` files so imports start faster next time.

## 🔵 सरल परिभाषा (Hindi)
`python app.py` चलाने पर CPython आपका source पढ़ता है, उसका syntax tree बनाता है, उसे bytecode में compile करता है, और एक virtual machine bytecode को एक-एक instruction करके चलाती है। Bytecode `__pycache__` में `.pyc` के रूप में cache होता है ताकि अगली बार import तेज़ हो।

---

## 🔴 Problem it Solves
Computers only understand machine code, but humans want readable code that runs on any OS. Python solves this with an intermediate language (bytecode) and a VM: write once, run on Windows, Mac or Linux. Knowing the pipeline also explains interview topics: `.pyc` files, why import runs code, why the GIL exists, and why Python is slower than C.

## 🔴 यह क्यों बना? (Hindi)
Computer सिर्फ machine code समझता है, पर इंसान को readable code चाहिए जो हर OS पर चले। Python बीच की भाषा (bytecode) और VM से यह हल करती है। यह pipeline जानने से `.pyc`, import का code चलाना, GIL और Python की धीमी speed समझ आती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Tokenizer: text → tokens (NAME, NUMBER, OP ...)
Step 2 → Parser: tokens → AST (Abstract Syntax Tree)
Step 3 → Compiler: AST → bytecode (code object)
Step 4 → Cache: bytecode saved to __pycache__/x.cpython-313.pyc (imports only)
Step 5 → Eval loop: VM runs bytecode on a value stack, frame by frame
Step 6 → Memory: objects live on a heap, freed by reference counting (+ cyclic GC)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tokenizer: text को tokens में तोड़ता है
Step 2 → Parser: tokens से AST (syntax tree) बनाता है
Step 3 → Compiler: AST से bytecode बनाता है
Step 4 → Cache: import किए module का bytecode __pycache__ में सेव होता है
Step 5 → Eval loop: VM bytecode को stack पर एक-एक instruction चलाती है
Step 6 → Memory: objects heap पर, reference counting + cyclic GC से free होते हैं
```

---

## 🟡 Real World Example
A FastAPI service at a fintech starts slowly in production containers. The team pre-compiles bytecode in the Docker image (`python -m compileall`) so the first request does not pay the compile cost. Another team debugs a slow function with `dis` to see it creates a new list on every call. Understanding the pipeline turns guesses into evidence.

## 🟡 Real Example Hindi mein
Fintech की FastAPI service production container में धीरे start होती है। Team Docker image में bytecode पहले से बना देती है (`python -m compileall`) ताकि पहली request पर compile का समय न लगे। दूसरी team `dis` से देखती है कि function हर call पर नई list बना रहा है। Pipeline समझने से अंदाज़े की जगह सबूत मिलते हैं।

---

## 💻 Code Example — Basic
```python
# Peek inside the pipeline: source -> code object -> bytecode -> run

import dis  # disassembler: shows bytecode instructions

source: str = "x = 2 + 3\nprint(x * 10)"  # a tiny program stored as text

code = compile(source, "<demo>", "exec")  # steps 1-3: tokenize, parse, compile
print(type(code).__name__)  # code
print(code.co_names)  # names used in the program -> ('x', 'print')
print(code.co_consts[:2])  # constants (2 + 3 is folded to 5) -> (5, 10)

exec(code)  # step 5: VM runs the bytecode -> prints 50


def square(n: int) -> int:  # a normal function also becomes a code object
    return n * n  # body is compiled once at definition time


print(square.__code__.co_varnames)  # local variable names -> ('n',)
print(square.__code__.co_argcount)  # number of parameters -> 1

# Show the instruction names (version-independent check):
names = [ins.opname for ins in dis.get_instructions(square)]  # list opcodes
print("RETURN_VALUE" in names or "RETURN_CONST" in names)  # True
print("BINARY_OP" in names)  # True on Python 3.11+
```

## 💻 Code Example — Advanced
```python
# Production-style inspection: pyc cache path, AST, and import side effects

import ast  # parse source into a tree
import importlib.util  # compute cache file path
import sys  # access module cache
import tempfile  # temp directory for a demo module
from pathlib import Path  # path handling


def show_ast(expr: str) -> str:  # return AST dump for an expression
    tree = ast.parse(expr, mode="eval")  # step 2: parser makes the tree
    return ast.dump(tree.body)  # compact textual form


def main() -> None:  # entry point
    print(show_ast("a + 1"))  # BinOp(left=Name(id='a', ctx=Load()), op=Add(), right=Constant(value=1))

    with tempfile.TemporaryDirectory() as tmp:  # auto-cleaned folder
        mod_path = Path(tmp) / "demo_mod.py"  # module file
        mod_path.write_text("print('demo_mod body runs')\nVALUE = 42\n")  # source
        sys.path.insert(0, tmp)  # let import find the folder
        try:
            import demo_mod  # first import: compiles, writes .pyc, RUNS the body
            import demo_mod as again  # second import: served from sys.modules cache
            print(demo_mod.VALUE, again is demo_mod)  # 42 True
            cache = importlib.util.cache_from_source(str(mod_path))  # pyc path
            print(Path(cache).parent.name)  # __pycache__
            print(Path(cache).exists())  # True: bytecode was cached
        finally:
            sys.path.remove(tmp)  # restore import path
            sys.modules.pop("demo_mod", None)  # forget the temp module


if __name__ == "__main__":  # only when run directly
    main()  # start
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: module body runs once on first import, then is cached in sys.modules
import sys  # module registry

import json  # first import loads and caches json
print("json" in sys.modules)  # True - like Node's require.cache
```
```javascript
// JavaScript (Node.js): the module is executed once and cached
const json = require("fs"); // first require runs the module
console.log(Object.keys(require.cache).length > 0); // true
```
Differences: JS engines (V8) JIT-compile hot functions to machine code, so they are often faster. CPython (3.13) has an experimental JIT but mainly interprets bytecode. Python's cache is `__pycache__/*.pyc`; Node has no on-disk bytecode cache by default.

---

## 🟠 FastAPI Connection
When uvicorn imports `main:app`, Python executes the whole `main.py` top to bottom once: decorators run, routes register, Pydantic models are built. That is why heavy work at module top-level slows startup, and why `--reload` re-imports modules.

```python
# FastAPI example (needs: pip install fastapi uvicorn)
from fastapi import FastAPI  # imported once, cached in sys.modules

print("module body runs once at import")  # appears once at server start

app = FastAPI()  # created at import time


@app.get("/ping")  # decorator runs at import: registers the route
def ping() -> dict[str, str]:  # function body compiled now, run per request
    return {"status": "ok"}  # executed only when the route is called
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `.pyc` files are a security or deployment artifact you must commit
```python
# Wrong: committing __pycache__/ to git (bytecode is version specific)
# Right: add it to .gitignore
#   __pycache__/
#   *.pyc
```
✅ Correct: `.pyc` is regenerated automatically; ignore it in git.

❌ Mistake 2: Putting slow or side-effect code at module level
```python
# Wrong: runs on every import (even for tests or tools)
# data = load_giant_model()       # takes 30 seconds on import!

# Right: wrap in a function or guard with __main__
def load_model() -> str:
    return "model"  # load lazily when needed

if __name__ == "__main__":
    print(load_model())  # only when run as a script
```
✅ Correct: keep module top-level cheap; do work inside functions.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import sys

print("start")
x = 1
def f() -> None:
    print("in f")
print(__name__)
print("f" in dir())
print("sys" in dir())
```
Answer: `start`, `__main__`, `True`, `True`. Statements run top to bottom; `def` itself executes (creating the function object) but the body of `f` does not run until called, so "in f" never prints. When the file is run directly `__name__` is `"__main__"`; when imported it is the module name.

---

## ⚫ Interview Questions + Answers

Q1: Is Python compiled or interpreted?
A1: Both. CPython compiles source to bytecode, then the VM interprets that bytecode. So it is "compiled to bytecode, interpreted by a VM". It is not compiled to native machine code (unless you use PyPy's JIT, Cython, or Nuitka).

Q2: What is a `.pyc` file and where is it stored?
A2: It is cached bytecode of an imported module, stored in `__pycache__/name.cpython-313.pyc`. It is only created for imported modules, not for the script you run directly. It is skipped if the source file's modification time or hash changed, so stale caches are safe.

Q3: What does the `dis` module do?
A3: It disassembles a function or code object to readable bytecode instructions like `LOAD_FAST`, `BINARY_OP`, `RETURN_VALUE`. Used to understand performance and behaviour, e.g. why `x += 1` in a loop is slow or how a closure captures variables.

Q4: What happens when you `import` a module twice?
A4: The first import finds the file, compiles (or loads `.pyc`), executes the module body, and stores the module object in `sys.modules`. The second import returns the cached object without re-running code. Use `importlib.reload` to force it.

Q5: How does Python manage memory?
A5: Every object has a reference count; when it hits zero the memory is freed immediately. A cyclic garbage collector (`gc` module) additionally finds reference cycles (A refers to B, B refers to A). Memory comes from Python's private heap managed by pymalloc.

---

## 🔷 When to Use + When Not to Use

✅ Use this knowledge when:
- Debugging slow startup, import cycles, or surprising module-level side effects
- Explaining performance to interviewers and teammates
- Building Docker images (pre-compile, ignore caches)

❌ Avoid:
- Relying on bytecode details in application logic; opcodes change between versions
- Shipping `.pyc` only as "protection" - it is easily decompiled

---

## 📊 Visual Diagram
```
 app.py
   │  tokenizer
   ▼
 tokens ──parser──► AST ──compiler──► code object (bytecode)
                                         │            │
                                         │            └─► __pycache__/app.cpython-313.pyc
                                         ▼
                                  CPython eval loop
                              (value stack, frames, refcounts)
                                         │
                                         ▼
                                   OS / C library
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bytecode | Low-level instructions for the VM | VM के लिए low-level instructions |
| AST | Tree form of source code | Source का tree रूप |
| Code object | Compiled unit (`__code__`) | Compile हुआ unit |
| `.pyc` | Cached bytecode file | Cache किया bytecode file |
| `sys.modules` | Cache of imported modules | Import हुए modules का cache |
| Reference count | Number of references to an object | Object के references की गिनती |

---

## ⚡ 3-Line Summary
English: Python source goes through tokenizer, parser and compiler to become bytecode, which the CPython VM runs. Imports are cached in `sys.modules` and `.pyc` files. Module-level code runs once on import, so keep it cheap.
Hindi: Source -> tokenizer -> parser -> compiler -> bytecode, जिसे CPython VM चलाती है। Imports `sys.modules` और `.pyc` में cache होते हैं। Module-level code import पर एक बार चलता है, इसलिए उसे हल्का रखें।

---

## ➡️ Next Topic
**005. CPython vs PyPy vs Jython** — the different Python implementations and when each matters.
