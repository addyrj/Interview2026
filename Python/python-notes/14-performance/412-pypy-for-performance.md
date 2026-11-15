---

# 412. PyPy for Performance
# हिंदी में: Performance के लिए PyPy (तेज़ Python interpreter)

---

## 🔵 Simple Definition (English)
PyPy is an alternative Python interpreter with a tracing JIT compiler. It watches hot loops while your pure-Python program runs and compiles them to machine code, so unchanged Python code is often 3-10x faster than CPython (and sometimes much more).

## 🔵 सरल परिभाषा (Hindi)
PyPy एक वैकल्पिक Python interpreter है जिसमें tracing JIT compiler है। यह आपके pure-Python program के चलते समय hot loops को देखता है और उन्हें machine code में compile कर देता है, इसलिए बिना बदले Python code अक्सर CPython से 3-10 गुना तेज़ चलता है (कभी-कभी और ज़्यादा)।

---

## 🔴 Problem it Solves
CPython interprets bytecode one instruction at a time, so long-running pure-Python loops (parsers, simulations, game logic, template engines) are slow. Cython and Numba need code changes. PyPy needs none: you run the same script with `pypy3` instead of `python3`.

## 🔴 यह क्यों बना? (Hindi)
CPython bytecode को एक-एक instruction करके चलाता है, इसलिए लंबे pure-Python loops (parsers, simulation, game logic, template engines) धीमे होते हैं। Cython और Numba में code बदलना पड़ता है। PyPy में कुछ नहीं बदलना: `python3` की जगह `pypy3` से वही script चलाइए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Program starts in PyPy's interpreter (initially about as slow as CPython)
Step 2 → The JIT counts how often loops and functions run
Step 3 → Hot loops (roughly thousands of iterations) are "traced" and recorded
Step 4 → The trace is optimized (types guessed, objects unboxed) and compiled to machine code
Step 5 → Guards check the assumptions; if one fails it falls back to the interpreter
Step 6 → Long-running programs get fast ("warm-up"); short scripts may not benefit
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Program PyPy के interpreter में शुरू होता है (शुरू में लगभग CPython जितना धीमा)
Step 2 → JIT गिनता है कि loops और functions कितनी बार चले
Step 3 → Hot loops (लगभग हज़ारों iterations) "trace" होकर record होते हैं
Step 4 → Trace optimize होकर machine code में compile होती है
Step 5 → Guards assumptions जाँचते हैं; गलत निकलें तो interpreter पर लौट आता है
Step 6 → लंबे चलने वाले programs तेज़ होते हैं ("warm-up"); छोटी scripts को फायदा कम
```

---

## 🟡 Real World Example
A pure-Python log-processing worker at a Swiggy-like company parses billions of text lines with plain loops and dicts and runs for hours: switching its Docker image to `pypy:3.10` gives a large speed-up with no code change. In contrast, an AI/NumPy/pandas service stays on CPython because those libraries are built for CPython's C API.

## 🟡 Real Example Hindi mein
Swiggy जैसी कंपनी का pure-Python log-processing worker अरबों text lines को plain loops और dicts से parse करता है और घंटों चलता है: उसकी Docker image को `pypy:3.10` पर बदलने से code बदले बिना बड़ा speed-up मिलता है। इसके उलट AI/NumPy/pandas service CPython पर ही रहती है क्योंकि वे libraries CPython के C API के लिए बनी हैं।

---

## 💻 Code Example — Basic
```python
# Basic: the same pure-Python file runs on CPython and PyPy - only the interpreter changes
import platform  # which interpreter is this?
import sys  # implementation info
import time  # timer


def collatz_steps(n: int) -> int:
    steps: int = 0  # how many moves so far
    while n != 1:  # until we reach 1
        n = n // 2 if n % 2 == 0 else 3 * n + 1  # even: halve, odd: 3n+1
        steps += 1  # count the move
    return steps  # total moves


def longest_chain(limit: int) -> int:
    best_n: int = 1  # number with the longest chain
    best_len: int = 0  # its length
    for n in range(1, limit):  # try every start value
        length: int = collatz_steps(n)  # steps for this start
        if length > best_len:  # new record
            best_n, best_len = n, length  # remember it
    return best_n  # answer


print(platform.python_implementation())  # "CPython" here, "PyPy" under pypy3
# Output: CPython
print(sys.implementation.name)  # lower-case implementation name
# Output: cpython
print(collatz_steps(27))  # famous example: 111 steps
# Output: 111

