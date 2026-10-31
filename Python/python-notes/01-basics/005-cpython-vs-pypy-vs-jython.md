---

# 005. CPython vs PyPy vs Jython
# हिंदी में: CPython बनाम PyPy बनाम Jython

---

## 🔵 Simple Definition (English)
"Python" is a language specification; CPython, PyPy, Jython, IronPython and others are different programs that implement it. CPython (written in C) is the standard one. PyPy uses a JIT compiler for speed. Jython runs on the Java VM. MicroPython runs on tiny chips.

## 🔵 सरल परिभाषा (Hindi)
"Python" एक language specification है; CPython, PyPy, Jython, IronPython उसे implement करने वाले अलग programs हैं। CPython (C में लिखा) standard है। PyPy JIT से तेज़ है। Jython Java VM पर चलता है। MicroPython छोटे chips पर चलता है।

---

## 🔴 Problem it Solves
One implementation cannot be best at everything. CPython is compatible but slowish; some teams need speed, some need to call Java libraries, some need .NET, some need to run on a 256 KB microcontroller. Different implementations exist so the same language can fit different environments.

## 🔴 यह क्यों बना? (Hindi)
एक implementation हर चीज़ में best नहीं हो सकती। CPython compatible पर थोड़ी धीमी है; किसी को speed चाहिए, किसी को Java libraries, किसी को .NET, किसी को microcontroller। इसलिए एक ही language के अलग implementations बने।

---

## 🟢 How it Works — Step by Step

```
CPython     : .py → bytecode → C interpreter loop (default, reference)
PyPy        : .py → bytecode → tracing JIT → machine code for hot loops
Jython      : .py → JVM bytecode → runs on the Java Virtual Machine
IronPython  : .py → .NET IL → runs on the CLR
MicroPython : .py → compact bytecode → tiny interpreter for microcontrollers
```

## 🟢 कैसे काम करता है? (Hindi)
```
CPython     : bytecode -> C का interpreter loop (default)
PyPy        : bytecode -> tracing JIT -> hot loops का machine code
Jython      : JVM bytecode -> Java Virtual Machine पर
IronPython  : .NET IL -> CLR पर
MicroPython : compact bytecode -> microcontroller पर
```

---

## 🟡 Real World Example
Quora ran on PyPy for CPU-heavy backend code; a bank with a large Java estate used Jython to script Java apps (Jython still targets Python 2.7/3.x slowly); Raspberry Pi Pico projects run MicroPython. A FastAPI + NumPy + Pydantic service runs on CPython because those libraries ship CPython-specific compiled wheels.

## 🟡 Real Example Hindi mein
Quora ने CPU-heavy backend के लिए PyPy इस्तेमाल किया; Java-heavy बैंकों ने Java apps को script करने के लिए Jython लिया; Raspberry Pi Pico पर MicroPython चलता है। FastAPI + NumPy + Pydantic वाली service CPython पर चलती है क्योंकि इन libraries के compiled wheels CPython के लिए होते हैं।

---

## 💻 Code Example — Basic
```python
# Find out which implementation and version you are running on

import platform  # implementation info
import sys  # interpreter details

impl: str = platform.python_implementation()  # 'CPython', 'PyPy', ...
print(impl)  # CPython (on a standard install)
print(sys.implementation.name)  # cpython (lowercase)
print(sys.version_info >= (3, 8))  # True: modern Python

is_cpython: bool = impl == "CPython"  # branch on implementation
if is_cpython:  # CPython-only features
    print("reference counting available:", hasattr(sys, "getrefcount"))  # True
else:  # other implementations
    print("different memory model")  # e.g. PyPy has no exact refcounts

x: list[int] = []  # a fresh list
print(sys.getrefcount(x) >= 2)  # True: variable + argument reference
```

## 💻 Code Example — Advanced
```python
# Benchmark helper: run the same CPU-bound function and report timing.
# Run this file with `python3 bench.py` and `pypy3 bench.py` to compare.

import platform  # to print which implementation ran
import time  # timing
from typing import Callable  # type hint


def collatz_steps(limit: int) -> int:  # CPU-bound pure Python work
    best = 0  # longest chain found
    for start in range(1, limit):  # try every start number
        n, steps = start, 0  # working value and counter
        while n != 1:  # until reaching 1
            n = n // 2 if n % 2 == 0 else 3 * n + 1  # collatz rule
            steps += 1  # count the step
        best = max(best, steps)  # keep the longest
    return best  # answer


def bench(fn: Callable[[int], int], arg: int) -> tuple[int, float]:
    t0 = time.perf_counter()  # start clock
    out = fn(arg)  # run function
    return out, time.perf_counter() - t0  # result and seconds


def main() -> None:  # entry point
    result, seconds = bench(collatz_steps, 30_000)  # run benchmark
    print(f"{platform.python_implementation()}: result={result}")  # deterministic
    print("took more than 0 seconds:", seconds > 0)  # True; real time varies


if __name__ == "__main__":  # only as script
    main()  # go
# On PyPy this loop is typically 5-20x faster than CPython; output result is identical.
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: choose an implementation (same code, different interpreter)
# $ python3 app.py   -> CPython
# $ pypy3 app.py     -> PyPy (JIT)
import sys  # access info
print(sys.implementation.name)  # cpython or pypy
```
```javascript
// JavaScript: choose a runtime (same code, different engine)
// $ node app.js   -> V8
// $ bun app.js    -> JavaScriptCore
// $ deno run app.js -> V8
console.log(typeof process !== "undefined" ? process.release.name : "browser");
```
JavaScript has a few engines but V8 dominates and all are JIT-based. Python's default is NOT JIT-based, which is why PyPy can give big speedups.

