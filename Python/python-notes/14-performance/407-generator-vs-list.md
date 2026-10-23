---

# 407. Generator vs List — Performance Complete Guide
# हिंदी में: Generator vs List — Performance पूरी Guide

---

## 🔵 Simple Definition (English)
A list comprehension `[x for x in data]` builds the **entire list in memory at once**. A generator expression `(x for x in data)` is lazy — it computes values **one at a time** as you iterate, using O(1) memory regardless of data size. Generators are critical for processing large files, database result sets, or infinite sequences. The difference: `[]` = everything now, `()` = one at a time.

## 🔵 सरल परिभाषा (Hindi)
List comprehension `[x for x in data]` = पूरी list memory में एक बार। Generator expression `(x for x in data)` = lazy — iterate करते समय एक-एक value compute। O(1) memory। Large files, DB results, infinite sequences के लिए critical। `[]` = सब अभी, `()` = एक-एक करके।

---

## 💻 Code Example — Basic
```python
# ─── List vs Generator — syntax comparison ───────────────────────

# List comprehension: builds ALL items immediately
squares_list = [x**2 for x in range(10)]
print(squares_list)   # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81] — all in memory

# Generator expression: computes on demand
squares_gen = (x**2 for x in range(10))
print(squares_gen)    # <generator object <genexpr> at 0x...> — not computed yet!

# Consume generator:
for val in squares_gen:
    print(val)   # 0, 1, 4, 9, 16, ... — computed one at a time

# Or convert to list:
result = list(squares_gen)  # but now it's a list again!

# ─── Generators are one-time use! ─────────────────────────────────
gen = (x**2 for x in range(5))
print(list(gen))   # [0, 1, 4, 9, 16] ✓
print(list(gen))   # []  ← EMPTY! generator exhausted!

# Lists can be iterated multiple times:
lst = [x**2 for x in range(5)]
print(list(lst))   # [0, 1, 4, 9, 16] ✓
print(list(lst))   # [0, 1, 4, 9, 16] ✓ again

# ─── Generator function with `yield` ─────────────────────────────
def fibonacci():
    """Infinite Fibonacci sequence — impossible with a list!"""
    a, b = 0, 1
    while True:          # infinite loop — OK with generator!
        yield a          # pause here, return a, resume next iteration
        a, b = b, a + b

fib = fibonacci()
for _ in range(10):
    print(next(fib))     # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

# ─── Memory comparison ────────────────────────────────────────────
import sys

n = 1_000_000

# List: all 1M items in memory at once:
lst = [x**2 for x in range(n)]
print(f"List size: {sys.getsizeof(lst):,} bytes")   # ~8,000,056 bytes (8MB)

# Generator: single object regardless of n:
gen = (x**2 for x in range(n))
print(f"Generator size: {sys.getsizeof(gen)} bytes")   # ~208 bytes!

# Sum works on both — but generator uses O(1) memory:
total_list = sum(lst)           # holds 8MB while summing
total_gen  = sum(x**2 for x in range(n))   # O(1) memory!
```

