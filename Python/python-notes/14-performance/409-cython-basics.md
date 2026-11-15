---

# 409. Cython Basics
# हिंदी में: Cython की बुनियादी बातें (Python को C में compile करना)

---

## 🔵 Simple Definition (English)
Cython turns Python-like code into C code and compiles it into a native extension module (`.so`). If you add C types (`cdef int`, `double`) to hot loops, they run at C speed, often 10-100x faster than pure Python, and you still `import` the result like a normal module.

## 🔵 सरल परिभाषा (Hindi)
Cython, Python जैसे code को C code में बदलकर native extension module (`.so`) में compile करता है। Hot loops में C types (`cdef int`, `double`) जोड़ने पर वे C की speed से चलते हैं, अक्सर pure Python से 10-100 गुना तेज़, और आप उसे सामान्य module की तरह `import` करते हैं।

---

## 🔴 Problem it Solves
CPython executes a loop one bytecode at a time and boxes every number as an object. NumPy cannot help when the loop has logic that depends on the previous step (dynamic programming, parsers, custom algorithms). Writing a C extension by hand is painful. Cython gives C speed while you write almost-Python.

## 🔴 यह क्यों बना? (Hindi)
CPython loop को एक-एक bytecode से चलाता है और हर number को object बनाता है। जब loop की logic पिछले step पर निर्भर हो (dynamic programming, parsers, custom algorithms) तो NumPy मदद नहीं करता। हाथ से C extension लिखना कठिन है। Cython में आप लगभग Python लिखते हैं और speed C जैसी मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write code in .pyx (or a .py using cython annotations)
Step 2 → cythonize converts it to a big .c file
Step 3 → A C compiler (clang/gcc/MSVC) builds a .so / .pyd extension
Step 4 → import mymodule loads the native library
Step 5 → Typed variables (cdef int, double) stay raw C values; untyped ones stay Python objects
Note   → Needs a C compiler, and you must rebuild per OS/Python version
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → .pyx (या cython annotations वाली .py) में code लिखें
Step 2 → cythonize उसे बड़ी .c file में बदलता है
Step 3 → C compiler (clang/gcc/MSVC) .so / .pyd extension बनाता है
Step 4 → import mymodule से native library load होती है
Step 5 → Typed variables raw C values रहते हैं; untyped Python objects
नोट   → C compiler चाहिए और हर OS/Python version के लिए दोबारा build करना पड़ता है
```

---

## 🟡 Real World Example
Razorpay risk engine: a custom scoring loop over millions of transactions that depends on running state cannot be vectorized, so the team moves it into a Cython module. Well-known libraries using Cython: pandas, scikit-learn, uvloop and many parsers. A FastAPI service imports the compiled module for its hot function.

## 🟡 Real Example Hindi mein
Razorpay risk engine में लाखों transactions पर running state वाला custom scoring loop vectorize नहीं हो सकता, इसलिए team उसे Cython module में डालती है। Cython इस्तेमाल करने वाली मशहूर libraries: pandas, scikit-learn, uvloop और कई parsers। FastAPI service अपने hot function के लिए compiled module import करती है।

---

## 💻 Code Example — Basic
```python
# Basic Cython: write a .pyx file, compile it, import it, compare speed
import subprocess  # run the build command
import sys  # python path and executable
import tempfile  # throwaway build folder
import timeit  # timer
from pathlib import Path  # file paths

PYX_SOURCE: str = '''
def fib_cy(int n):
    cdef long a = 0, b = 1  # C integers, not Python objects
    cdef int i  # C loop counter
    for i in range(n):  # compiled to a plain C for-loop
        a, b = b, a + b  # no object allocation
    return a
'''  # contents of fibmod.pyx

SETUP_SOURCE: str = '''
from setuptools import setup
from Cython.Build import cythonize
setup(ext_modules=cythonize("fibmod.pyx", language_level=3, quiet=True))
'''  # build script


def fib_py(n: int) -> int:
    a: int = 0  # first value
    b: int = 1  # second value
    for _ in range(n):  # same algorithm in pure Python
        a, b = b, a + b  # tuple swap
    return a  # result


with tempfile.TemporaryDirectory() as tmp:  # build in a temp dir, auto-cleaned
    folder: Path = Path(tmp)  # folder path
    (folder / "fibmod.pyx").write_text(PYX_SOURCE)  # write the .pyx
    (folder / "setup.py").write_text(SETUP_SOURCE)  # write setup.py
    subprocess.run(  # equals: python setup.py build_ext --inplace
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=folder, check=True, capture_output=True,
    )
    sys.path.insert(0, str(folder))  # make the compiled module importable
    import fibmod  # type: ignore  # the compiled extension (.so)

    print(fibmod.fib_cy(50) == fib_py(50))  # same answer
    # Output: True
    print(fibmod.fib_cy(10))  # small check
    # Output: 55
    t_py: float = min(timeit.repeat(lambda: fib_py(80), number=20000, repeat=3))  # python time
    t_cy: float = min(timeit.repeat(lambda: fibmod.fib_cy(80), number=20000, repeat=3))  # cython time
    print("cython faster:", t_cy < t_py)  # compiled C loop wins
    # Output: cython faster: True
    print(fibmod.__file__.endswith((".so", ".pyd")))  # it is a compiled extension
    # Output: True
