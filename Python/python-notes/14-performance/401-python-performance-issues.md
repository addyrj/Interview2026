---

# 401. Python Performance Issues
# हिंदी में: Python की आम Performance समस्याएँ

---

## 🔵 Simple Definition (English)
Python performance issues are the common reasons Python code runs slower or uses more memory than it should: wrong data structures, loops that repeat work, string building in loops, N+1 database queries, blocking I/O in async code, and CPU-heavy work stuck behind the GIL. The fix is almost always: measure first, then change the algorithm or data structure, and only then reach for tools like NumPy, multiprocessing or Cython.

## 🔵 सरल परिभाषा (Hindi)
Python की performance समस्याएँ वे आम कारण हैं जिनसे code धीमा चलता है या ज़्यादा memory लेता है: गलत data structure, बार-बार दोहराया जाने वाला काम, loop में string जोड़ना, N+1 database queries, async code में blocking I/O, और GIL के पीछे फँसा CPU-heavy काम। हल: पहले measure करें, फिर algorithm/data structure बदलें, उसके बाद ही NumPy, multiprocessing या Cython लें।

---

## 🔴 Problem it Solves
Developers guess where the slowness is and "optimize" the wrong thing. Knowing the usual suspects (in order of impact) saves days: algorithmic complexity (O(n²) vs O(n)), I/O wait (database, network), memory (loading everything), then interpreter overhead. This note is the checklist you apply before any rewrite.

## 🔴 यह क्यों बना? (Hindi)
Developers अंदाज़े से गलत जगह optimize करते हैं। असर के क्रम में आम कारण जानने से दिन बचते हैं: algorithm की complexity (O(n²) बनाम O(n)), I/O इंतज़ार (database, network), memory (सब कुछ load करना), फिर interpreter का overhead। Rewrite से पहले यही checklist लगाएँ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: time (timeit), profile (cProfile), memory (tracemalloc). Never guess.
Step 2 → Classify: CPU-bound, I/O-bound, or memory-bound?
Step 3 → Fix the algorithm first: list -> set/dict lookups, remove nested loops, cache results
Step 4 → Fix I/O: batch queries (kill N+1), connection pool, async / threads for waiting
Step 5 → Fix memory: generators, chunked reading, __slots__, right data types
Step 6 → CPU-heavy: NumPy vectorization, multiprocessing, Cython/Numba, or a faster language
Step 7 → Re-measure to prove the gain; keep the benchmark as a regression test
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Measure: timeit, cProfile, tracemalloc। अंदाज़ा नहीं।
Step 2 → पहचानें: CPU-bound, I/O-bound या memory-bound?
Step 3 → पहले algorithm: list की जगह set/dict, nested loops हटाना, results cache करना
Step 4 → I/O: queries batch करना (N+1 खत्म), connection pool, async/threads
Step 5 → Memory: generators, chunks में पढ़ना, __slots__
Step 6 → CPU-heavy: NumPy, multiprocessing, Cython/Numba
Step 7 → दोबारा measure करके सुधार साबित करें
```

---

## 🟡 Real World Example
A Swiggy-style "my orders" endpoint took 4 seconds. Profiling showed 1 query for orders plus 1 query per order for restaurant (N+1: 200 orders = 201 queries), and a `list` membership check inside a loop. Fixing with one `JOIN` and a `set` brought it to 80 ms. The Python code itself was never the bottleneck.

## 🟡 Real Example Hindi mein
Swiggy जैसा "my orders" endpoint 4 सेकंड लेता था। Profiling में दिखा: orders की 1 query और हर order के restaurant की 1-1 query (N+1: 200 orders = 201 queries), साथ में loop के अंदर `list` membership check। एक `JOIN` और `set` से यह 80 ms हो गया। Python code कभी bottleneck नहीं था।

---

## 💻 Code Example — Basic
```python
# VERIFIED: ran on Python 3.13.3. Timings vary by machine, so we print only comparisons (True/False).
import timeit  # micro-benchmarks
from typing import List, Set  # type hints

