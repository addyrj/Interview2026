---

# 155. Memory Management in Python
# हिंदी में: Python में Memory Management

---

## 🔵 Simple Definition (English)
In CPython, every value is an object living in a private heap managed by the interpreter. Names are only references (labels) that point to those objects. Python allocates memory automatically when you create an object and frees it automatically when nobody uses it any more, using reference counting plus a cyclic garbage collector.

## 🔵 सरल परिभाषा (Hindi)
CPython में हर value एक object है जो interpreter द्वारा संभाले जाने वाले private heap में रहता है। नाम सिर्फ references (लेबल) हैं जो उन objects की ओर इशारा करते हैं। Object बनाते समय Python अपने आप memory देता है और जब कोई उसका उपयोग नहीं करता तो reference counting और cyclic garbage collector की मदद से अपने आप मुक्त कर देता है।

---

## 🔴 Problem it Solves
In C you call `malloc` and `free` yourself, and forgetting `free` leaks memory while freeing twice crashes the program. Python removes this whole class of bugs for ordinary code. You still must understand it: lists that grow forever, caches without limits, large intermediate lists and shared mutable objects cause real memory problems in production servers.

## 🔴 यह क्यों बना? (Hindi)
C में आप खुद `malloc` और `free` करते हैं; `free` भूलने पर memory leak होती है और दो बार free करने पर program crash हो जाता है। Python सामान्य code में यह पूरी तरह की गलतियां हटा देता है। फिर भी समझना जरूरी है: हमेशा बढ़ती lists, बिना limit वाले caches, बड़ी intermediate lists और shared mutable objects production servers में असली memory समस्याएं पैदा करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → x = [1, 2, 3]  : Python asks its allocator for memory and builds a list object
Step 2 → Small objects (<= 512 bytes) come from pymalloc: arenas -> pools -> blocks
Step 3 → Bigger objects go to the system allocator (malloc)
Step 4 → The name x stores a REFERENCE (pointer); y = x copies only the pointer
Step 5 → Each object keeps a reference count (how many references point to it)
Step 6 → When the count reaches 0, the object is freed immediately
Step 7 → Objects in reference cycles (a -> b -> a) never reach 0; the cyclic GC finds them
Step 8 → Freed memory returns to pymalloc's pools first; the OS gets it back only when a whole arena is empty

Optimizations: small ints (-5..256) cached, string interning, list over-allocation (grows in jumps)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → x = [1, 2, 3]  : Python allocator से memory मांगकर list object बनाता है
Step 2 → छोटे objects (<= 512 bytes) pymalloc से मिलते हैं: arenas -> pools -> blocks
Step 3 → बड़े objects system allocator (malloc) से आते हैं
Step 4 → नाम x एक REFERENCE (pointer) रखता है; y = x सिर्फ pointer copy करता है
Step 5 → हर object एक reference count रखता है (कितने references उसकी ओर हैं)
Step 6 → Count 0 होते ही object तुरंत free हो जाता है
Step 7 → Reference cycles (a -> b -> a) वाले objects का count 0 नहीं होता; cyclic GC उन्हें ढूंढता है
Step 8 → Free हुई memory पहले pymalloc के pools में लौटती है; OS को तब मिलती है जब पूरा arena खाली हो

Optimizations: छोटे ints (-5..256) cached, string interning, list की over-allocation (jumps में बढ़ती है)
```

---

## 🟡 Real World Example
A FastAPI analytics service loads a CSV of 1 million rows. Building `[row_to_dict(r) for r in rows]` creates a million dicts at once and the server's memory spikes. Switching to a generator (process row by row) keeps memory almost flat. Another classic production bug: a global `requests_log = []` list that appends every request and is never trimmed, so memory grows until the pod is killed (OOMKilled) in Kubernetes.

## 🟡 Real Example Hindi mein
FastAPI analytics service 10 लाख rows की CSV load करती है। `[row_to_dict(r) for r in rows]` एक साथ दस लाख dicts बनाता है और server की memory ऊपर उछल जाती है। Generator (row by row processing) से memory लगभग स्थिर रहती है। Production का एक क्लासिक bug: global `requests_log = []` list जिसमें हर request append होती है और कभी साफ नहीं होती, इसलिए memory बढ़ती रहती है जब तक Kubernetes में pod kill (OOMKilled) न हो जाए।

---

## 💻 Code Example — Basic
```python
# Memory management basics: everything is an object on the heap; names are references
import sys                                                # getsizeof, getrefcount


a: list[int] = [1, 2, 3]                                  # list object created on the private heap
b = a                                                     # second name -> SAME object, no copy
print(a is b, id(a) == id(b))                             # True True
b.append(4)                                               # change through one name
print(a)                                                  # [1, 2, 3, 4] seen via both names

print(sys.getsizeof(0), sys.getsizeof(10**30))            # int size grows with value (bytes)
print(sys.getsizeof([]), sys.getsizeof([1, 2, 3]))        # empty list vs 3 items (over-allocation)

