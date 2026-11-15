---

# 159. Memory Profiling
# हिंदी में: Memory Profiling (memory कहाँ खर्च हो रही है पता करना)

---

## 🔵 Simple Definition (English)
Memory profiling means measuring how much memory your Python code uses and which lines allocate it. The standard library gives you `sys.getsizeof` (size of one object) and `tracemalloc` (tracks every allocation, takes snapshots, and shows where growth happens).

## 🔵 सरल परिभाषा (Hindi)
Memory profiling का मतलब है यह नापना कि आपका Python code कितनी memory लेता है और कौन सी lines allocate करती हैं। Standard library में `sys.getsizeof` (एक object का size) और `tracemalloc` (हर allocation track करता है, snapshots लेता है और बताता है growth कहाँ हो रही है) मिलते हैं।

---

## 🔴 Problem it Solves
A service slowly eats RAM until Kubernetes kills it with OOMKilled. Guessing does not help. Profiling shows exactly which line or data structure grows, so you can fix a leak (an ever-growing cache) or a waste (list instead of generator, normal class instead of `__slots__`).

## 🔴 यह क्यों बना? (Hindi)
Service धीरे-धीरे RAM खाती है और Kubernetes उसे OOMKilled कर देता है। अंदाज़े से कुछ नहीं होता। Profiling बताता है कि कौन सी line या data structure बढ़ रही है, ताकि आप leak (बढ़ता cache) या waste (generator की जगह list, `__slots__` की जगह normal class) ठीक कर सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → tracemalloc.start() hooks Python's memory allocator
Step 2 → Every allocation is recorded with its traceback (file:line)
Step 3 → take_snapshot() freezes the current picture
Step 4 → Take a second snapshot after the suspicious code runs
Step 5 → snapshot2.compare_to(snapshot1, "lineno") shows who grew
Step 6 → Fix the top line, measure again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → tracemalloc.start() Python के memory allocator में hook लगाता है
Step 2 → हर allocation traceback (file:line) के साथ record होती है
Step 3 → take_snapshot() उस समय की तस्वीर फ्रीज़ करता है
Step 4 → संदिग्ध code चलाने के बाद दूसरा snapshot लें
Step 5 → snapshot2.compare_to(snapshot1, "lineno") बताता है कौन बढ़ा
Step 6 → सबसे ऊपर वाली line ठीक करें और फिर नापें
```

---

## 🟡 Real World Example
A Razorpay reconciliation job builds a list of 5 million transaction dicts and crashes with MemoryError. Snapshot comparison points to the `rows.append(...)` line; switching to a generator that yields rows one by one drops peak memory from GBs to MBs. A RAG service finds its embedding cache never evicts entries and adds an LRU limit.

## 🟡 Real Example Hindi mein
Razorpay का reconciliation job 50 लाख transaction dicts की list बनाता है और MemoryError से crash होता है। Snapshot comparison `rows.append(...)` वाली line दिखाता है; rows एक-एक करके yield करने वाला generator लगाने से peak memory GBs से MBs में आ जाती है। एक RAG service में पता चलता है कि embedding cache कभी entries हटाता ही नहीं, तो LRU limit जोड़ी जाती है।

---

## 💻 Code Example — Basic
```python
# Basic memory measurement - every line commented
import sys  # for getsizeof
import tracemalloc  # allocation tracker
from typing import List  # type hints

print(sys.getsizeof(1), sys.getsizeof("a"), sys.getsizeof([]), sys.getsizeof([1, 2, 3]), sys.getsizeof({}))  # shallow sizes in bytes
# Output: 28 42 56 88 64   # CPython 3.13, 64-bit; other versions/platforms differ

tracemalloc.start()  # begin tracking allocations
data: List[int] = [i for i in range(100_000)]  # allocate 100k ints in a list
current, peak = tracemalloc.get_traced_memory()  # bytes now, and the highest so far
print(current > 800_000, peak >= current)  # a list of 100k ints is several MB
# Output: True True
tracemalloc.stop()  # stop tracking and free its own bookkeeping
print(tracemalloc.is_tracing())  # confirm it is off
# Output: False

# getsizeof is SHALLOW: it does not include the items inside
nested: List[List[int]] = [[1] * 1000 for _ in range(10)]  # ten lists of 1000 items
print(sys.getsizeof(nested) < 200)  # only the outer list container is counted
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: snapshot diff to find growth, plus __slots__ and generator comparisons
import tracemalloc  # allocation tracker
from typing import Callable, List, Type  # type hints


