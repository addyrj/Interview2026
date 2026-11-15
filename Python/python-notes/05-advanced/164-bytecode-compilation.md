---

# 164. Bytecode Compilation
# हिंदी में: Bytecode Compilation (Python code का बीच वाला रूप)

---

## 🔵 Simple Definition (English)
Python does not run your source text directly. It first compiles it to bytecode, a compact list of simple instructions, and then the Python virtual machine (PVM) runs that bytecode. For imported modules the bytecode is cached in `.pyc` files inside `__pycache__`.

## 🔵 सरल परिभाषा (Hindi)
Python आपके source text को सीधे नहीं चलाता। पहले वह उसे bytecode में compile करता है, यानी सरल instructions की छोटी list, और फिर Python virtual machine (PVM) उस bytecode को चलाती है। Import किए गए modules का bytecode `__pycache__` के अंदर `.pyc` files में cache होता है।

---

## 🔴 Problem it Solves
Parsing and compiling text on every start costs time. Pure interpretation of text would be slow, and compiling all the way to machine code would lose portability. Bytecode is the middle path: platform independent, fast to execute, and cacheable on disk. Next time you import the same module, Python skips parsing and loads the `.pyc` if the source did not change.

## 🔴 यह क्यों बना? (Hindi)
हर बार start पर text को parse और compile करना समय लेता है। Text को सीधे interpret करना धीमा होता और machine code तक compile करने से portability जाती। Bytecode बीच का रास्ता है: platform से स्वतंत्र, चलाने में तेज़ और disk पर cache हो सकने वाला। अगली बार वही module import होने पर, अगर source नहीं बदला, तो Python parsing छोड़कर `.pyc` load कर लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Source text is tokenized and parsed into an AST
Step 2 → The compiler walks the AST, applies simple optimisations
           (constant folding: 2**10 becomes 1024), and emits bytecode
Step 3 → The result is a code object: co_code (bytes), co_consts, co_names, co_varnames
Step 4 → For an imported module, the code object is saved with marshal into
           __pycache__/name.cpython-313.pyc  (16-byte header + code)
Step 5 → The header has a magic number (Python version) and source mtime/size or hash
Step 6 → Next import: header matches -> load .pyc; otherwise recompile
Step 7 → The PVM loop runs each instruction (3.11+ may "specialise" hot instructions)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Source text tokenize और parse होकर AST बनता है
Step 2 → Compiler AST पर चलता है, छोटे optimisations करता है
           (constant folding: 2**10 बन जाता है 1024) और bytecode बनाता है
Step 3 → नतीजा एक code object है: co_code (bytes), co_consts, co_names, co_varnames
Step 4 → Import हुए module का code object marshal से
           __pycache__/name.cpython-313.pyc में save होता है (16-byte header + code)
Step 5 → Header में magic number (Python version) और source का mtime/size या hash होता है
Step 6 → अगली import पर: header मिले तो .pyc load, नहीं तो फिर compile
Step 7 → PVM loop हर instruction चलाता है (3.11+ में hot instructions "specialise" हो सकती हैं)
```

---

## 🟡 Real World Example
In a Docker image for a FastAPI service, startup imports hundreds of modules. If `__pycache__` is missing, every container start recompiles them, which slows cold starts. Teams run `python -m compileall` during the image build to pre-create `.pyc` files, or keep the default so Python writes them on first run. Read-only containers need pre-compiled `.pyc` or `PYTHONPYCACHEPREFIX`.

## 🟡 Real Example Hindi mein
FastAPI service के Docker image में start पर सैकड़ों modules import होते हैं। अगर `__pycache__` नहीं है तो हर container start पर सब दोबारा compile होते हैं, जिससे cold start धीमा होता है। Teams image build के दौरान `python -m compileall` चलाकर `.pyc` पहले से बना लेती हैं, या default रखती हैं ताकि Python पहली बार चलने पर लिख दे। Read-only containers में pre-compiled `.pyc` या `PYTHONPYCACHEPREFIX` चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic bytecode examples
import sys                                        # version info

def add(a: int, b: int) -> int:                   # simple function
    return a + b                                  # one addition

co = add.__code__                                 # the compiled code object
print(co.co_name, co.co_varnames)                 # name and local variable names
print(co.co_argcount, co.co_consts)               # arg count and constants
print(type(co.co_code).__name__, len(co.co_code) > 0)   # raw bytecode is bytes
print(list(co.co_code[:4]))                       # first instruction as numbers (version dependent)

code = compile("print('hi', 2 + 3)", "<s>", "exec")   # source -> code object (no file)
exec(code)                                        # run it
print(code.co_consts)                             # 2 + 3 was folded into 5 at compile time
print(sys.version_info[:2])                       # the .pyc magic number depends on this

# Output:
# add ('a', 'b')
# 2 (None,)
# bytes True
# [149, 0, 88, 1]
# hi 5
# ('hi', 5, None)
# (3, 13)
```

