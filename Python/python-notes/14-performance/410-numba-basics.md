---

# 410. Numba Basics
# हिंदी में: Numba की बुनियादी बातें (JIT compile सिर्फ एक decorator से)

---

## 🔵 Simple Definition (English)
Numba is a just-in-time (JIT) compiler. You put `@njit` on a numeric Python function and, on its first call, Numba compiles it to machine code with LLVM. Later calls run at near-C speed. No separate build step and no C code are needed.

## 🔵 सरल परिभाषा (Hindi)
Numba एक just-in-time (JIT) compiler है। Numeric Python function पर `@njit` लगाइए, पहली call पर Numba उसे LLVM से machine code में compile कर देता है। बाद की calls लगभग C की speed से चलती हैं। अलग build step या C code नहीं चाहिए।

---

## 🔴 Problem it Solves
Some numeric loops (simulations, prime checks, rolling statistics, custom distance functions) cannot be written as NumPy one-liners, and pure Python is 50-200x slower than C for them. Cython fixes this but needs a compiler and a build. Numba gives the speed with one decorator and works directly with NumPy arrays.

## 🔴 यह क्यों बना? (Hindi)
कुछ numeric loops (simulation, prime check, rolling statistics, custom distance function) NumPy की एक line में नहीं लिखे जा सकते, और pure Python उनमें C से 50-200 गुना धीमा है। Cython इसे ठीक करता है पर compiler और build चाहिए। Numba एक decorator से वही speed देता है और NumPy arrays के साथ सीधे चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @njit marks the function (nopython mode, no Python objects inside)
Step 2 → First call: Numba inspects argument types (int64, float64[:] ...)
Step 3 → It translates the bytecode to LLVM IR and compiles machine code for those types
Step 4 → The compiled version is cached in memory (cache=True also saves it on disk)
Step 5 → Later calls with the same types run the machine code directly
Step 6 → A new argument type triggers a new compilation (a new "signature")
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @njit function को mark करता है (nopython mode, अंदर Python objects नहीं)
Step 2 → पहली call पर Numba arguments के types देखता है (int64, float64[:] ...)
Step 3 → Bytecode को LLVM IR में बदलकर उन types के लिए machine code बनाता है
Step 4 → Compiled version memory में रहता है (cache=True से disk पर भी)
Step 5 → उसी type की अगली calls सीधे machine code चलाती हैं
Step 6 → नया argument type आने पर नया compile होता है (नया "signature")
```

---

## 🟡 Real World Example
A Zerodha-style trading analytics service computes maximum drawdown and rolling risk over millions of price ticks with a custom loop; `@njit` makes it run in milliseconds. A data science team simulates 10 million Monte Carlo paths. A FastAPI service warms up the compiled functions at startup.

## 🟡 Real Example Hindi mein
Zerodha जैसी trading analytics service लाखों price ticks पर custom loop से maximum drawdown और rolling risk निकालती है; `@njit` से यह milliseconds में चलता है। Data science team 1 करोड़ Monte Carlo paths simulate करती है। FastAPI service startup पर compiled functions को warm-up कर लेती है।

---

## 💻 Code Example — Basic
```python
# Basic Numba (pip install numba numpy): add @njit and the loop is compiled to machine code
import timeit  # timer
import time  # one-off timing of the first call

from numba import njit  # the JIT decorator


def count_primes_py(limit: int) -> int:
    count: int = 0  # primes found
    for n in range(2, limit):  # test every number
        is_prime: bool = True  # assume prime
        d: int = 2  # first divisor
        while d * d <= n:  # only check up to sqrt(n)
            if n % d == 0:  # divisible -> not prime
                is_prime = False  # mark
                break  # stop early
            d += 1  # next divisor
        if is_prime:  # survived all checks
            count += 1  # count it
    return count  # total


count_primes_nb = njit(count_primes_py)  # same function, compiled (decorator form: @njit)

start: float = time.perf_counter()  # time the first call
first: int = count_primes_nb(10)  # first call COMPILES the function (slow)
compile_time: float = time.perf_counter() - start  # includes compile time
print(first)  # primes below 10: 2, 3, 5, 7
# Output: 4

print(count_primes_py(20000) == count_primes_nb(20000))  # same result
# Output: True
print(count_primes_nb(20000))  # number of primes below 20000
# Output: 2262