## 💻 Code Example — Advanced
```python
import time
import sys
from typing import Iterator

# ─── Real-world: processing large files ───────────────────────────
# WRONG — loads entire file into memory:
def count_long_lines_bad(filepath: str, min_len: int = 100) -> int:
    with open(filepath) as f:
        lines = f.readlines()    # 10GB file → 10GB in RAM!
    return sum(1 for line in lines if len(line) >= min_len)

# CORRECT — generator, O(1) memory:
def count_long_lines_good(filepath: str, min_len: int = 100) -> int:
    with open(filepath) as f:
        return sum(1 for line in f if len(line) >= min_len)
        # 'for line in f' is already a generator (file iterator)

# ─── Generator pipeline — compose multiple lazy operations ────────
def read_logs(filepath: str) -> Iterator[str]:
    """Lazily read log lines."""
    with open(filepath) as f:
        for line in f:
            yield line.strip()

def filter_errors(lines: Iterator[str]) -> Iterator[str]:
    """Lazily filter ERROR lines."""
    for line in lines:
        if "ERROR" in line:
            yield line

def parse_timestamps(lines: Iterator[str]) -> Iterator[dict]:
    """Lazily parse each error line."""
    for line in lines:
        parts = line.split(" | ")
        if len(parts) >= 2:
            yield {"timestamp": parts[0], "message": parts[1]}

# Compose pipeline — nothing runs until consumed!
def process_log_file(filepath: str) -> Iterator[dict]:
    lines = read_logs(filepath)         # lazy
    errors = filter_errors(lines)       # lazy
    parsed = parse_timestamps(errors)   # lazy
    return parsed

# Only here does processing happen, one line at a time:
for error in process_log_file("app.log"):
    print(error)

# ─── Send values into generators ──────────────────────────────────
def running_average() -> float:
    """Generator that accepts values and yields running average."""
    total = 0.0
    count = 0
    while True:
        value = yield total / count if count > 0 else 0
        if value is None:
            break
        total += value
        count += 1

avg_gen = running_average()
next(avg_gen)          # prime the generator (advance to first yield)
avg_gen.send(10)       # → 10.0
avg_gen.send(20)       # → 15.0
avg_gen.send(30)       # → 20.0

# ─── When to use list vs generator ───────────────────────────────
# USE LIST when:
# 1. You need random access: data[50]
# 2. You need len(): len(data)
# 3. You iterate multiple times
# 4. Data is small (< few thousand items)
# 5. You need to reverse or slice

# USE GENERATOR when:
# 1. Single pass through data
# 2. Data is large (files, DB result sets, API pages)
# 3. Data might be infinite (fibonacci, event streams)
# 4. You compose lazy pipelines
# 5. Memory is constrained

# ─── Performance benchmark ────────────────────────────────────────
import time

n = 10_000_000

# List: builds entire list, then sums:
start = time.perf_counter()
result = sum([x**2 for x in range(n)])
list_time = time.perf_counter() - start
# ~1.5 seconds, ~80MB memory

# Generator: sums on the fly:
start = time.perf_counter()
result = sum(x**2 for x in range(n))
gen_time = time.perf_counter() - start
# ~0.8 seconds, ~200 bytes memory

print(f"List: {list_time:.2f}s, Generator: {gen_time:.2f}s")
# Generator: ~2x faster AND uses 400,000x less memory!
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python generator:
def* range_gen(n):   # NOT valid Python syntax

# Python uses yield:
def count_up(n):
    for i in range(n):
        yield i

gen = count_up(5)
print(next(gen))   # 0

# Generator expression:
squares = (x**2 for x in range(10))
```

```javascript
// JavaScript generator:
function* countUp(n) {
    for (let i = 0; i < n; i++) {
        yield i;
    }
}

const gen = countUp(5);
console.log(gen.next().value);   // 0

// Array vs generator (lazy):
const squares = Array.from({length: 10}, (_, i) => i**2);  // list
function* squaresGen() { for (let i=0; i<10; i++) yield i**2; }  // generator
```

Key similarities:
- Both use `yield` keyword. Both return iterators.
- Both are lazy — only compute when iterated.
- `next()` in Python = `.next()` in JS.
- Generator expressions `(x for x in data)` = no direct JS equivalent (use `function*`).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Consuming generator twice
```python
# Wrong:
data = (process(x) for x in large_dataset)
first_pass = list(data)     # works
second_pass = list(data)    # returns [] — generator exhausted!

# Correct: materialize if you need multiple passes:
data = [process(x) for x in large_dataset]   # use list if small enough
# Or recreate generator each time you need it
```