## 💻 Code Example — Advanced
```python
# Production style: inspect the .pyc cache the way Python really does
import importlib.util                             # magic number and cache path helpers
import marshal                                    # code object (de)serialiser
import py_compile                                 # explicit compile to .pyc
import sys                                        # version
import tempfile                                   # throw-away folder
from pathlib import Path                          # paths

with tempfile.TemporaryDirectory() as tmp:        # work in a temp dir
    src: Path = Path(tmp) / "mod.py"              # a module file
    src.write_text("VALUE = 6 * 7\n")             # tiny module
    pyc: str = py_compile.compile(str(src), doraise=True)   # compile to __pycache__
    pyc_path: Path = Path(pyc)                    # path of the cache file
    print(pyc_path.parent.name, pyc_path.name)    # __pycache__ mod.cpython-313.pyc
    print(pyc_path == Path(importlib.util.cache_from_source(str(src))))   # same place import uses

    data: bytes = pyc_path.read_bytes()           # raw cache bytes
    print(data[:4] == importlib.util.MAGIC_NUMBER)   # first 4 bytes = interpreter magic number
    flags: int = int.from_bytes(data[4:8], "little")   # 0 = validate by source mtime+size
    print("flags:", flags)                        # 0 for a default timestamp pyc
    code = marshal.loads(data[16:])               # header is 16 bytes, then the code object
    ns: dict[str, int] = {}                       # namespace
    exec(code, ns)                                # run the cached code
    print(ns["VALUE"])                            # 42

print(f"cache tag: {sys.implementation.cache_tag}")   # e.g. cpython-313
print("only imported modules get a .pyc; the main script is compiled in memory each run")

# Output:
# __pycache__ mod.cpython-313.pyc
# True
# True
# flags: 0
# 42
# cache tag: cpython-313
# only imported modules get a .pyc; the main script is compiled in memory each run
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (V8) |
|---------|--------|-----------------|
| Intermediate form | bytecode in code objects | Ignition bytecode (internal) |
| Cached on disk | `.pyc` in `__pycache__` | V8 code cache (opt-in, not a public file) |
| Inspect it | `dis`, `__code__` | `node --print-bytecode` |
| JIT to machine code | not in CPython (experimental JIT in 3.13) | TurboFan JIT, always on |
| Version tied | yes (magic number) | yes (V8 version) |

```python
# Python way
def f() -> int:
    return 2 ** 10
print(f.__code__.co_consts)                     # (None, 1024) constant folded
```
```javascript
// JavaScript way
function f() { return 2 ** 10; }
// V8 compiles to bytecode internally; see it with:  node --print-bytecode script.js
```

Key difference: Python's bytecode and `.pyc` files are visible and easy to inspect. V8's bytecode is internal and followed by a JIT that compiles hot code to machine code, which is why JavaScript is often faster on CPU-heavy loops.

---

## 🟠 FastAPI Connection
A FastAPI deployment imports your app, routers and all dependencies at startup. Warm `.pyc` files shorten start time, which matters for autoscaling and serverless cold starts. The route functions you write are ordinary code objects; FastAPI also inspects their signatures (see `inspect`).

```python
# FastAPI: show why startup is faster with warm .pyc, and expose interpreter info
import sys                                        # interpreter details
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client

app: FastAPI = FastAPI()                          # create app


@app.get("/runtime")                              # GET /runtime
def runtime() -> dict[str, object]:
    return {
        "cache_tag": sys.implementation.cache_tag,   # which .pyc flavour is used
        "dont_write_bytecode": sys.dont_write_bytecode,   # PYTHONDONTWRITEBYTECODE state
    }


client: TestClient = TestClient(app)              # test client
print(client.get("/runtime").json())              # {'cache_tag': 'cpython-313', ...}

