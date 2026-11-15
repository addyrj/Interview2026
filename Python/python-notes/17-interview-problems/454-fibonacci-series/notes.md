---

# 454. Fibonacci Series
# हिंदी में: Fibonacci Series (हर संख्या = पिछली दो का जोड़)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `fib series: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]` and `All Fibonacci tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
The Fibonacci series starts `0, 1` and every next number is the sum of the previous two: `0, 1, 1, 2, 3, 5, 8, 13...`. The problem is to compute the n-th number or the first n numbers efficiently.

## 🔵 सरल परिभाषा (Hindi)
Fibonacci series `0, 1` से शुरू होती है और अगली हर संख्या पिछली दो का जोड़ होती है: `0, 1, 1, 2, 3, 5, 8, 13...`। Problem है n-वीं संख्या या पहली n संख्याएँ कुशलता से निकालना।

---

## 🔴 Problem it Solves
It is the standard way to teach recursion, memoization (dynamic programming) and time complexity. Naive recursion looks elegant but takes exponential time; interviewers want you to notice repeated work and fix it. The same pattern (overlapping subproblems) shows up in pricing, path counting and caching.

## 🔴 यह क्यों बना? (Hindi)
Recursion, memoization (dynamic programming) और time complexity सिखाने का यह standard तरीका है। सीधी recursion सुंदर दिखती है पर exponential समय लेती है; interviewer चाहते हैं कि आप दोहराया गया काम पहचानकर उसे ठीक करें। यही pattern (overlapping subproblems) pricing, path counting और caching में मिलता है।

---

## 🟢 How it Works — Step by Step

```
Naive recursion: fib(n) = fib(n-1) + fib(n-2); base: fib(0)=0, fib(1)=1
   -> recomputes the same values again and again: O(2^n)
Memoized: store each fib(k) once in a cache -> O(n)
Iterative: keep only two numbers (a, b), slide forward n times -> O(n) time, O(1) space
Generator: yield a; a, b = b, a + b  -> infinite lazy series
Fast doubling: fib(2k) = F(k) * (2F(k+1) - F(k)) ; fib(2k+1) = F(k)^2 + F(k+1)^2 -> O(log n)
```

## 🟢 कैसे काम करता है? (Hindi)
```
सीधी recursion: fib(n) = fib(n-1) + fib(n-2); base: fib(0)=0, fib(1)=1
   -> वही values बार-बार निकलती हैं: O(2^n)
Memoized: हर fib(k) एक बार cache में रखो -> O(n)
Iterative: सिर्फ़ दो संख्याएँ (a, b) रखो, n बार आगे खिसकाओ -> O(n) समय, O(1) space
Generator: yield a; a, b = b, a + b  -> अनंत lazy series
Fast doubling: fib(2k) और fib(2k+1) के formula से -> O(log n)
```

---

## 🟡 Real World Example
Fibonacci backoff is used for retries: wait 1s, 1s, 2s, 3s, 5s, 8s between attempts when a payment gateway such as Razorpay times out. Cached recursion (`lru_cache`) is the same technique used to avoid recomputing expensive results in a pricing service or a feature pipeline.

## 🟡 Real Example Hindi mein
Retries में Fibonacci backoff इस्तेमाल होता है: Razorpay जैसा payment gateway timeout दे तो attempts के बीच 1s, 1s, 2s, 3s, 5s, 8s इंतज़ार किया जाता है। Cached recursion (`lru_cache`) वही तकनीक है जिससे pricing service या feature pipeline में महँगे results दोबारा नहीं निकाले जाते।

---

## 💻 Code Example — Basic
```python
# Basic: iterative Fibonacci (O(n) time, O(1) space)
def fib(n: int) -> int:  # n-th Fibonacci number, fib(0) = 0
    a: int = 0  # fib(0)
    b: int = 1  # fib(1)
    for _ in range(n):  # slide the pair forward n times
        a, b = b, a + b  # tuple assignment, no temp variable
    return a  # after n slides, a is fib(n)


print([fib(i) for i in range(10)])  # first ten numbers
# Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(fib(90))  # Python ints never overflow
# Output: 2880067194370816120
```

## 💻 Code Example — Advanced
```python
# From main.py: memoization, generator, and the cost of naive recursion
import time  # to time the difference
from functools import lru_cache  # automatic memoization
from typing import Iterator  # type hint


def fib_naive(n: int) -> int:  # O(2^n)
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)  # two recursive calls


@lru_cache(maxsize=None)  # remember every result
def fib_memo(n: int) -> int:  # O(n) time, O(n) space
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_gen() -> Iterator[int]:  # infinite generator
    a, b = 0, 1
    while True:
        yield a  # hand out one number
        a, b = b, a + b


calls: int = 0  # count how many calls naive recursion makes


def counted(n: int) -> int:
    global calls
    calls += 1  # one more call
    return n if n < 2 else counted(n - 1) + counted(n - 2)


counted(20)  # compute fib(20) the slow way
print(calls)  # number of function calls for n = 20
# Output: 21891
print(fib_memo(30))  # instant with the cache
# Output: 832040
print(fib_memo.cache_info().currsize)  # 31 cached results (n = 0..30)
# Output: 31
gen: Iterator[int] = fib_gen()  # create the generator
print([next(gen) for _ in range(8)])  # take eight values lazily
# Output: [0, 1, 1, 2, 3, 5, 8, 13]
t: float = time.perf_counter()  # start timer
fib_naive(27)  # slow
print(time.perf_counter() - t > 0)  # timing varies per machine; naive is always the slowest
# Output: True
```

(`fib_memo.cache_info().currsize` is 31 only if the cache was empty before; `main.py` also adds `fib_fast`, the O(log n) fast-doubling version.)

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: tuple swap + unlimited integers
a, b = 0, 1
for _ in range(90):
    a, b = b, a + b