x, y = 256, 256                                           # small ints are cached singletons
print(x is y)                                             # True (CPython detail)
s1 = "hello"
s2 = "hel" + "lo"                                         # constant folded at compile time
print(s1 is s2)                                           # True (interned, implementation detail)

lst: list[int] = []
sizes = set()                                             # collect distinct sizes while appending
for i in range(20):
    lst.append(i)
    sizes.add(sys.getsizeof(lst))
print(sorted(sizes))                                      # list grows in jumps, not one slot at a time

# Output (byte sizes are from CPython 3.13 on 64-bit macOS; other versions/platforms differ):
# True True
# [1, 2, 3, 4]
# 28 40
# 56 88
# True
# True
# [88, 120, 184, 248]
```

## 💻 Code Example — Advanced
```python
# Production style: deep size helper, list vs generator memory, string interning
import sys                                                # getsizeof, intern
import tracemalloc                                        # measure Python allocations
from typing import Any                                    # any type


def deep_size(obj: Any, seen: set[int] | None = None) -> int:
    """Approximate total bytes of obj and everything it references."""
    seen = set() if seen is None else seen                # ids already counted
    if id(obj) in seen:                                   # shared object: count once
        return 0
    seen.add(id(obj))
    size: int = sys.getsizeof(obj)                        # the object itself
    if isinstance(obj, dict):                             # add keys and values
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):  # add items
        size += sum(deep_size(i, seen) for i in obj)
    return size


order: dict[str, Any] = {"id": 101, "items": ["pizza", "coke"], "tags": ("hot", "new")}
print("shallow:", sys.getsizeof(order), "deep:", deep_size(order) > sys.getsizeof(order))


def peak_mb(func: Any) -> float:
    tracemalloc.start()                                   # begin tracking
    func()                                                # run the code under test
    _cur, peak = tracemalloc.get_traced_memory()          # peak bytes
    tracemalloc.stop()
    return peak / 1024 / 1024


def with_list() -> int:
    return sum([i * i for i in range(1_000_000)])         # builds the whole list first


def with_generator() -> int:
    return sum(i * i for i in range(1_000_000))           # one item at a time


print("list peak > generator peak:", peak_mb(with_list) > 50 * peak_mb(with_generator))

a = "".join(["pay", "ment"])                              # built at runtime: new string object
b = "".join(["pay", "ment"])
print(a == b, a is b)                                     # equal, different objects
print(sys.intern(a) is sys.intern(b))                     # interned: one shared object

# Output:
# shallow: 184 deep: True
# list peak > generator peak: True
# True False
# True
```
Both blocks were run on Python 3.13.3 (macOS, 64-bit). Byte sizes like `184` are version and platform dependent; `is` results on small ints and strings are CPython implementation details, never rely on them in real logic.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (CPython) | JavaScript (V8) |
|---------|------------------|-----------------|
| Main strategy | reference counting + cyclic GC | tracing GC (mark and sweep, generational) |
| Freed when | count hits 0, immediately | at some later GC cycle |
| Deterministic cleanup | yes (`__del__`, `with`) | no (`FinalizationRegistry` is not guaranteed) |
| Assignment `b = a` | copies reference | copies reference (objects) |
| Inspect memory | `sys.getsizeof`, `tracemalloc` | `process.memoryUsage()`, DevTools heap snapshot |

```python
# Python way
a = [1, 2, 3]                  # one list object
b = a                         # two names, ONE object
b.append(4)
print(a)                      # [1, 2, 3, 4]
```
```javascript
// JavaScript way
const a = [1, 2, 3];          // one array object
const b = a;                  // two names, ONE object
b.push(4);
console.log(a);               // [1, 2, 3, 4]
```

Key difference: both languages share objects by reference, so mutation is visible through every name. The difference is cleanup timing: CPython frees an object the instant its count reaches zero, while V8 waits for its garbage collector.

---

## 🟠 FastAPI Connection
A FastAPI process is long-lived, so any module-level container that only grows is a memory leak. Use bounded structures (`deque(maxlen=...)`, `functools.lru_cache(maxsize=...)`, TTL caches) for in-process state, and stream big responses instead of building them whole.

```python
# FastAPI example — unbounded list vs bounded deque
from collections import deque                               # bounded queue
from fastapi import FastAPI                                 # FastAPI app
from fastapi.testclient import TestClient                   # in-process client

app: FastAPI = FastAPI()
LEAKY: list[str] = []                                       # grows forever: memory leak
RECENT: deque[str] = deque(maxlen=3)                        # keeps only the last 3


@app.post("/log/{msg}")
def log(msg: str) -> dict[str, int]:
    LEAKY.append(msg)                                       # BAD in production
    RECENT.append(msg)                                      # GOOD: old entries drop automatically
    return {"leaky": len(LEAKY), "bounded": len(RECENT)}


client = TestClient(app)
for m in "abcde":                                           # five requests
    r = client.post(f"/log/{m}")
print(r.json(), list(RECENT))
# {'leaky': 5, 'bounded': 3} ['c', 'd', 'e']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `b = a` copies a list
✅ Correct: use `a.copy()` or `copy.deepcopy(a)` when you need an independent object