# --- Issue 1: membership test on a list is O(n), on a set it is O(1) ---
ids: List[int] = list(range(10_000))  # list of 10k ids
id_set: Set[int] = set(ids)  # same data as a set
t_list: float = timeit.timeit(lambda: 9_999 in ids, number=2000)  # worst case: scans the whole list
t_set: float = timeit.timeit(lambda: 9_999 in id_set, number=2000)  # hash lookup
print("list slower than set by more than 50x:", t_list / t_set > 50)  # Output: True


# --- Issue 2: building a string with += in a loop ---
def concat_bad(n: int) -> str:
    s: str = ""  # start empty
    for i in range(n):  # n iterations
        s += str(i)  # may copy the whole string each time (CPython sometimes optimises this, never rely on it)
    return s


def concat_good(n: int) -> str:
    return "".join(str(i) for i in range(n))  # one allocation at the end


assert concat_bad(1000) == concat_good(1000)  # same result, different cost
print(concat_good(5))  # Output: 01234


# --- Issue 3: no profiling ---
import cProfile  # standard profiler
import io  # capture the report as text
import pstats  # read the report


def fib(n: int) -> int:  # slow recursive version on purpose
    return n if n < 2 else fib(n - 1) + fib(n - 2)


prof = cProfile.Profile()  # create profiler
prof.enable()  # start
fib(20)  # code to measure
prof.disable()  # stop
buf = io.StringIO()  # buffer for the text report
pstats.Stats(prof, stream=buf).sort_stats("cumulative").print_stats(2)  # top 2 lines
print(buf.getvalue().splitlines()[0].strip())  # Output: 21892 function calls (2 primitive calls) in 0.004 seconds
# (time varies; the call count 21892 is stable for fib(20))
```

## 💻 Code Example — Advanced
```python
# VERIFIED: ran on Python 3.13.3. Shows the 4 biggest real-world fixes with typed, testable code.
import sys  # getsizeof
import timeit  # benchmark
import tracemalloc  # memory tracking
from functools import lru_cache  # caching
from typing import Dict, Iterator, List


# ---- Fix A: N+1 style nested loop -> dict index (emulates N+1 DB queries) ----
users: List[Dict[str, object]] = [{"id": i, "name": f"u{i}"} for i in range(2000)]  # 2000 users
orders: List[Dict[str, int]] = [{"user_id": i % 2000, "amt": i} for i in range(4000)]  # 4000 orders


def slow_join() -> int:
    count: int = 0  # matches found
    for o in orders:  # for each order ...
        for u in users:  # ... scan every user (O(n*m)), like 1 query per order
            if u["id"] == o["user_id"]:
                count += 1
                break
    return count


def fast_join() -> int:
    by_id: Dict[object, Dict[str, object]] = {u["id"]: u for u in users}  # build index once, O(n)
    return sum(1 for o in orders if o["user_id"] in by_id)  # O(1) per order, like a SQL JOIN


assert slow_join() == fast_join() == 4000  # identical results
print("dict join >20x faster:", timeit.timeit(slow_join, number=1) / timeit.timeit(fast_join, number=1) > 20)
# Output: dict join >20x faster: True


# ---- Fix B: generator instead of a huge list (memory) ----
def numbers(n: int) -> Iterator[int]:
    for i in range(n):  # produces one value at a time
        yield i


big_list = [i for i in range(1_000_000)]  # all values in memory
gen = numbers(1_000_000)  # nothing computed yet
print(sys.getsizeof(big_list) > sys.getsizeof(gen) * 1000)  # Output: True (list ~8 MB, generator ~200 bytes)
print(sum(numbers(10)))  # Output: 45


# ---- Fix C: cache repeated pure computations ----
@lru_cache(maxsize=1024)  # remember the last 1024 results
def square(n: int) -> int:
    return n * n  # imagine something expensive here


