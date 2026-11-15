---

# 411. C Extensions Basics
# हिंदी में: C Extensions की बुनियादी बातें (Python से C code चलाना)

---

## 🔵 Simple Definition (English)
A C extension is a compiled native library (`.so`, `.dylib`, `.pyd`) that Python can call. You can reach C code in two main ways: `ctypes` (load any shared library, no compiler step on the Python side) or the CPython C API (write a real module with `#include <Python.h>`).

## 🔵 सरल परिभाषा (Hindi)
C extension एक compiled native library (`.so`, `.dylib`, `.pyd`) है जिसे Python call कर सकता है। C code तक पहुँचने के दो मुख्य रास्ते हैं: `ctypes` (कोई भी shared library load करें) या CPython C API (`#include <Python.h>` के साथ असली module लिखें)।

---

## 🔴 Problem it Solves
Python is slow for tight CPU loops, and a lot of useful software already exists in C (OpenSSL, zlib, SQLite, image libraries). C extensions let Python reuse those libraries and let you write the one hot function in C while everything else stays Python. That is exactly how NumPy, pydantic-core, orjson and `hashlib` work.

## 🔴 यह क्यों बना? (Hindi)
Python tight CPU loops में धीमा है, और बहुत सारा उपयोगी software पहले से C में है (OpenSSL, zlib, SQLite, image libraries)। C extensions से Python उन libraries को दोबारा इस्तेमाल कर सकता है और आप सिर्फ hot function C में लिख सकते हैं, बाकी Python में। NumPy, pydantic-core, orjson और `hashlib` ऐसे ही काम करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write C code (a plain function, or a module using the Python C API)
Step 2 → Compile it into a shared library (cc -shared -fPIC, or setuptools Extension)
Step 3 → Python loads it: ctypes.CDLL("lib.so") or a normal "import module"
Step 4 → Arguments are converted Python object -> C type (declare argtypes/restype!)
Step 5 → The C function runs at native speed without the interpreter
Step 6 → The result is converted back to a Python object
Note   → The GIL is held during a C-API call unless the C code releases it;
         ctypes releases the GIL while the foreign function runs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → C code लिखें (सादा function या Python C API वाला module)
Step 2 → Shared library में compile करें (cc -shared -fPIC या setuptools Extension)
Step 3 → Python load करता है: ctypes.CDLL("lib.so") या सामान्य "import module"
Step 4 → Arguments Python object से C type में बदलते हैं (argtypes/restype घोषित करें!)
Step 5 → C function बिना interpreter के native speed से चलता है
Step 6 → Result वापस Python object बनता है
नोट   → C-API call में GIL तब तक रहता है जब तक C code उसे छोड़े नहीं; ctypes foreign function के दौरान GIL छोड़ देता है
```

---

## 🟡 Real World Example
Paytm needs a custom checksum for a banking file format that only a legacy C library provides: they load it with `ctypes`. An AI inference service wraps a C++ tokenizer. `orjson` (a fast JSON library used with FastAPI) and `pydantic-core` are compiled extensions (Rust and C), which is why FastAPI is fast.

## 🟡 Real Example Hindi mein
Paytm को banking file format के लिए custom checksum चाहिए जो सिर्फ एक पुरानी C library देती है: वे उसे `ctypes` से load करते हैं। AI inference service C++ tokenizer को wrap करती है। `orjson` (FastAPI के साथ इस्तेमाल होने वाली तेज़ JSON library) और `pydantic-core` compiled extensions हैं (Rust और C), इसीलिए FastAPI तेज़ है।

---

## 💻 Code Example — Basic
```python
# Basic: call C from Python with ctypes (standard library, no install)
import ctypes  # foreign function interface
import ctypes.util  # find system libraries
import subprocess  # run the C compiler
import sys  # platform check
import tempfile  # throwaway folder
import timeit  # timer
from pathlib import Path  # paths

