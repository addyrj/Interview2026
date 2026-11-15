---

# 404. Memory Profiling
# हिंदी में: Memory Profiling (RAM कौन खा रहा है)

---

## 🔵 Simple Definition (English)
Memory profiling measures how much RAM your Python code uses and WHICH lines allocate it. The main tools are `sys.getsizeof` (size of one object), `tracemalloc` (built in, tracks allocations) and `memory_profiler` (line-by-line RSS, third party).

## 🔵 सरल परिभाषा (Hindi)
Memory profiling नापता है कि आपका Python code कितनी RAM लेता है और कौन सी lines उसे allocate करती हैं। मुख्य tools: `sys.getsizeof` (एक object का size), `tracemalloc` (built-in, allocations track करता है) और `memory_profiler` (line-by-line RSS, third party)।

---

## 🔴 Problem it Solves
Servers get killed by the OS (OOM kill) or pods restart in Kubernetes because memory keeps growing. Reasons: loading a whole file into a list, a global cache that never expires, or objects kept alive by references. Python's garbage collector cannot free what you still reference. You need tools to see where memory goes.

## 🔴 यह क्यों बना? (Hindi)
Memory लगातार बढ़ने से server को OS kill कर देता है (OOM) या Kubernetes pod restart होता है। कारण: पूरी file list में load करना, कभी expire न होने वाला global cache, या references की वजह से जिंदा objects। जब तक आप reference पकड़े हैं, garbage collector कुछ free नहीं करेगा। Memory कहाँ जा रही है यह देखने के लिए tools चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sys.getsizeof(obj)      : shallow size of ONE object (no children)
Step 2 → tracemalloc.start()     : Python records every allocation + traceback
Step 3 → take_snapshot()         : copy of "who allocated what" at that moment
Step 4 → compare_to(before)      : diff two snapshots -> the leaking line
Step 5 → memory_profiler         : samples process RSS per line / over time
Step 6 → Fix: generators, chunks, __slots__, bounded caches; measure again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sys.getsizeof(obj)      : सिर्फ एक object का shallow size (अंदर के objects नहीं)
Step 2 → tracemalloc.start()     : Python हर allocation और traceback record करता है
Step 3 → take_snapshot()         : उस पल की "किसने क्या allocate किया" की copy
Step 4 → compare_to(before)      : दो snapshots का फर्क -> leak करने वाली line
Step 5 → memory_profiler         : process की RSS line-by-line नापता है
Step 6 → सुधार: generators, chunks, __slots__, bounded cache; फिर से measure करें
```

---

## 🟡 Real World Example
A FastAPI AI service keeps `_cache[user_id] = embeddings` in a global dict. After a day, memory goes from 300 MB to 4 GB and the pod is OOM-killed. A tracemalloc snapshot diff points at the exact `_cache[...] =` line. The fix is an LRU cache with a max size. Another case: a Zomato export loads 5 million rows with `list(csv_reader)` (1.5 GB); switching to a generator keeps memory flat.

## 🟡 Real Example Hindi mein
एक FastAPI AI service global dict में `_cache[user_id] = embeddings` रखती है। एक दिन में memory 300 MB से 4 GB हो जाती है और pod OOM-kill हो जाता है। tracemalloc snapshot diff ठीक उसी `_cache[...] =` line को दिखाता है। समाधान: max size वाला LRU cache। दूसरा case: Zomato export में `list(csv_reader)` से 50 लाख rows (1.5 GB) load होती थीं; generator लगाने से memory स्थिर रही।

---

## 💻 Code Example — Basic
```python
# Basic memory measurement - every line commented
import sys  # for getsizeof
import tracemalloc  # built-in allocation tracker
from typing import List  # type hints


def make_list(n: int) -> List[int]:  # builds a list of n numbers
    return [i * 2 for i in range(n)]  # one list, n items


tracemalloc.start()  # begin tracking allocations
data: List[int] = make_list(100_000)  # allocate ~3.8 MB
cur, peak = tracemalloc.get_traced_memory()  # (current, peak) in bytes
print(f"current={cur/1024/1024:.1f}MB peak={peak/1024/1024:.1f}MB")  # show in MB
# Output: current=3.8MB peak=3.8MB   (about; depends on Python version)

snap = tracemalloc.take_snapshot()  # capture who allocated what
for st in snap.statistics("lineno")[:1]:  # biggest allocation site
    print(st.traceback[0].lineno, st.count, round(st.size / 1024 / 1024, 1))  # line, blocks, MB
# Output: 5 99872 3.8     (line number = the list comprehension line in your file)
tracemalloc.stop()  # stop tracking (tracking itself costs memory/time)

# getsizeof is SHALLOW and tiny for lazy objects
print(sys.getsizeof([]), sys.getsizeof([1]))  # empty list vs one item (Python 3.13, 64-bit)
print(sys.getsizeof(range(10**7)))  # range stores 3 numbers only
print(sys.getsizeof(i for i in range(10**7)))  # a generator is tiny
print(sys.getsizeof(list(range(100_000))))  # real list = 8 bytes per pointer
# Output:
# 56 64
# 48
# 192
# 800056
# (exact bytes differ between Python versions)
```

## 💻 Code Example — Advanced
```python
# Production style: find a leak with snapshot diff + compare eager vs lazy
# Needs: pip install memory_profiler
import tracemalloc  # allocation tracker
from typing import Dict, List  # type hints
from memory_profiler import memory_usage  # process memory sampler