❌ Mistake 2: Using `len()` on a generator
```python
# Wrong — TypeError: object of type 'generator' has no len():
gen = (x for x in range(10))
print(len(gen))    # TypeError!

# Correct options:
count = sum(1 for _ in gen)        # counts while iterating (exhausts gen)
lst = list(gen); count = len(lst)   # materialize first
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `yield` and `return` in a function?

**Answer**: A function with `return` runs to completion and returns once. A function with `yield` becomes a **generator function** — calling it returns a generator object (doesn't run the body!). `next(gen)` runs until the next `yield`, pauses, and returns the yielded value. The function's local state (variables) is preserved between yields. When the function returns (or falls off the end), `StopIteration` is raised. Multiple `yield` statements in one function = multiple values produced.

---

## ⚫ Interview Questions + Answers

Q1: What is lazy evaluation and why does it matter?
A1: Lazy evaluation means deferring computation until the result is needed. Generators are lazy — `(x**2 for x in range(1M))` doesn't compute any squares until you iterate. Benefits: (1) Memory efficiency — no 8MB list for 1M squares. (2) Speed for early exit — `next(x for x in huge_list if x > 5)` stops at first match, not scan all. (3) Composability — build pipelines of lazy transformations. (4) Infinite sequences — you can't store an infinite list. Eagerness (lists) is better when: random access needed, multiple passes needed, or data is small.

Q2: What is the `yield from` statement?
A2: `yield from iterable` delegates to another iterable (including generators), yielding each value. Cleaner than `for x in sub_gen: yield x`. Example: `def flat(nested): for lst in nested: yield from lst`. Also propagates `.send()` and `.throw()` to the sub-generator, enabling bidirectional communication. Used in `asyncio` before `async/await` was introduced — `async def` functions are internally built on generators.

Q3: How do generators improve performance in data processing pipelines?
A3: Chaining generators creates a lazy pipeline — data flows through all stages one item at a time without intermediate storage. `filter_errors(parse_logs(read_file(path)))` reads one log line, filters it, parses it, and yields it — no intermediate lists. Memory stays O(1) regardless of file size. Speed improves because: less memory allocation/GC, better CPU cache locality (processing one item through all stages), and early termination (if you only need first 100 errors, remaining file is unread). For large data sets, this can be 10-100x more memory efficient.

Q4: What is the difference between an iterator and a generator?
A4: An **iterator** is any object implementing `__iter__()` (returns self) and `__next__()` (returns next value or raises StopIteration). A **generator** is a special iterator created by a generator function (uses `yield`) or generator expression. All generators are iterators, but not all iterators are generators. Custom iterators need a class with `__iter__` and `__next__`. Generators are syntactic sugar — Python auto-implements the iterator protocol. Use generators when possible (simpler code); write custom iterator classes when you need more control (caching, seeking, etc.).

Q5: When should you NOT use a generator?
A5: Don't use generators when: (1) **Multiple passes needed** — generators exhaust after one pass; use a list. (2) **Random access needed** — `gen[50]` doesn't work; use a list. (3) **len() needed** — generators have no length. (4) **Small, frequently used data** — a list is simpler and just as efficient for <1000 items. (5) **Debugging** — generators are harder to inspect; a list lets you `print(data[5:10])`. (6) **Async contexts** — don't mix sync generators with async code; use `async def` with `async for` and `async_generator`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generator | Lazy iterator with yield | Lazy iterator with yield |
| yield | Pause function, return value | Function pause, value return |
| Lazy evaluation | Compute on demand | जरूरत पड़ने पर compute |
| Exhausted | Generator used up (empty) | Generator खत्म हो गया |
| Pipeline | Chained lazy operations | Chained lazy operations |
| StopIteration | Generator finished signal | Generator खत्म होने का signal |
| yield from | Delegate to sub-generator | Sub-generator को delegate |

---

## ⚡ 3-Line Summary
English: Generator expressions `(x for x in data)` use O(1) memory vs list comprehensions `[...]` which load everything. Use generators for: large files, DB result sets, infinite sequences, and lazy pipelines. Generators are single-use — materialize to a list if you need multiple passes or random access.
Hindi: Generator expressions `(...)` O(1) memory use करते हैं। Large files, DB results, infinite sequences, lazy pipelines के लिए generators। Generators one-time use हैं — multiple passes के लिए list बनाओ।

---

## ➡️ Next Topic
**401. Performance Profiling** — cProfile, line_profiler, finding bottlenecks. **406. List vs Loop** — when comprehensions beat loops. **415. Redis Caching** — cache expensive computations.