```python
import copy
n = [[1], [2]]
sh = n.copy()                      # shallow copy: inner lists are shared
dp = copy.deepcopy(n)              # deep copy: fully independent
n[0].append(9)
print(sh, dp)                      # [[1, 9], [2]] [[1], [2]]
```

❌ Mistake 2: Mutable default arguments
✅ Correct: use `None` and create the object inside

```python
def add(x, bucket=[]):             # Wrong: ONE list is created at def time and shared by all calls
    bucket.append(x)
    return bucket
print(add(1), add(2))              # [1, 2] [1, 2]  <- same list printed twice
def add2(x, bucket=None):          # Right
    bucket = [] if bucket is None else bucket
    bucket.append(x)
    return bucket
print(add2(1), add2(2))            # [1] [2]
```

❌ Mistake 3: Global caches or logs with no size limit
✅ Correct: bound them (`deque(maxlen=N)`, `lru_cache(maxsize=N)`)

```python
cache: dict[str, bytes] = {}       # Wrong: grows with every unique key until the process is killed
# Right: from functools import lru_cache; @lru_cache(maxsize=1024)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
a = [1]
b = a
b += [2]
print(a, b)

c = [1]
d = c
d = d + [2]
print(c, d)
```
Answer: `[1, 2] [1, 2]` then `[1] [1, 2]`. For lists, `+=` calls `__iadd__`, which extends the SAME object in place, so `a` also changes. `d = d + [2]` builds a NEW list and rebinds `d`, so `c` is unchanged. For immutable types such as ints, tuples and strings `+=` always creates a new object.

---

## ⚫ Interview Questions + Answers

Q1: How does Python manage memory?
A1: A private heap holds all objects. The allocator (pymalloc for objects up to 512 bytes, malloc otherwise) provides memory. Objects are freed by reference counting when the count hits zero, and a cyclic garbage collector clears reference cycles.

Q2: Why does Python not return memory to the OS immediately after `del`?
A2: Freed blocks go back to pymalloc's pools for reuse. Only completely empty arenas are released to the OS, and fragmentation can keep partially used arenas alive. So `top` / RSS may stay high even after you delete objects.

Q3: What is the difference between `sys.getsizeof` and the real memory used?
A3: `getsizeof` returns only the object's own size, not what it references. A list of 1000 strings reports just the pointer array. Use a recursive helper, `pympler.asizeof`, or `tracemalloc` for the full picture.

Q4: Why is a list comprehension inside `sum()` worse than a generator?
A4: The comprehension builds the whole list first (O(n) memory). A generator expression produces one value at a time (O(1) memory). On a million items, the list version peaked at many tens of MiB while the generator stayed tiny in my run.

Q5: Is the small-int cache or string interning part of the Python language?
A5: No, they are CPython implementation details. Always compare values with `==`; use `is` only for `None`, `True`, `False` and sentinels.

---

## 🔷 When to Use + When Not to Use
✅ Think about memory management when:
- Processing large files or datasets (stream, use generators)
- Writing long-running servers, workers or caches
- Creating millions of small objects (consider `__slots__`)

❌ Do not over-optimize when:
- Scripts run briefly with small data
- You have no measurement; always profile first (`tracemalloc`)
- You would sacrifice readability for a tiny saving

---

## 📊 Visual Diagram
```
 names (stack/frames)          private heap (objects)
 ┌───────┐                    ┌──────────────────────────┐
 │ a ────┼───────────────────►│ list [1,2,3,4]  refcnt=2 │
 │ b ────┼───────────────────►│                          │
 └───────┘                    └──────────────────────────┘
 del a → refcnt=1 ;  del b → refcnt=0 → object freed immediately

 pymalloc:  Arena (1 MiB) ──► Pools (16 KiB) ──► Blocks (8..512 bytes)
 objects > 512 bytes → system malloc
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Heap | Memory area for objects | Objects की memory का क्षेत्र |
| Reference | A name pointing to an object | Object की ओर इशारा करने वाला नाम |
| pymalloc | CPython's small-object allocator | छोटे objects का allocator |
| Arena / pool / block | pymalloc's memory levels | pymalloc की memory के स्तर |
| Interning | Sharing one object for equal immutable values | बराबर immutable values के लिए एक ही object |
| Memory leak | Memory kept alive that is no longer needed | जरूरत खत्म होने पर भी बची हुई memory |

---

## ⚡ 3-Line Summary
English: CPython stores every value as an object in a private heap and frees it automatically through reference counting plus a cycle collector. Names are references, so assignment shares objects. Real-world leaks come from unbounded caches and global lists, not from forgetting `free`.
Hindi: CPython हर value को private heap में object की तरह रखता है और reference counting व cycle collector से अपने आप free करता है। नाम references हैं, इसलिए assignment से objects साझा होते हैं। असली leaks बिना limit वाले caches और global lists से आते हैं, `free` भूलने से नहीं।

---

## ➡️ Next Topic
**156. Reference Counting** — how the count works, `sys.getrefcount`, when it goes up and down, and why it frees objects instantly.