```

## 💻 Code Example — Advanced
```python
# Advanced Cython: pure-Python mode (works as normal Python AND compiles), memoryview over NumPy
import subprocess  # build command
import sys  # python path
import tempfile  # temp build folder
import timeit  # timer
from pathlib import Path  # paths
from typing import Callable  # type hints

import numpy as np  # arrays passed into Cython

KERNEL: str = '''
import cython  # in plain Python this is a harmless shim


@cython.boundscheck(False)  # skip index bounds checks (we validate ourselves)
@cython.wraparound(False)  # no negative-index support = faster
def dot_loop(a: cython.double[:], b: cython.double[:]) -> cython.double:
    n: cython.Py_ssize_t = a.shape[0]  # length as a C integer
    if b.shape[0] != n:  # validate BEFORE the unchecked loop
        raise ValueError("length mismatch")  # clear error, no memory corruption
    total: cython.double = 0.0  # C double accumulator
    i: cython.Py_ssize_t  # C loop index
    for i in range(n):  # becomes a C for-loop
        total += a[i] * b[i]  # raw memory access
    return total  # converted back to a Python float
'''  # the same file also runs un-compiled as pure Python

SETUP: str = '''
from setuptools import setup
from Cython.Build import cythonize
setup(ext_modules=cythonize("kernel.py", language_level=3, quiet=True))
'''  # compile a .py file


def py_dot(a: np.ndarray, b: np.ndarray) -> float:
    total: float = 0.0  # python accumulator
    for i in range(a.shape[0]):  # python loop
        total += float(a[i]) * float(b[i])  # slow per-element access
    return total  # result


with tempfile.TemporaryDirectory() as tmp:  # build folder
    folder: Path = Path(tmp)  # path
    (folder / "kernel.py").write_text(KERNEL)  # source
    (folder / "setup.py").write_text(SETUP)  # build script
    subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"],
                   cwd=folder, check=True, capture_output=True)  # compile
    sys.path.insert(0, str(folder))  # import path
    import kernel  # type: ignore  # compiled module (the .so wins over kernel.py)

    x: np.ndarray = np.arange(1000, dtype=np.float64)  # 0..999
    y: np.ndarray = np.ones(1000, dtype=np.float64)  # all ones
    print(kernel.dot_loop(x, y))  # sum(0..999)
    # Output: 499500.0
    print(kernel.dot_loop(x, y) == py_dot(x, y) == float(x @ y))  # all methods agree
    # Output: True
    try:  # error handling
        kernel.dot_loop(x, y[:10])  # wrong length
    except ValueError as exc:  # caught
        print("ValueError:", exc)  # message
    # Output: ValueError: length mismatch
    fast: Callable[[], float] = lambda: kernel.dot_loop(x, y)  # compiled call
    slow: Callable[[], float] = lambda: py_dot(x, y)  # python call
    print("compiled faster than python loop:",
          min(timeit.repeat(fast, number=200, repeat=3)) < min(timeit.repeat(slow, number=200, repeat=3)))
    # Output: compiled faster than python loop: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python + Cython: add C types to the hot loop, compile, import
# fibmod.pyx:   def fib_cy(int n): cdef long a = 0, b = 1 ...
import fibmod                      # loads the compiled .so
print(fibmod.fib_cy(10))           # 55
```
```javascript
// JavaScript: V8's JIT compiles hot code automatically; for native speed use WebAssembly or N-API
const wasm = await WebAssembly.instantiate(bytes);   // precompiled from C/Rust
console.log(wasm.instance.exports.fib(10));          // 55
// Node native addon: require('./build/Release/fib.node')
```

Key differences: JavaScript engines JIT-compile hot code for you, so you rarely compile by hand. CPython has no JIT by default (3.13 has an experimental one), so Cython is an explicit ahead-of-time step, similar to using WebAssembly or a Node native addon.

---

## 🟠 FastAPI Connection
Use Cython for CPU-heavy pure functions called by an endpoint (scoring, parsing, custom math). Keep a pure-Python fallback so tests and developer laptops work without a compiler, and validate input ranges, because C integers can overflow without any error.

```python
# FastAPI + a compiled extension with a safe pure-Python fallback (pip install fastapi httpx)
from fastapi import FastAPI, Query  # app + validation
from fastapi.testclient import TestClient  # in-process test client

try:  # use the compiled Cython module if it was built
    from fibmod import fib_cy as fib  # type: ignore  # compiled C version
except ImportError:  # not built (dev laptop, CI without compiler)
    def fib(n: int) -> int:  # same algorithm in pure Python
        a: int = 0  # first value
        b: int = 1  # second value
        for _ in range(n):  # loop n times
            a, b = b, a + b  # advance
        return a  # result