square(4)  # miss: computed
square(4)  # hit: from cache
print(square.cache_info())  # Output: CacheInfo(hits=1, misses=1, maxsize=1024, currsize=1)


# ---- Fix D: __slots__ for millions of small objects ----
class Plain:
    def __init__(self) -> None:
        self.x: int = 1  # stored in a per-object dict (extra memory)
        self.y: int = 2


class Slotted:
    __slots__ = ("x", "y")  # fixed attributes, no per-object dict

    def __init__(self) -> None:
        self.x: int = 1
        self.y: int = 2


tracemalloc.start()  # begin tracking allocations
plain = [Plain() for _ in range(100_000)]  # 100k normal objects
mem_plain: int = tracemalloc.get_traced_memory()[0]  # bytes in use now
del plain  # free them
slotted = [Slotted() for _ in range(100_000)]  # 100k slotted objects
mem_slotted: int = tracemalloc.get_traced_memory()[0]  # bytes in use now
tracemalloc.stop()  # stop tracking
print("slots use less memory:", mem_plain > mem_slotted)  # Output: slots use less memory: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: use set for fast lookups, "".join for strings, generators for big data
seen = set(ids)
ok = user_id in seen
text = "".join(parts)
total = sum(x * x for x in range(1_000_000))      # generator, no big list
```
```javascript
// JavaScript: Set for lookups, array join, iterate without building arrays
const seen = new Set(ids);
const ok = seen.has(userId);
const text = parts.join("");
let total = 0; for (let x = 0; x < 1e6; x++) total += x * x;
```

Key differences: JavaScript runs on a JIT engine (V8), so tight number loops are usually much faster than CPython loops. Python's big gains come from using C-backed libraries (NumPy, pandas), the right data structures, and multiprocessing for CPU work (the GIL limits threads for CPU-bound code; the free-threaded build is available from 3.13 but is experimental). Node is single-threaded for JS code too, and both languages suffer from blocking I/O in the event loop.

---

## 🟠 FastAPI Connection
Top FastAPI slowdowns: blocking calls inside `async def`, N+1 ORM queries, huge response lists, and loading models per request.

```python
# FastAPI: avoid blocking the event loop (verified structure with TestClient is simple; code below is illustrative)
import asyncio  # async tools
import time  # blocking sleep to simulate slow work
from typing import Dict
from fastapi import FastAPI  # framework

app: FastAPI = FastAPI()  # create app


@app.get("/bad")
async def bad() -> Dict[str, str]:
    time.sleep(1)  # WRONG: blocks the whole event loop; every other request waits 1 s
    return {"status": "done"}


@app.get("/good-async")
async def good_async() -> Dict[str, str]:
    await asyncio.sleep(1)  # non-blocking wait: other requests continue
    return {"status": "done"}


@app.get("/good-sync")
def good_sync() -> Dict[str, str]:  # plain def: FastAPI runs it in a thread pool
    time.sleep(1)  # blocking is OK here, only this worker thread waits
    return {"status": "done"}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Optimizing without measuring
```python
# Wrong: rewriting a function "because it looks slow"
# Right: python -m cProfile -s cumtime app.py  (or py-spy / line_profiler) and fix the top item
```

❌ Mistake 2: `x in some_list` inside a loop
```python
# Wrong: O(n*m)
bad = [x for x in a if x in b_list]

# Right: O(n + m)
b_set = set(b_list)
good = [x for x in a if x in b_set]
```

❌ Mistake 3: N+1 queries
```python
# Wrong: one query per order
for order in orders:
    restaurant = db.query(Restaurant).get(order.restaurant_id)

# Right: one JOIN or an eager load (SQLAlchemy: selectinload / joinedload)
```

❌ Mistake 4: Loading a whole file or table into memory
```python
# Wrong
lines = open("big.log").readlines()

# Right: stream it
with open("big.log") as f:
    for line in f:
        process(line)
```