def leaky(store: List[bytes]) -> None:  # simulates a leak: keeps 1000 KB alive
    for _ in range(1000):  # 1000 times
        store.append(bytes(1024))  # allocate a fresh 1 KB object


tracemalloc.start(5)  # keep up to 5 frames per traceback
store: List[bytes] = []  # the "cache" that grows
before = tracemalloc.take_snapshot()  # snapshot 1
leaky(store)  # the suspicious code
after = tracemalloc.take_snapshot()  # snapshot 2
top = after.compare_to(before, "lineno")[0]  # biggest growth first
frame = top.traceback[0]  # file and line responsible
print(f"+{top.size_diff // 1024} KiB in {top.count_diff} blocks at line {frame.lineno}")  # report
# Output: +1040 KiB in 1001 blocks at line 8   (line 8 = the append line when this snippet is saved as a file; sizes may differ slightly)
tracemalloc.stop()  # stop tracking


class Plain:  # normal class: each instance has a __dict__
    def __init__(self) -> None:  # constructor
        self.x: int = 1  # attribute x
        self.y: int = 2  # attribute y


class Slotted:  # __slots__ class: no per-instance __dict__
    __slots__ = ("x", "y")  # fixed attribute names

    def __init__(self) -> None:  # constructor
        self.x: int = 1  # attribute x
        self.y: int = 2  # attribute y


def measure(factory: Callable[[], object]) -> int:  # memory held by 10k instances
    tracemalloc.start()  # start tracking
    items: List[object] = [factory() for _ in range(10_000)]  # keep them alive
    current, _ = tracemalloc.get_traced_memory()  # bytes currently allocated
    tracemalloc.stop()  # stop tracking
    del items  # release the objects
    return current  # return the byte count


plain, slotted = measure(Plain), measure(Slotted)  # measure both classes
print(plain > slotted, round(plain / slotted, 1))  # slots use less memory
# Output: True 1.7   (ratio varies by version)

# Generator vs list: peak memory
tracemalloc.start()  # start tracking
total: int = sum(i for i in range(200_000))  # generator: one number at a time
_, peak_gen = tracemalloc.get_traced_memory()  # peak for the generator
tracemalloc.stop()  # stop
tracemalloc.start()  # start again
total = sum([i for i in range(200_000)])  # list: all numbers at once
_, peak_list = tracemalloc.get_traced_memory()  # peak for the list
tracemalloc.stop()  # stop
print(peak_gen < 10_000, peak_list > 1_000_000)  # generator is tiny, list is MBs
# Output: True True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: built in
import tracemalloc, sys
tracemalloc.start()
cur, peak = tracemalloc.get_traced_memory()   # bytes
print(sys.getsizeof([1, 2, 3]))               # shallow size of one object
```

```javascript
// Node.js
console.log(process.memoryUsage());           // { rss, heapTotal, heapUsed, external, ... }
const v8 = require("v8");
v8.writeHeapSnapshot();                        // open the file in Chrome DevTools
// Chrome DevTools "Memory" tab compares snapshots visually
```

Key differences: Node gives process-level numbers plus heap snapshots viewed in DevTools. Python gives line-level allocation tracking in the standard library. Python's `sys.getsizeof` is shallow, while a JS heap snapshot shows retained size. For deep size in Python use third-party tools like `pympler` or `memory_profiler` (`@profile` shows per-line usage).

---

## 🟠 FastAPI Connection
Add a debug endpoint that reports traced memory (enable tracing at startup only in staging because tracing slows the app by roughly 2x or more). Compare two snapshots between requests to find leaking caches.

```python
import tracemalloc  # allocation tracker
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client
from typing import Dict  # type hints

app: FastAPI = FastAPI()  # create app
CACHE: Dict[int, bytes] = {}  # a global cache that never evicts (the leak)

@app.get("/fill/{n}")  # grows the cache
def fill(n: int) -> Dict[str, int]:
    for i in range(n):  # add n entries
        CACHE[i] = b"x" * 1024  # 1 KB each
    return {"items": len(CACHE)}  # report size