start: float = time.perf_counter()  # start the clock
winner: int = longest_chain(100_000)  # tight pure-Python loops: PyPy's best case
elapsed: float = time.perf_counter() - start  # seconds taken
print(winner)  # start value below 100000 with the longest chain
# Output: 77031
print(f"took {elapsed:.2f}s on {platform.python_implementation()}")  # varies by machine
# Output: took 0.74s on CPython 3.13 (on the author's Mac; varies by machine)
# PyPy is typically several times faster on this kind of loop - NOT measured here, run it yourself
```

## 💻 Code Example — Advanced
```python
# Advanced: benchmark with warm-up (needed for any JIT), and write interpreter-aware code
import platform  # implementation name
import statistics  # median of runs
import time  # timer
from typing import Callable, List, Optional


def is_pypy() -> bool:
    return platform.python_implementation() == "PyPy"  # True only under PyPy


def bench(func: Callable[[], object], warmup: int = 3, runs: int = 5) -> float:
    """Median seconds per call, after warm-up so a JIT has time to compile."""
    for _ in range(warmup):  # JIT interpreters get faster after many calls
        func()  # discard these timings
    times: List[float] = []  # measured runs
    for _ in range(runs):  # real measurements
        t0: float = time.perf_counter()  # start
        func()  # run the workload
        times.append(time.perf_counter() - t0)  # store elapsed time
    return statistics.median(times)  # robust against one slow outlier


def word_freq(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}  # word -> count
    for word in text.split():  # pure Python loop over words
        counts[word] = counts.get(word, 0) + 1  # update the counter
    return counts  # result


TEXT: str = ("zomato swiggy razorpay fastapi " * 50_000).strip()  # 200k words

print(len(word_freq(TEXT)))  # four distinct words
# Output: 4
print(word_freq("a b a")["a"])  # simple correctness check
# Output: 2

median: float = bench(lambda: word_freq(TEXT))  # seconds per call
print("median per call is positive:", median > 0)  # sanity check
# Output: median per call is positive: True

# Interpreter-aware choice: C-extension heavy stacks (numpy, pandas, many wheels) work best on CPython
backend: Optional[str] = "pure-python path" if is_pypy() else "cpython path (C extensions ok)"
print(backend)  # which branch we are on
# Output: cpython path (C extensions ok)
# Under PyPy this prints: pure-python path   (not run here: PyPy is not installed)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: choose the interpreter, not the code
#   python3 app.py     -> CPython (bytecode interpreter, no JIT by default)
#   pypy3   app.py     -> PyPy (tracing JIT, same code)
import platform
print(platform.python_implementation())
```
```javascript
// JavaScript: the JIT is built in - V8 (Node/Chrome) compiles hot functions automatically
//   node app.js        -> V8 JIT (TurboFan)
console.log(process.versions.v8);
```

Key differences: JavaScript developers get a JIT by default (V8). In Python you must choose PyPy to get one (CPython 3.13 only has an experimental, off-by-default JIT). So PyPy is the closest thing to "Node-like" speed for pure-Python code.

---

## 🟠 FastAPI Connection
FastAPI depends on `pydantic-core` (a Rust extension) and often on other C extensions, so it is usually deployed on CPython. PyPy fits best for pure-Python workers (queue consumers, parsers) that do not use NumPy or pydantic v2. Always test your dependency set on PyPy before deploying, and keep the interpreter name visible in a health endpoint.

```python
# FastAPI note: run the SAME app file under CPython or PyPy (pip install fastapi httpx)
import platform  # interpreter name
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # create app


@app.get("/runtime")  # GET /runtime
def runtime() -> dict[str, str]:
    return {"impl": platform.python_implementation(), "version": platform.python_version()[:4]}  # info


print(TestClient(app).get("/runtime").json())  # call it
# Output: {'impl': 'CPython', 'version': '3.13'}
# Deploying on PyPy would be:  pypy3 -m uvicorn main:app   (pydantic-core is a Rust extension, so
# check compatibility first - many FastAPI stacks do not run on PyPy. Not run here.)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Benchmarking a short script
```python
# Wrong - a 0.2 second script never leaves the warm-up phase:
#   time pypy3 tiny.py   ->   looks no faster than CPython

# Correct - benchmark long-running work with warm-up runs (see bench() above)
```