# 1) Call a function from the system C library (no compiler needed)
libc = ctypes.CDLL(ctypes.util.find_library("c"))  # load libc
libc.abs.argtypes = [ctypes.c_int]  # declare the argument type
libc.abs.restype = ctypes.c_int  # declare the return type
print(libc.abs(-42))  # C abs() called from Python
# Output: 42

# 2) Compile our own tiny C library and call it
C_SOURCE: str = """
long sum_to(long n) {            /* sum of 0..n-1 */
    long total = 0;              /* C integer accumulator */
    for (long i = 0; i < n; i++) total += i;   /* plain C loop */
    return total;                /* return to Python */
}
"""  # C code as a string
ext: str = ".dylib" if sys.platform == "darwin" else ".so"  # shared library suffix

with tempfile.TemporaryDirectory() as tmp:  # build folder
    src: Path = Path(tmp) / "fast.c"  # C file
    lib_path: Path = Path(tmp) / f"libfast{ext}"  # output library
    src.write_text(C_SOURCE)  # write the C code
    subprocess.run(["cc", "-O2", "-shared", "-fPIC", str(src), "-o", str(lib_path)], check=True)  # compile
    lib = ctypes.CDLL(str(lib_path))  # load the shared library
    lib.sum_to.argtypes = [ctypes.c_long]  # input type
    lib.sum_to.restype = ctypes.c_long  # output type

    def py_sum_to(n: int) -> int:
        total: int = 0  # python accumulator
        for i in range(n):  # python loop
            total += i  # add
        return total  # result

    print(lib.sum_to(1000) == py_sum_to(1000))  # same answer
    # Output: True
    print(lib.sum_to(1000))  # sum of 0..999
    # Output: 499500
    t_py: float = min(timeit.repeat(lambda: py_sum_to(1_000_000), number=3, repeat=3))  # python
    t_c: float = min(timeit.repeat(lambda: lib.sum_to(1_000_000), number=3, repeat=3))  # C
    print("C faster:", t_c < t_py)  # normally 100x+
    # Output: C faster: True
```

## 💻 Code Example — Advanced
```python
# Advanced: a real CPython C-API extension module, built with setuptools
import subprocess  # build command
import sys  # python path
import tempfile  # build folder
from pathlib import Path  # paths
from typing import Any  # type hints

C_MODULE: str = r'''
#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* fastmath.sum_squares(n) -> sum of i*i for i in [0, n) */
static PyObject *sum_squares(PyObject *self, PyObject *args) {
    long n;                                      /* C variable for the argument */
    if (!PyArg_ParseTuple(args, "l", &n))        /* parse Python int -> C long */
        return NULL;                             /* NULL = exception already set */
    if (n < 0) {                                 /* validate the input */
        PyErr_SetString(PyExc_ValueError, "n must be >= 0");
        return NULL;                             /* raises ValueError in Python */
    }
    unsigned long long total = 0;                /* wide accumulator */
    for (long i = 0; i < n; i++) total += (unsigned long long)i * i;   /* C loop */
    return PyLong_FromUnsignedLongLong(total);   /* C value -> Python int */
}

static PyMethodDef methods[] = {                 /* table of exported functions */
    {"sum_squares", sum_squares, METH_VARARGS, "Sum of squares below n."},
    {NULL, NULL, 0, NULL}                        /* sentinel */
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "fastmath", NULL, -1, methods};

PyMODINIT_FUNC PyInit_fastmath(void) { return PyModule_Create(&module); }   /* import hook */
'''  # the whole extension

SETUP: str = '''
from setuptools import setup, Extension
setup(name="fastmath", ext_modules=[Extension("fastmath", ["fastmath.c"])])
'''  # build script