@app.get("/debug/memory")  # admin only in real life
def mem() -> Dict[str, int]:
    if not tracemalloc.is_tracing():  # lazily start
        tracemalloc.start()
    cur, peak = tracemalloc.get_traced_memory()  # numbers in bytes
    return {"current_kb": cur // 1024, "peak_kb": peak // 1024}  # JSON

c = TestClient(app)
print(c.get("/debug/memory").json())
# Output: {'current_kb': 0, 'peak_kb': 0}   (tracing just started)
print(c.get("/fill/100").json())
# Output: {'items': 100}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting `sys.getsizeof` for containers
```python
# Wrong - only the outer list is counted
big = [[0] * 10_000 for _ in range(100)]
print(sys.getsizeof(big))        # ~920 bytes, looks tiny!

# Correct - measure real allocation
tracemalloc.start(); big = [[0] * 10_000 for _ in range(100)]
print(tracemalloc.get_traced_memory()[0])   # ~8 MB
```

❌ Mistake 2: Profiling in production with `tracemalloc` always on
```python
# Wrong - slows every allocation and adds its own memory overhead
tracemalloc.start(25)      # 25 frames = heavy

# Correct - start(1) or sample only on a staging box / for a short window
```

❌ Mistake 3: Measuring RSS from `top` and calling it a leak
```python
# Wrong: RSS may stay high because the allocator keeps freed pages for reuse
# Correct: compare tracemalloc snapshots over time; steady growth of Python blocks = leak
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import sys
big = [list(range(100_000)) for _ in range(3)]
print(sys.getsizeof(big) < 200)
print(sys.getsizeof([]) < sys.getsizeof([1]))
l = []
sizes = []
for i in range(6):
    l.append(i)
    sizes.append(sys.getsizeof(l))
print(sizes)
```

**Answer**:
```
True
True
[88, 88, 88, 88, 120, 120]
```
`getsizeof` is shallow, so the three big inner lists are not counted: `big` itself is under 200 bytes. Lists over-allocate as they grow, so the size jumps in steps (exact numbers depend on Python version).

---

## ⚫ Interview Questions + Answers

Q1: How do you find a memory leak in a Python service?
A1: Start `tracemalloc`, take a snapshot, run traffic, take another, and call `compare_to(old, "lineno")`. The top growing line is usually a cache, a list that is only appended, or a global registry.

Q2: Difference between `sys.getsizeof` and `tracemalloc`?
A2: `getsizeof` returns the shallow size of one object. `tracemalloc` tracks all allocations made by Python with their source lines and gives current/peak totals.

Q3: What is `memory_profiler`?
A3: A third-party package: decorate a function with `@profile` and run `python -m memory_profiler file.py` for per-line memory usage.

Q4: Why does memory not return to the OS after `del`?
A4: Python's allocator (pymalloc) keeps freed arenas and the OS may keep pages resident. The memory is reusable by Python even if RSS looks high.

Q5: How can you cut memory use of many small objects?
A5: Use `__slots__`, dataclasses with `slots=True`, tuples or arrays instead of dicts, generators instead of lists, and `array`/NumPy for numeric data.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- RAM keeps growing or you see OOMKilled
- You compare two implementations (list vs generator, class vs slots)
- You need line-level attribution of allocations

❌ Avoid when:
- Always-on in production (use short windows or sampling tools)
- You need CPU time (use cProfile instead)
- You trust `getsizeof` as a deep size

---

## 📊 Visual Diagram

```
 start() ─► snapshot A ─► [ run suspicious code ] ─► snapshot B
                                                        │
                                  B.compare_to(A) ◄─────┘
                                        │
                     file.py:8  +1040 KiB  +1001 blocks   <- fix this line
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Snapshot | Frozen view of allocations | allocations की तस्वीर |
| Peak | Highest memory seen | सबसे ज़्यादा memory उपयोग |
| Shallow size | Object only, not what it references | सिर्फ object का size |
| Leak | Memory kept alive but unused | बेकार रुकी हुई memory |
| RSS | Memory the OS gave the process | OS द्वारा दी गई memory |
| `__slots__` | Fixed attributes, no `__dict__` | fixed attributes, कम memory |

---

## ⚡ 3-Line Summary
English: Use `tracemalloc` snapshots to see which line grows, and `sys.getsizeof` only for shallow sizes. Compare list vs generator and class vs `__slots__` with real numbers. Profile briefly, not forever, in production.
Hindi: कौन सी line बढ़ रही है यह देखने के लिए `tracemalloc` snapshots इस्तेमाल करें और `sys.getsizeof` सिर्फ shallow size के लिए। List बनाम generator और class बनाम `__slots__` की असली numbers से तुलना करें। Production में थोड़ी देर ही profile करें।

---

## ➡️ Next Topic
**160. Weak References** — hold an object without keeping it alive (caches, parent links).