_cache: Dict[int, bytes] = {}  # global dict that never shrinks = a leak


def leaky_handler(i: int) -> None:  # simulates a request handler
    _cache[i] = b"x" * 10_000  # stores 10 KB per request, forever


def eager(n: int) -> int:  # builds the full list first
    return sum([i for i in range(n)])  # list of n ints in RAM


def lazy(n: int) -> int:  # generator expression
    return sum(i for i in range(n))  # one value at a time


def main() -> None:  # main() because memory_usage may spawn a process
    tracemalloc.start()  # start tracking
    before = tracemalloc.take_snapshot()  # baseline snapshot
    for i in range(1000):  # 1000 "requests"
        leaky_handler(i)  # leak 10 KB each
    after = tracemalloc.take_snapshot()  # snapshot after the traffic
    top = after.compare_to(before, "lineno")[0]  # biggest growth first
    print(f"{top.size_diff/1024/1024:.1f}MB new, {top.count_diff} blocks, line {top.traceback[0].lineno}")  # leak site
    # Output: 9.6MB new, 1001 blocks, line 8   (line = the `_cache[i] = ...` line)
    tracemalloc.stop()  # stop tracking

    for fn in (eager, lazy):  # compare the two strategies
        usage: List[float] = memory_usage((fn, (3_000_000,)), interval=0.01)  # MiB samples
        print(fn.__name__, "peak increase MiB:", round(max(usage) - usage[0]))  # extra RAM used
    # Output (varies by machine):
    # eager peak increase MiB: 117
    # lazy peak increase MiB: 0


if __name__ == "__main__":  # REQUIRED guard: on macOS/Windows memory_usage(func) starts a process
    main()  # run
```
Verified: both blocks ran on Python 3.13.3. Without the `if __name__ == "__main__":` guard, `memory_usage((func, args))` crashed with `RuntimeError: An attempt has been made to start a new process...` on macOS (spawn start method).

Line-by-line with the decorator (`from memory_profiler import profile`):
```python
from memory_profiler import profile  # decorator

@profile  # prints a per-line table when f() ends
def f():
    a = [1] * 10**6  # 8 MB
    b = [2] * (2 * 10**7)  # 160 MB
    del b  # freed
    return a

f()
# Output (MiB, machine dependent):
# Line #    Mem usage    Increment  Occurrences   Line Contents
#      5     34.2 MiB      7.7 MiB           1       a = [1] * 10**6
#      6    186.8 MiB    152.6 MiB           1       b = [2] * (2 * 10**7)
#      7     34.2 MiB   -152.6 MiB           1       del b
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import tracemalloc
tracemalloc.start()
data = [0] * 1_000_000
print(tracemalloc.get_traced_memory())   # (current, peak) bytes
```

```javascript
// JavaScript (Node.js)
const data = new Array(1_000_000).fill(0);
console.log(process.memoryUsage());      // { rss, heapTotal, heapUsed, external }
// Deep analysis: node --inspect + Chrome DevTools "Memory" tab -> heap snapshot,
// or require("v8").writeHeapSnapshot()
```

Key differences: Node has a managed V8 heap (`heapUsed`), and heap snapshots are opened in DevTools. Python's `tracemalloc` shows allocation tracebacks directly in code, while `memory_profiler` and `psutil` show whole-process RSS (which may not shrink even after objects are freed, because the allocator keeps arenas).

---

## 🟠 FastAPI Connection
Expose a protected debug endpoint (or log periodically) with `tracemalloc` numbers so you can watch growth between deploys. Start tracing only in staging or behind a flag: it slows code by roughly 2x and adds its own memory.

```python
# FastAPI: memory debug endpoint (needs: pip install fastapi httpx)
import tracemalloc  # allocation tracker
from typing import Dict, List  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app
_store: List[bytearray] = []  # simulated leak


@app.post("/upload")  # each call keeps 100 KB
def upload() -> Dict[str, int]:
    _store.append(bytearray(100_000))  # never freed
    return {"n": len(_store)}  # how many we hold