with tempfile.TemporaryDirectory() as tmp:  # build in a temp dir
    folder: Path = Path(tmp)  # path
    (folder / "fastmath.c").write_text(C_MODULE)  # C source
    (folder / "setup.py").write_text(SETUP)  # setup script
    subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"],
                   cwd=folder, check=True, capture_output=True)  # compile to fastmath*.so
    sys.path.insert(0, str(folder))  # make it importable
    import fastmath  # type: ignore  # our compiled C module

    result: Any = fastmath.sum_squares(10)  # 0+1+4+...+81
    print(result)  # check value
    # Output: 285
    print(fastmath.sum_squares(10) == sum(i * i for i in range(10)))  # compare with Python
    # Output: True
    print(type(fastmath.sum_squares(10)).__name__)  # returns a normal Python int
    # Output: int
    try:  # error handling from C
        fastmath.sum_squares(-1)  # triggers PyErr_SetString
    except ValueError as exc:  # becomes a normal Python exception
        print("ValueError:", exc)  # message
    # Output: ValueError: n must be >= 0
    try:  # wrong argument type
        fastmath.sum_squares("x")  # PyArg_ParseTuple rejects it
    except TypeError as exc:  # TypeError raised by the C API
        print("TypeError raised:", True)  # we only show that it was raised
    # Output: TypeError raised: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: ctypes (no wrapper code) or a C-API module
import ctypes
lib = ctypes.CDLL("./libfast.so")
lib.sum_to.argtypes = [ctypes.c_long]
lib.sum_to.restype = ctypes.c_long
print(lib.sum_to(1000))
```
```javascript
// Node.js: native addon (N-API) or WebAssembly
const addon = require('./build/Release/fast.node');   // compiled with node-gyp
console.log(addon.sumTo(1000));
// or: const { instance } = await WebAssembly.instantiate(wasmBytes);
```

Key differences: Python's `ctypes` needs no wrapper code, only a shared library, while Node needs an N-API addon or WebAssembly. Both are an explicit native boundary where type conversion and memory safety are your responsibility.

---

## 🟠 FastAPI Connection
A FastAPI app already runs on C/Rust extensions: `uvloop`, `httptools`, `pydantic-core`, `orjson`, `zlib`, `hashlib`. For your own hot function, expose it via ctypes/Cython/pybind11, keep input validation in Pydantic (so C code never sees bad sizes), and call it from a plain `def` endpoint so it runs in the threadpool.

```python
# FastAPI: most "fast Python" you already use is C extensions (zlib, hashlib, orjson, pydantic-core)
import hashlib  # C implementation of SHA/MD5 (OpenSSL)
import zlib  # C implementation of crc32/compression
from fastapi import FastAPI, Body  # app + body parsing
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # create app


@app.post("/fingerprint")  # POST /fingerprint
def fingerprint(payload: str = Body(..., media_type="text/plain")) -> dict[str, str | int]:
    data: bytes = payload.encode()  # text -> bytes
    return {  # both calls below run in compiled C code
        "crc32": zlib.crc32(data),  # checksum
        "sha256": hashlib.sha256(data).hexdigest(),  # secure hash
    }


client: TestClient = TestClient(app)  # test client
res: dict = client.post("/fingerprint", content="hello", headers={"content-type": "text/plain"}).json()  # call
print(res["crc32"], res["sha256"][:16])  # known values for "hello"
# Output: 907060870 2cf24dba5fb0a30e
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not declaring `argtypes` / `restype` in ctypes
```python
# Wrong - default conversion assumes int, so big values are truncated or crash:
libc.abs(2**40)          # returns 0 on 64-bit macOS/Linux

# Correct - declare the types:
libc.labs.argtypes = [ctypes.c_long]
libc.labs.restype = ctypes.c_long
```

❌ Mistake 2: Not checking inputs before passing them to C
```python
# Wrong - negative or huge sizes passed to C can corrupt memory or crash the whole process:
lib.process(buffer, n)

# Correct - validate in Python (Pydantic / asserts), then call C
if not (0 <= n <= len(buffer)):
    raise ValueError("bad size")
```

❌ Mistake 3: Reference-count and exception errors in the C API
```python
# Wrong (in C): returning a value without setting an exception on failure, or leaking
# references (forgetting Py_DECREF).

# Correct: on failure always PyErr_SetString(...) and return NULL;
# prefer Cython, pybind11 or PyO3 (Rust), which handle this for you.
```