app: FastAPI = FastAPI()  # create app


@app.get("/fib")  # GET /fib?n=10
def get_fib(n: int = Query(10, ge=0, le=90)) -> dict[str, int]:  # le=90 keeps C long from overflowing
    return {"n": n, "fib": fib(n)}  # CPU work done in C when compiled


client: TestClient = TestClient(app)  # test client
print(client.get("/fib", params={"n": 10}).json())  # call it
# Output: {'n': 10, 'fib': 55}
print(client.get("/fib", params={"n": 500}).status_code)  # rejected by validation
# Output: 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Compiling without adding types
```python
# Wrong - same code compiled, but all variables are still Python objects (only modestly faster):
def total(n):
    s = 0
    for i in range(n):
        s += i
    return s

# Correct - declare C types in the hot loop (in .pyx):
# def total(int n):
#     cdef long s = 0
#     cdef int i
#     for i in range(n):
#         s += i
#     return s
```

❌ Mistake 2: Ignoring C integer overflow
```python
# Wrong - cdef long wraps silently (fib(93) gives a negative number):
# cdef long a ...

# Correct - validate the input range (as in the FastAPI example: n <= 90),
# or keep big values as Python int objects.
```

❌ Mistake 3: Optimizing before profiling
```python
# Wrong - rewriting everything in Cython "just in case"

# Correct - profile first (cProfile / py-spy), try NumPy or a better algorithm,
# then move only the 1-2 hot functions to Cython.
```

---

## 🧠 Tricky Interview Question

**Q**: A `.pyx` file defines `def fib_cy(int n)` using `cdef long a, b`, and also `cdef int hidden(int x)`. From Python, what do these print?

```python
import fibmod
print(fibmod.fib_cy(92))
print(fibmod.fib_cy(93))
print(hasattr(fibmod, "hidden"))
```

**Answer**:
```
7540113804746346429
-6246583658587674878
False
```
(Output verified on a 64-bit Mac; on platforms where C `long` is 32-bit, e.g. Windows, overflow starts much earlier.) `fib(93)` exceeds the 64-bit signed range, so the C `long` wraps around silently, unlike a Python `int` which would give `12200160415121876738`. `cdef` functions are pure C functions and are not visible to Python; only `def` and `cpdef` are.

---

## ⚫ Interview Questions + Answers

Q1: What is Cython and how is it different from CPython?
A1: CPython is the standard interpreter. Cython is a compiler that translates Python-like code (with optional C types) to C, building an extension module that CPython imports. They are different things with similar names.

Q2: `def` vs `cdef` vs `cpdef`?
A2: `def` is a normal Python-callable function. `cdef` is a C-only function (fast, not visible from Python). `cpdef` creates both: a fast C entry point and a Python wrapper.

Q3: Why is Cython sometimes not faster?
A3: If variables stay untyped, or the code mostly calls Python functions and objects, the time is spent in the interpreter anyway. Use `cython -a` to produce an HTML report; yellow lines show Python interaction.

Q4: What does `@cython.boundscheck(False)` do?
A4: It removes array index bounds checks for speed. If your index is wrong you get a crash or memory corruption instead of `IndexError`, so validate sizes first.

Q5: Cython vs Numba?
A5: Numba JIT-compiles decorated functions at runtime (no compiler step, great for numeric NumPy code). Cython is ahead-of-time, supports more of the language and C libraries, but needs a build step.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A hot loop has state-dependent logic NumPy cannot vectorize
- You wrap existing C/C++ libraries
- You ship a library and can build wheels per platform

❌ Avoid when:
- NumPy or a better algorithm already solves it
- The bottleneck is IO (use asyncio) or the database
- You cannot control the build environment (no compiler)

---

## 📊 Visual Diagram

```
fibmod.pyx ──cythonize──► fibmod.c ──clang/gcc──► fibmod.cpython-313-*.so
                                                         │
Python:  import fibmod  ◄────────────────────────────────┘
                         calls run as native machine code
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| .pyx | Cython source file | Cython source file |
| cdef | Declare a C variable or C function | C variable/function घोषित करना |
| cpdef | C function with a Python wrapper | Python wrapper वाला C function |
| Extension module | Compiled native module (.so/.pyd) | compile हुआ native module |
| Memoryview | Typed fast view of an array buffer | array buffer का typed view |
| AOT compile | Compile before running | चलाने से पहले compile |

---

## ⚡ 3-Line Summary
English: Cython compiles Python-like code with C types into a native extension, giving 10-100x speedups on hot loops. It needs a compiler and a build step, and C integers can overflow silently. Profile first, then convert only the hot function.
Hindi: Cython, C types वाले Python जैसे code को native extension में compile करता है, hot loops पर 10-100 गुना तेज़। इसे compiler और build step चाहिए, और C integers चुपचाप overflow हो सकते हैं। पहले profile करें, फिर सिर्फ hot function बदलें।

---

## ➡️ Next Topic
**410. Numba Basics** — get similar speedups with just a decorator and no build step.