# Output:
# {'cache_tag': 'cpython-313', 'dont_write_bytecode': False}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Committing `__pycache__` to git
✅ Correct: add `__pycache__/` and `*.pyc` to `.gitignore`; `.pyc` files are tied to one Python version

❌ Mistake 2: Thinking the main script gets a `.pyc`
✅ Correct: only imported modules are cached; the script you run is compiled in memory every time

```python
# Wrong belief: "python app.py" creates app.cpython-313.pyc
# Right: put the heavy logic in importable modules, keep app.py tiny
```

❌ Mistake 3: Parsing the bytecode bytes by hand in real code
✅ Correct: use `dis`, `types.CodeType` helpers; the format changes in every release (3.11, 3.12 and 3.13 differ)

❌ Mistake 4: Setting `PYTHONDONTWRITEBYTECODE=1` and wondering why startup is slow
✅ Correct: it avoids writing `.pyc`, useful for read-only images, but you lose the cache unless you precompile during build

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def f(): return 2**10
print(f.__code__.co_consts)
c = compile("a=1\nb=a+1", "s", "exec")
print(c.co_names, c.co_consts)
def g():
    x = 5
    return x
print(g.__code__.co_varnames, g.__code__.co_names)
```
Answer (verified on 3.13):
```
(None, 1024)
('a', 'b') (1, None)
('x',) ()
```
`2**10` is folded to `1024` at compile time. At module level, `a` and `b` are global names, so they live in `co_names`; `1` and the final `None` are constants. Inside a function, `x` is a local variable and lives in `co_varnames`, so `co_names` is empty. `None` appears in the constants of `f` because a function without a docstring keeps `None` at position 0 (this layout can vary by version).

---

## ⚫ Interview Questions + Answers

Q1: Is Python interpreted or compiled?
A1: Both. CPython compiles source to bytecode, then the virtual machine interprets the bytecode. There is no separate "compile" step for you to run.

Q2: Where are `.pyc` files stored and how does Python know they are fresh?
A2: In `__pycache__/`, named like `mod.cpython-313.pyc`. The header holds a magic number for the Python version and either the source modification time and size or a hash. If it does not match, the file is recompiled.

Q3: Does a `.pyc` make my code run faster?
A3: No. It only speeds up loading (skips parsing and compiling). Execution speed is the same.

Q4: Is bytecode portable across Python versions?
A4: No. The magic number changes between versions, and the instruction set changes (for example 3.11 added specialising adaptive instructions). It is portable across operating systems for the same version.

Q5: What is a code object?
A5: An immutable object (`types.CodeType`) holding bytecode plus metadata: constants, names, local variable names, line table, flags. Every function has one at `fn.__code__`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Optimising container start time (`compileall`, keep `__pycache__`)
- Debugging how Python optimises your code
- Understanding errors like "bad magic number"

❌ Avoid when:
- Trying to hide source code by shipping only `.pyc` (easily decompiled)
- Writing tools that depend on exact opcodes (changes every version)
- Looking for big speed-ups (use better algorithms, NumPy, async I/O)

---

## 📊 Visual Diagram
```
 app/models.py ──tokenize/parse──► AST ──compile──► code object ──marshal──► __pycache__/models.cpython-313.pyc
                                                       │                          │
                                                       ▼                          ▼ (next import, header OK)
                                                PVM executes bytecode  ◄───────── load, skip parsing

 .pyc layout:  [magic 4B][flags 4B][mtime 4B][size 4B][marshal(code object)...]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bytecode | Low-level instructions for the PVM | PVM के लिए निचले स्तर के instructions |
| Code object | Holds bytecode and metadata | bytecode और metadata रखने वाला object |
| `.pyc` | Cached compiled module | cache किया compiled module |
| Magic number | Identifies Python version in `.pyc` | `.pyc` में Python version की पहचान |
| Constant folding | Computing constants at compile time | compile के समय constants निकालना |
| PVM | Python virtual machine | bytecode चलाने वाली मशीन |

---

## ⚡ 3-Line Summary
English: Python compiles source to bytecode inside code objects, then the PVM runs it. Imported modules are cached as `.pyc` files for faster loading. Bytecode depends on the Python version.
Hindi: Python source को code objects में bytecode बनाता है, फिर PVM उसे चलाती है। Import हुए modules तेज़ loading के लिए `.pyc` में cache होते हैं। Bytecode Python version पर निर्भर है।

---

## ➡️ Next Topic
**165. dis Module** — read bytecode instructions yourself and compare how two code styles compile.