---

## 🧠 Tricky Interview Question

**Q**: On 64-bit macOS/Linux, what does this print?

```python
import ctypes, ctypes.util
libc = ctypes.CDLL(ctypes.util.find_library("c"))
print(libc.abs(-42))
print(libc.abs(2**40))
print(ctypes.sizeof(ctypes.c_int), ctypes.sizeof(ctypes.c_long))
```

**Answer**:
```
42
0
4 8
```
Without `argtypes`, ctypes passes a Python int as a C `int` (32 bits), so `2**40` is truncated to 0 before `abs` runs. `c_long` is 8 bytes on 64-bit macOS/Linux but 4 bytes on Windows, so use fixed-width types such as `c_int64` when the size matters.

---

## ⚫ Interview Questions + Answers

Q1: `ctypes` vs C API vs Cython: when to use which?
A1: `ctypes` for calling an existing shared library quickly with no build step. The C API for full control (new types, GIL handling) at the cost of boilerplate and refcount bugs. Cython/pybind11/PyO3 for writing new fast code with far less boilerplate.

Q2: What happens to the GIL when calling a C function?
A2: With `ctypes`, the GIL is released during the foreign call, so threads can run in parallel. With the C API, the GIL is held unless your C code uses `Py_BEGIN_ALLOW_THREADS`. Note that free-threaded 3.13 builds change this model.

Q3: What is the stable ABI (`abi3`)?
A3: A restricted subset of the C API (`Py_LIMITED_API`) that lets one compiled wheel work across multiple Python versions, so you do not rebuild for each 3.x release.

Q4: What is a wheel and why do extensions need one?
A4: A prebuilt package (`.whl`). Compiled extensions are platform- and version-specific, so projects publish wheels per OS/architecture to spare users from needing a compiler.

Q5: Biggest risks of C extensions?
A5: Memory bugs (segfaults, leaks, wrong refcounts), platform-specific builds, and harder debugging. A crash in C kills the whole Python process; it is not a catchable exception.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You must reuse an existing C/C++ library
- A single hot function needs native speed and Numba/Cython do not fit
- You are building a reusable library with wheels

❌ Avoid when:
- NumPy, a better algorithm or `functools.lru_cache` is enough
- Your team cannot maintain C code and cross-platform builds
- The bottleneck is I/O or the database

---

## 📊 Visual Diagram

```
Python code                      Native world
-----------                      ------------
lib.sum_to(1000)  ─ ctypes ───►  libfast.dylib : sum_to()
import fastmath   ─ C API  ───►  fastmath.so   : PyInit_fastmath()
     ▲                                   │
     └──── Python int / exception ◄──────┘   (convert types, check errors)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ctypes | Stdlib module to call shared libraries | shared libraries call करने वाला stdlib module |
| C API | Python.h functions for writing modules | modules लिखने के लिए Python.h functions |
| Shared library | Compiled .so/.dylib/.dll | compiled साझा library |
| Wheel | Prebuilt installable package | पहले से बना installable package |
| Refcount | Python's object reference counter | object का reference counter |
| GIL | Lock allowing one thread to run Python bytecode | एक समय में एक thread की lock |

---

## ⚡ 3-Line Summary
English: C extensions are compiled libraries Python can call, either via `ctypes` or the CPython C API. They give native speed and access to C libraries, but need careful types, validation and per-platform builds. Prefer Cython, pybind11 or PyO3 for new code.
Hindi: C extensions compiled libraries हैं जिन्हें Python `ctypes` या CPython C API से call करता है। ये native speed और C libraries तक पहुँच देते हैं, पर types, validation और platform-wise build का ध्यान चाहिए। नए code के लिए Cython, pybind11 या PyO3 बेहतर हैं।

---

## ➡️ Next Topic
**412. PyPy for Performance** — a different interpreter with a JIT that speeds up pure-Python code without any C.