❌ Mistake 5: Believing micro-tricks matter (and that they always help)
```python
# Caching math.sqrt in a local variable ("sq = math.sqrt") is an old trick.
# On Python 3.13 in our test it was NOT reliably faster; the adaptive interpreter already optimises it.
# Right: fix big-O and I/O first; micro-optimise only what the profiler flags, and re-measure.
```

---

## 🧠 Tricky Interview Question

**Q**: Does this make 4 threads 4x faster? Why or why not?

```python
import threading

def work():
    total = 0
    for i in range(50_000_000):
        total += i

threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
```

**Answer**: No. This is CPU-bound pure Python code, and in the default CPython build the GIL lets only one thread execute Python bytecode at a time, so 4 threads take about as long as (or longer than) running the function 4 times in a row. Use `multiprocessing` / `ProcessPoolExecutor` (separate interpreters), NumPy (releases the GIL in C code), or the experimental free-threaded build of 3.13+. Threads DO help for I/O-bound work (network, disk) because the GIL is released while waiting.

---

## ⚫ Interview Questions + Answers

Q1: How do you find why a Python program is slow?
A1: Profile. `cProfile` for function-level time, `line_profiler` for line-level, `tracemalloc`/`memray` for memory, `py-spy` for a live process. Fix the biggest cost first.

Q2: Why is `s += "x"` in a loop discouraged?
A2: Strings are immutable. Each `+=` can create a new string (O(n²) overall in the worst case). CPython has an in-place optimisation in some cases, but it is not guaranteed. Collect parts in a list and use `"".join(parts)`.

Q3: What is an N+1 query problem?
A3: Running 1 query to fetch N rows and then N more queries to fetch related data. Fix with a JOIN, `IN (...)` batch query, or ORM eager loading.

Q4: When do you use threads, processes, or asyncio?
A4: Asyncio or threads for I/O-bound; processes for CPU-bound; NumPy/C extensions for number crunching.

Q5: What does `__slots__` do?
A5: It removes the per-instance `__dict__` and fixes the attribute set, saving memory (useful for millions of small objects) and slightly speeding attribute access. Downside: no arbitrary new attributes and some limits with multiple inheritance.

---

## 🔷 When to Use + When Not to Use

✅ Optimize when:
- A profile shows a clear hotspot or you miss a latency/memory target
- Data size will grow (O(n²) code will fail at scale)
- The code is on a hot path (called thousands of times per second)

❌ Do not optimize when:
- You have not measured
- The code runs once a day on small data
- The change makes code much harder to read for a gain of a few percent

---

## 📊 Visual Diagram

```
Slow request (4000 ms)
 ├── 3500 ms  DB: 201 queries (N+1)            -> fix: JOIN / eager load
 ├──  300 ms  `x in list` inside loops (O(n²)) -> fix: set / dict
 ├──  150 ms  JSON building of huge lists      -> fix: pagination / streaming
 └──   50 ms  "real" Python logic

Order of attack: I/O  ->  algorithm  ->  memory  ->  CPU tricks (NumPy / processes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profiling | Measuring where time goes | समय कहाँ जा रहा है नापना |
| Big-O | How cost grows with input | input बढ़ने पर cost कैसे बढ़ता है |
| N+1 | One query plus N extra queries | 1 query के बाद N और queries |
| GIL | One thread runs Python at a time | एक समय में एक thread |
| I/O-bound | Waiting on disk/network | disk/network का इंतज़ार |
| CPU-bound | Limited by computation | गणना पर निर्भर |

---

## ⚡ 3-Line Summary
English: Measure first, then fix algorithm and data structures (set/dict), I/O (N+1, blocking calls), and memory (generators, slots). Use processes or NumPy for CPU-bound work because of the GIL.
Hindi: पहले measure करें, फिर algorithm और data structures (set/dict), I/O (N+1, blocking calls) और memory (generators, slots) सुधारें। GIL की वजह से CPU-bound काम के लिए processes या NumPy लें।

---

## ➡️ Next Topic
**402. Profiling with cProfile** — find the real bottleneck before optimizing.