print(a)   # 2880067194370816120  (exact)
```
```javascript
// JavaScript: numbers are 64-bit floats; use BigInt after 2^53
let a = 0n, b = 1n;
for (let i = 0; i < 90; i++) { [a, b] = [b, a + b]; }   // destructuring swap
console.log(a);   // 2880067194370816120n
```

Key differences: Python integers have arbitrary precision, so `fib(1000)` is exact. In JavaScript the default `Number` loses precision past 2^53 (about `fib(78)`); use `BigInt`. Python offers `@lru_cache` for memoization; JS needs a hand-written `Map` cache.

---

## 🟠 FastAPI Connection
A CPU-heavy computation inside an `async` endpoint blocks the event loop. Use a plain `def` endpoint (FastAPI runs it in a thread pool), cap the input, and cache results.

```python
# FastAPI: Fibonacci endpoint (pip install fastapi)
from functools import lru_cache  # cache repeated requests

from fastapi import FastAPI, Query  # framework

app: FastAPI = FastAPI()  # create app


@lru_cache(maxsize=1024)  # remember answers across requests
def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.get("/fib")  # GET /fib?n=50
def get_fib(n: int = Query(..., ge=0, le=5000)) -> dict[str, str]:  # sync def -> runs in thread pool
    return {"n": str(n), "value": str(fib(n))}  # return as str: JSON clients (JS) lose precision on big ints
```

Not run as a server here; the arithmetic is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Naive recursion for large n
✅ Correct: use memoization or a loop.

```python
# Wrong - fib(40) takes many seconds, fib(100) never finishes
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
# Right
from functools import lru_cache
@lru_cache(maxsize=None)
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
```

❌ Mistake 2: Mutable default argument as cache (`def fib(n, memo={})`)
✅ Correct: it happens to work but is shared across calls and surprising; prefer `lru_cache` or an explicit argument.

❌ Mistake 3: Starting the series at 1, 1 and mixing indexing
✅ Correct: state your convention. Here `fib(0) = 0`, `fib(1) = 1`.

---

## 🧠 Tricky Interview Question

**Q**: How many function calls does naive `fib(20)` make, and how many entries does the cache of the memoized `fib(30)` hold?

```python
calls = 0
def fn(n):
    global calls
    calls += 1
    return n if n < 2 else fn(n - 1) + fn(n - 2)
fn(20)
print(calls)
```

**Answer**: `21891` calls for naive `fib(20)` (the count is `2 * fib(21) - 1`), versus only 21 distinct subproblems that memoization solves once each. The memoized `fib(30)` stores 31 results (n = 0..30). This is the exponential-versus-linear gap.

---

## ⚫ Interview Questions + Answers

Q1: Why is naive recursive Fibonacci slow?
A1: It solves the same subproblems repeatedly, so the call tree has about 2^n nodes (precisely O(phi^n), about 1.618^n).

Q2: Time and space complexity of each approach?
A2: Naive O(2^n) time, O(n) stack. Memoized O(n) time, O(n) space. Iterative O(n) time, O(1) space. Fast doubling O(log n) time.

Q3: How do you hit `RecursionError` and fix it?
A3: Memoized recursion for `n` above about 1000 exceeds the recursion limit. Use the iterative version (or `sys.setrecursionlimit`, which is risky).

Q4: What is the difference between memoization and tabulation?
A4: Memoization is top-down: recurse and cache results. Tabulation is bottom-up: fill a table (or two variables) from the base cases, which is the iterative version.

Q5: How would you produce Fibonacci numbers lazily?
A5: A generator with `yield`; callers use `itertools.islice(fib_gen(), 10)` to take the first ten.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Teaching or testing recursion and dynamic programming
- You need growth-style delays (backoff) or sequences with overlapping subproblems
- You want an infinite lazy generator example

❌ Avoid when:
- You use naive recursion in production code
- You need huge `n` and ignore big-integer cost (digits grow linearly)
- A closed-form or library function already exists for the real problem

---

## 📊 Visual Diagram

```
 fib(5)
 ├─ fib(4)
 │   ├─ fib(3)
 │   │   ├─ fib(2) ...      <- fib(3) computed twice,
 │   │   └─ fib(1)             fib(2) three times...
 │   └─ fib(2) ...
 └─ fib(3)                  <- repeated work (memoization stores it once)
     ├─ fib(2)
     └─ fib(1)

 iterative:  (a,b) = (0,1) -> (1,1) -> (1,2) -> (2,3) -> (3,5) ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recursion | Function calls itself | function का खुद को call करना |
| Memoization | Cache results of calls | results को cache करना |
| Dynamic programming | Solve by reusing subproblems | subproblems दोबारा इस्तेमाल करना |
| Base case | Stops recursion | recursion रोकने वाला case |
| Generator | Lazy sequence producer | lazy sequence बनाने वाला |
| Backoff | Growing wait between retries | retries के बीच बढ़ता इंतज़ार |

---

## ⚡ 3-Line Summary
English: Naive recursion is O(2^n) because it repeats work; memoization makes it O(n). The iterative two-variable loop is O(n) time and O(1) space, and fast doubling gives O(log n). Python's big integers make large results exact.
Hindi: सीधी recursion काम दोहराने से O(2^n) होती है; memoization इसे O(n) कर देता है। दो variables वाला loop O(n) समय और O(1) space लेता है, और fast doubling O(log n) देता है। Python के बड़े integers से बड़े results भी सटीक मिलते हैं।

---

## ➡️ Next Topic
**455. Factorial (recursive + iterative)** — another recursion classic, with the recursion-limit trade-off.