---

## 🟠 FastAPI Connection
FastAPI, Pydantic v2 (Rust core `pydantic-core`), uvloop, orjson and asyncpg ship compiled extensions built for CPython. PyPy supports some of them slowly or not at all, so production FastAPI deployments use CPython. Speed comes from async I/O and compiled dependencies, not from PyPy.

```python
# FastAPI example (needs: pip install fastapi uvicorn)
import platform  # implementation name

from fastapi import FastAPI  # framework

app = FastAPI()  # application object


@app.get("/runtime")  # route
def runtime() -> dict[str, str]:  # shows what runs the service
    return {"impl": platform.python_implementation(), "version": platform.python_version()}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming PyPy is a drop-in speedup for every project
```python
# Wrong: switching a NumPy/pandas/FastAPI app to PyPy and expecting faster results
# C extensions use the CPython C-API; on PyPy they run through a slow emulation layer.

# Right: profile first. Use PyPy for pure-Python CPU loops; use NumPy/Cython/Rust for data.
```
✅ Correct: measure, then choose.

❌ Mistake 2: Relying on CPython-only behaviour in portable code
```python
import sys
x: object = object()
# Wrong: depending on exact refcount numbers (only meaningful on CPython)
# assert sys.getrefcount(x) == 2
# Right: use weakref / context managers (with) for cleanup, never rely on __del__ timing
with open(__file__) as f:  # file closes deterministically on every implementation
    pass
```
✅ Correct: use `with` blocks instead of relying on immediate garbage collection.

---

## 🧠 Tricky Interview Question

```python
# What will this output on CPython?
import sys

a = []
b = a
print(sys.getrefcount(a) - 1)
del b
print(sys.getrefcount(a) - 1)
```
Answer: `2` then `1`. `getrefcount` itself adds one temporary reference (the argument), so we subtract 1. Before `del`, references are `a` and `b`; after `del b`, only `a`. On PyPy this exact counting does not exist, which is why it is a CPython implementation detail.

---

## ⚫ Interview Questions + Answers

Q1: What is CPython?
A1: The reference implementation of Python, written in C, maintained by the Python core team. It compiles to bytecode and interprets it. When people say "Python" they almost always mean CPython. It has the GIL and supports the C-API used by NumPy, Pydantic and most libraries.

Q2: Why is PyPy faster?
A2: PyPy has a tracing JIT: it watches hot loops, specialises them for the observed types, and compiles them to machine code. Pure-Python numeric loops can be 5-20x faster. It uses more memory and starts slower, and C-extension support is weaker.

Q3: What is Jython and is it used today?
A3: Jython compiles Python to JVM bytecode so Python code can import Java classes. It lags behind (supports Python 2.7, a Python 3 version is still in progress), so modern projects rarely use it. For Java interop today people use REST APIs, gRPC, or GraalPy.

Q4: Does PyPy have a GIL?
A4: Yes, PyPy has a GIL too. Jython and IronPython do not have a GIL because the JVM and CLR handle threads. CPython 3.13 added an experimental free-threaded build (no GIL), still opt-in.

Q5: Which implementation do you use for FastAPI in production?
A5: CPython (usually the latest stable like 3.12 or 3.13) because every dependency supports it. Performance is improved by async I/O, uvicorn workers, and compiled libraries, not by switching implementation.

---

## 🔷 When to Use + When Not to Use

✅ Use PyPy when:
- Long-running pure-Python CPU-bound code (parsers, simulations)
- Few or no C-extension dependencies

✅ Use MicroPython when:
- Microcontrollers (ESP32, Pico)

❌ Avoid PyPy / Jython when:
- NumPy, pandas, PyTorch, Pydantic-core, or modern Python 3 features are needed
- You want the best library compatibility (use CPython)

---

## 📊 Visual Diagram
```
                 Python language spec
                        │
   ┌──────────┬─────────┼───────────┬──────────────┐
   ▼          ▼         ▼           ▼              ▼
 CPython     PyPy     Jython    IronPython    MicroPython
 (C, VM)   (JIT)     (JVM)      (.NET)        (embedded)
 default   fast      Java libs  C# libs        tiny chips
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Implementation | A program that runs Python code | Python code चलाने वाला program |
| JIT | Compile hot code while running | चलते समय hot code compile करना |
| C-API | C interface used by extensions | Extensions के लिए C interface |
| GIL | Lock allowing one thread to run bytecode | एक समय एक thread की lock |
| Wheel | Prebuilt package file | पहले से बना package |
| Free-threaded | Build without the GIL | बिना GIL वाला build |

---

## ⚡ 3-Line Summary
English: Python is a language; CPython, PyPy, Jython and others implement it. CPython is the default and most compatible; PyPy is faster for pure-Python loops; Jython targets Java. Production FastAPI uses CPython.
Hindi: Python language है; CPython, PyPy, Jython उसे implement करते हैं। CPython default और सबसे compatible; PyPy pure-Python loops में तेज़; Jython Java के लिए। Production FastAPI में CPython।

---

## ➡️ Next Topic
**006. Python Versions (2 vs 3)** — why Python 2 died, what changed, and which version to use now.