❌ Mistake 2: Using C-extension-heavy libraries on PyPy
```python
# Wrong - numpy/pandas/pydantic-core via the emulation layer (cpyext) can be slow or fail:
#   pypy3 -m pip install pandas

# Correct - keep numeric/data stacks on CPython; use PyPy for pure-Python hot paths
```

❌ Mistake 3: Relying on CPython-only behaviour (reference counting)
```python
# Wrong - assuming __del__ or file closing happens immediately:
f = open("data.txt"); data = f.read()     # file closed "when f is collected" - not guaranteed on PyPy

# Correct - always use context managers:
with open("data.txt") as f:
    data = f.read()
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print on CPython? Which lines could differ on PyPy?

```python
import sys

class A:
    def __del__(self):
        print("del")

A()
print("after")
print(hasattr(sys, "getrefcount"))
```

**Answer**:
```
del
after
True
```
On CPython the object is destroyed immediately (reference count drops to zero), so `del` prints first. PyPy uses a tracing garbage collector, so `__del__` may run later (or at exit), changing the order, and `sys.getrefcount` does not exist there. The lesson: never depend on timing of destructors; use `with` blocks. (CPython output verified; the PyPy behaviour is from its documented semantics and was not run here.)

---

## ⚫ Interview Questions + Answers

Q1: Why is PyPy faster than CPython?
A1: A tracing JIT compiles hot loops to machine code, unboxes integers and floats, and removes interpreter dispatch overhead. CPython interprets bytecode (3.13 has only an experimental JIT).

Q2: When is PyPy slower or not helpful?
A2: For short scripts (warm-up cost), for code dominated by C-extension calls (NumPy, pandas), and for I/O-bound programs where the interpreter is not the bottleneck.

Q3: Does PyPy have a GIL?
A3: Yes. PyPy has a GIL too, so it does not give multi-core threading. Use multiprocessing for CPU parallelism there as well.

Q4: PyPy vs Numba vs Cython?
A4: PyPy: zero code changes, general pure-Python code, but poor C-extension compatibility. Numba: numeric NumPy loops, decorator. Cython: ahead-of-time, typed code, full C-library access.

Q5: How do you migrate a project to PyPy safely?
A5: Run the full test suite under PyPy in CI, check every dependency (especially C extensions), benchmark with warm-up on realistic data, and watch memory (PyPy can use more or less depending on the workload).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Long-running, pure-Python, CPU-bound code (parsers, simulators, algorithms)
- You cannot or do not want to change the code
- All dependencies are pure Python or PyPy-compatible

❌ Avoid when:
- You rely on NumPy, pandas, pydantic v2, TensorFlow, PyTorch
- The program is short-lived or I/O-bound
- You need the newest CPython-only features immediately

---

## 📊 Visual Diagram

```
CPython:  source -> bytecode -> interpreter loop (one instruction at a time)  -> slow loops

PyPy:     source -> bytecode -> interpreter
                                  │ hot loop detected (counter)
                                  ▼
                         trace + optimize -> MACHINE CODE  ──► fast loops
                                  ▲             │
                                  └── guard fails: fall back
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JIT | Compile while the program runs | चलते समय compile |
| Tracing | Recording a hot path to compile it | hot path को record करके compile करना |
| Warm-up | Slow start before the JIT kicks in | JIT शुरू होने से पहले की धीमी शुरुआत |
| Guard | Runtime check of a JIT assumption | JIT की मान्यता की runtime जाँच |
| cpyext | PyPy layer emulating the CPython C API | PyPy में CPython C API की नक़ल |
| Interpreter | Program that runs Python code | Python code चलाने वाला program |

---

## ⚡ 3-Line Summary
English: PyPy is a Python interpreter with a tracing JIT that speeds up long-running pure-Python code, often 3-10x, with no code changes. It struggles with C-extension-heavy stacks like NumPy or pydantic v2 and needs warm-up. Test dependencies and benchmark properly before switching.
Hindi: PyPy tracing JIT वाला Python interpreter है जो लंबे चलने वाले pure-Python code को बिना बदलाव अक्सर 3-10 गुना तेज़ करता है। NumPy या pydantic v2 जैसे C-extension वाले stacks में दिक्कत होती है और warm-up चाहिए। बदलने से पहले dependencies test और ठीक से benchmark करें।

---

## ➡️ Next Topic
**413. Multiprocessing for CPU Tasks** — use all CPU cores with separate processes to get past the GIL.