t_py: float = min(timeit.repeat(lambda: count_primes_py(20000), number=3, repeat=3))  # python
t_nb: float = min(timeit.repeat(lambda: count_primes_nb(20000), number=3, repeat=3))  # compiled
print("numba at least 20x faster:", t_py / t_nb > 20)  # usually 50-200x
# Output: numba at least 20x faster: True
print("first call slower than later calls:", compile_time > t_nb / 3)  # compile cost paid once
# Output: first call slower than later calls: True
```

## 💻 Code Example — Advanced
```python
# Advanced Numba: explicit signature, cache, parallel prange, nopython errors
import numpy as np  # arrays
from numba import njit, prange, TypingError  # JIT, parallel range, error type
from numba import float64  # type object for the signature


@njit(float64(float64[:]), cache=True)  # eager compile with signature; cache=True saves to __pycache__
def moving_max_drawdown(prices: np.ndarray) -> float:
    peak: float = prices[0]  # highest price so far
    worst: float = 0.0  # biggest fall from a peak
    for i in range(1, prices.shape[0]):  # one pass, C speed
        if prices[i] > peak:  # new high
            peak = prices[i]  # update peak
        drop: float = (peak - prices[i]) / peak  # fall from the peak
        if drop > worst:  # bigger than any earlier fall
            worst = drop  # remember it
    return worst  # fraction, e.g. 0.25 = 25% drop


@njit(parallel=True)  # use all CPU cores for prange loops
def row_sums_parallel(m: np.ndarray) -> np.ndarray:
    out = np.empty(m.shape[0])  # result array
    for i in prange(m.shape[0]):  # iterations are split over threads
        s = 0.0  # private accumulator per row
        for j in range(m.shape[1]):  # inner loop stays serial
            s += m[i, j]  # add the value
        out[i] = s  # write the row total
    return out  # one total per row


prices: np.ndarray = np.array([100.0, 120.0, 90.0, 110.0, 60.0, 130.0])  # sample price series
print(moving_max_drawdown(prices))  # worst fall: peak 120 down to 60 = 50%
# Output: 0.5
print(moving_max_drawdown.signatures)  # the compiled signature(s)
# Output: [(Array(float64, 1, 'A', False, aligned=True),)]

m: np.ndarray = np.arange(12, dtype=np.float64).reshape(3, 4)  # 3 rows x 4 columns
print(row_sums_parallel(m))  # sum of each row
# Output: [ 6. 22. 38.]
print(np.allclose(row_sums_parallel(m), m.sum(axis=1)))  # matches NumPy
# Output: True


@njit  # nopython mode: unsupported Python features raise an error
def bad(x):
    return open("data.txt")  # file objects are not supported in nopython mode


try:  # show what a failure looks like
    bad(1)  # compile happens here
except TypingError:  # numba's typing error
    print("TypingError: numba could not compile this function")  # readable message
# Output: TypingError: numba could not compile this function
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python + Numba: one decorator, compiled on the first call
from numba import njit

@njit
def total(n: int) -> int:
    s = 0
    for i in range(n):
        s += i
    return s

print(total(10))   # 45
```
```javascript
// JavaScript: V8 already JIT-compiles hot functions automatically, no decorator needed
function total(n) {
  let s = 0;
  for (let i = 0; i < n; i++) s += i;
  return s;
}
console.log(total(10));   // 45
```

Key differences: V8 JIT-compiles every hot JS function for you. CPython does not, so Numba adds that opt-in JIT for numeric code. The cost is the first-call compile time and a restricted subset of Python (no arbitrary objects in nopython mode).

---

## 🟠 FastAPI Connection
Put CPU-bound numeric functions behind `@njit(cache=True)` and warm them up in the FastAPI `lifespan`, so the first user request does not pay the compile cost (often 0.5-several seconds). Use plain `def` endpoints so the work runs in the threadpool and does not block the event loop.

```python
# FastAPI + Numba: compile at startup (warm-up) so the first request is not slow
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator, Dict, List  # type hints

import numpy as np  # arrays
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client
from numba import njit  # JIT


@njit(cache=True)  # compiled once, cached on disk for next process start
def total_above(values: np.ndarray, limit: float) -> float:
    s = 0.0  # running total
    for v in values:  # compiled loop
        if v > limit:  # keep large values
            s += v  # add
    return s  # result


@asynccontextmanager  # startup/shutdown hook
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    total_above(np.zeros(1), 0.0)  # warm-up call triggers compilation before traffic
    yield  # app runs here


app: FastAPI = FastAPI(lifespan=lifespan)  # create app


@app.post("/above")  # sync def -> threadpool, fine for CPU work
def above(values: List[float], limit: float = 0.0) -> Dict[str, float]:
    return {"total": total_above(np.asarray(values, dtype=np.float64), limit)}  # call JIT code