@app.get("/debug/mem")  # protect with auth in real life
def mem() -> Dict[str, object]:
    cur, peak = tracemalloc.get_traced_memory()  # bytes
    return {"current_kb": cur // 1024, "tracing": tracemalloc.is_tracing()}  # JSON


tracemalloc.start()  # normally behind an env flag
client = TestClient(app)  # test client
for _ in range(3):  # three uploads
    client.post("/upload")  # leak 300 KB
print(client.get("/debug/mem").json())  # Output: {'current_kb': 2905, 'tracing': True}
# current_kb is bigger than 300 because the app/test client also allocate; value varies.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `sys.getsizeof` for nested objects
```python
# Wrong - shallow size only (verified, Python 3.13)
big = [[0] * 1000 for _ in range(1000)]
print(sys.getsizeof(big))                   # 8856  (just the outer list pointers!)

# Right - add the children (or use pympler.asizeof / tracemalloc)
print(sys.getsizeof(big) + sum(sys.getsizeof(r) for r in big))   # 8064856 (~8 MB)
```

❌ Mistake 2: Expecting RSS to drop after `del`
```python
# Wrong - assuming "del" returns memory to the OS immediately
# Right - Python reuses freed memory internally; RSS may stay high.
#         Use tracemalloc (live objects) to judge leaks, not top/RSS alone.
```

❌ Mistake 3: Leaving tracemalloc on in production
```python
# Wrong - tracemalloc.start() always on in prod (slower, extra RAM)
# Right - enable with an env flag or only while investigating
```

❌ Mistake 4: Forgetting the main guard with memory_profiler
```python
# Wrong - memory_usage((func, args)) at module top level (crashes on macOS/Windows)
# Right - wrap in main() and use: if __name__ == "__main__": main()
```

---

## 🧠 Tricky Interview Question

**Q**: How many bytes does this list take, and why is it so small?

```python
import sys
big = [[0] * 1000 for _ in range(1000)]
print(sys.getsizeof(big))
print(sys.getsizeof(big) + sum(sys.getsizeof(r) for r in big))
a = []
sizes = set()
for i in range(20):
    a.append(i)
    sizes.add(sys.getsizeof(a))
print(sorted(sizes))
```

**Answer** (Python 3.13, 64-bit):
```
8856
8064856
[88, 120, 184, 248]
```
`getsizeof` counts only the outer list: 1000 pointers (8 bytes each) plus header, not the 1000 inner lists (about 8 MB). The third line shows over-allocation: a list grows in jumps, not one slot at a time, so appends are amortized O(1) and the size takes only a few distinct values. Exact numbers differ across Python versions.

---

## ⚫ Interview Questions + Answers

Q1: How do you find a memory leak in Python?
A1: Take `tracemalloc` snapshots before and after a workload and call `after.compare_to(before, "lineno")`. The top entries show lines whose allocations keep growing. Then look for global dicts/lists, caches without limits, lingering closures or circular references with `__del__`.

Q2: `sys.getsizeof` vs `tracemalloc` vs `memory_profiler`?
A2: `getsizeof` = size of one object (shallow). `tracemalloc` = Python allocations with tracebacks (built in). `memory_profiler` = process RSS per line or over time (third party; it samples with psutil, so results are approximate).

Q3: Does garbage collection fix leaks?
A3: Not if you still hold a reference. A global dict that keeps objects alive is a logical leak; the GC only frees unreachable objects (and cycles).

Q4: How do you reduce memory for large data?
A4: Generators and chunked reading, `__slots__` for many small objects, `array`/NumPy for numbers, smaller dtypes in pandas, bounded caches (`functools.lru_cache(maxsize=...)`), and streaming responses.

Q5: Why can memory stay high after freeing objects?
A5: CPython's allocator keeps freed arenas/pools for reuse, and the OS may not take pages back. Live-object accounting (tracemalloc) shows the true picture.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Memory grows over time (leak suspicion)
- A job gets OOM-killed
- You are choosing between a list and a generator for big data

❌ Avoid when:
- You only care about speed (use cProfile)
- You need production, always-on monitoring (use metrics like Prometheus / psutil RSS, not tracemalloc)
- The object is tiny and not repeated

---

## 📊 Visual Diagram

```
 snapshot A ----> run workload ----> snapshot B
      \                                 /
       \--------- compare_to ----------/
                       |
                       v
     +4.2 MB   cache.py:57   _cache[user_id] = embeddings   <-- the leak
     +0.1 MB   utils.py:12   ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RSS | Physical RAM used by the process | process द्वारा उपयोग की गई असली RAM |
| Allocation | Request for memory by the program | memory की माँग |
| Snapshot | Saved copy of allocation info | allocation जानकारी की सेव की हुई copy |
| Leak | Memory kept alive by mistake | गलती से जिंदा रखी memory |
| Shallow size | Object only, not its children | सिर्फ object, उसके अंदर वाले नहीं |
| OOM | Out Of Memory kill by the OS | OS द्वारा memory खत्म होने पर process बंद |

---

## ⚡ 3-Line Summary
English: Use `sys.getsizeof` for one object, `tracemalloc` snapshot diffs to find leaking lines, and `memory_profiler` for line-by-line process memory. Most leaks are unbounded globals or caches. Prefer generators, chunks and bounded caches.
Hindi: एक object के लिए `sys.getsizeof`, leak वाली line खोजने के लिए `tracemalloc` snapshot diff और line-by-line process memory के लिए `memory_profiler` लें। ज़्यादातर leaks बिना सीमा वाले globals या caches होते हैं। Generators, chunks और bounded cache अपनाएँ।

---

## ➡️ Next Topic
**405. Optimizing Loops** — after you find the hot loop, make it faster: builtins, comprehensions, hoisting, sets and vectorization.