with TestClient(app) as client:  # "with" runs the lifespan
    print(client.post("/above", params={"limit": 10}, json=[5, 20, 30]).json())  # call
# Output: {'total': 50.0}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Timing the first call
```python
# Wrong - the first call includes compile time:
import time
t = time.perf_counter(); f(x); print(time.perf_counter() - t)

# Correct - call once to warm up, then measure:
f(x)
t = time.perf_counter(); f(x); print(time.perf_counter() - t)
```

❌ Mistake 2: Using Python objects, pandas or unsupported features inside @njit
```python
# Wrong - DataFrame, dicts of mixed types, files and most libraries are not supported:
@njit
def bad(df):
    return df["price"].sum()

# Correct - pass NumPy arrays in, keep the compiled function purely numeric:
@njit
def good(prices):
    return prices.sum()
```

❌ Mistake 3: Forgetting that integers are fixed-width
```python
# Wrong - assuming unlimited ints like Python:
# @njit def f(a, b): return a + b   ->  f(2**62, 2**62) wraps to a negative number

# Correct - use float64, or check ranges before calling.
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
from numba import njit

@njit
def add(a, b):
    return a + b

print(add(1, 2), add(1.5, 2.5), add(1, 2.5))
print(len(add.signatures))
print(add(2**62, 2**62))
print(2**62 + 2**62)
```

**Answer**:
```
3 4.0 3.5
3
-9223372036854775808
9223372036854775808
```
Each new combination of argument types (int,int), (float,float), (int,float) triggers a separate compile, giving 3 signatures. Inside compiled code `int` is a 64-bit integer, so `2**62 + 2**62` wraps to the most negative int64, while normal Python integers never overflow.

---

## ⚫ Interview Questions + Answers

Q1: What does `@njit` mean and how is it different from `@jit`?
A1: `@njit` = `@jit(nopython=True)`: the whole function must compile without falling back to the Python interpreter. In current Numba `@jit` also defaults to nopython mode, but `@njit` is the explicit, recommended spelling because it fails loudly instead of silently running slowly.

Q2: Why is the first call slow?
A2: Numba compiles lazily on the first call for the observed argument types. Use `cache=True` to store compiled code on disk, or give an explicit signature to compile at import time.

Q3: Numba vs NumPy?
A3: NumPy is fast when you can express work as whole-array operations. Numba is for explicit loops and custom algorithms. They combine well: Numba functions take NumPy arrays.

Q4: What is `prange` / `parallel=True`?
A4: It splits loop iterations over CPU threads. Iterations must be independent; reductions like `s += x` are recognized, but other shared writes cause races.

Q5: Does Numba help with I/O-bound code?
A5: No. Use asyncio or threads for I/O. Numba only speeds CPU-bound numeric code.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You have numeric loops over NumPy arrays that cannot be vectorized
- You want C-like speed without writing C
- Simulation, finance, signal processing, custom distance functions

❌ Avoid when:
- The code uses pandas, dicts of objects, strings, or many third-party libraries
- The function runs only once for a short time (compile cost dominates)
- The bottleneck is network or database

---

## 📊 Visual Diagram

```
first call  f(array)                 later calls
   │                                    │
   ▼                                    ▼
 type inference ─► LLVM ─► machine code ─► run machine code directly
   (slow, once per type signature)         (fast, near C)

cache=True  →  machine code saved in __pycache__ for the next process start
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JIT | Compile at run time | चलते समय compile |
| nopython mode | Compiled code with no Python objects | बिना Python objects वाला compiled mode |
| Signature | Argument/return types of a compiled version | compiled version के types |
| LLVM | Compiler backend used by Numba | Numba का compiler backend |
| prange | Parallel range for threads | threads के लिए parallel range |
| Warm-up | Calling once to trigger compilation | compile कराने के लिए पहली call |

---

## ⚡ 3-Line Summary
English: Numba JIT-compiles numeric Python functions with `@njit`, giving near-C speed on NumPy loops without a build step. The first call compiles, so warm up and use `cache=True`. It supports only a numeric subset and fixed-width integers.
Hindi: Numba `@njit` से numeric Python functions को JIT compile करके NumPy loops को लगभग C की speed देता है, build step के बिना। पहली call में compile होता है, इसलिए warm-up करें और `cache=True` लें। यह सिर्फ numeric subset support करता है और integers fixed-width होते हैं।

---

## ➡️ Next Topic
**411. C Extensions Basics** — call hand-written C code from Python with ctypes and the CPython C API.
