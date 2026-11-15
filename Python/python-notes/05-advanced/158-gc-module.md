---

# 158. gc Module
# हिंदी में: gc Module (Garbage Collector को control करना)

---

## 🔵 Simple Definition (English)
The `gc` module is the control panel of Python's cycle garbage collector. You can turn it on or off, run it by hand with `gc.collect()`, read its thresholds and statistics, and inspect which objects are tracked. Normal objects are freed by reference counting; `gc` exists only for reference cycles.

## 🔵 सरल परिभाषा (Hindi)
`gc` module Python के cycle garbage collector का control panel है। इससे आप GC को on/off कर सकते हैं, `gc.collect()` से हाथ से चला सकते हैं, thresholds और statistics देख सकते हैं और देख सकते हैं कि कौन से objects track हो रहे हैं। आम objects reference counting से साफ होते हैं; `gc` सिर्फ reference cycles के लिए है।

---

## 🔴 Problem it Solves
Reference counting cannot free objects that point to each other (`a.other = b`, `b.other = a`): their counts never reach zero. The cycle collector finds such unreachable groups. The `gc` module lets you tune it: pause it during a latency-critical section, force a collection after a big batch job, or debug memory leaks by listing objects.

## 🔴 यह क्यों बना? (Hindi)
Reference counting उन objects को साफ नहीं कर सकता जो एक-दूसरे को point करते हैं (`a.other = b`, `b.other = a`) क्योंकि उनका count कभी 0 नहीं होता। Cycle collector ऐसे unreachable groups ढूँढता है। `gc` module से आप इसे tune कर सकते हैं: latency-critical हिस्से में रोकना, बड़े batch job के बाद force collect करना, या memory leak debug करने के लिए objects की list देखना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container objects (list, dict, class instances) are "tracked" by the GC
Step 2 → Every allocation minus deallocation bumps a gen-0 counter
Step 3 → When the counter passes threshold0, gen-0 is scanned
Step 4 → Objects only referenced from inside the scanned group are unreachable
Step 5 → Unreachable objects are finalized and freed; survivors move to an older generation
Step 6 → Older generations (1, 2) are scanned less often (thresholds 10, 10)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container objects (list, dict, class instance) GC में "tracked" होते हैं
Step 2 → हर allocation - deallocation gen-0 के counter को बढ़ाता है
Step 3 → Counter threshold0 पार करे तो gen-0 scan होती है
Step 4 → जो objects सिर्फ उसी group के अंदर से referenced हैं वे unreachable हैं
Step 5 → Unreachable objects साफ होते हैं; बचे हुए objects पुरानी generation में जाते हैं
Step 6 → पुरानी generations (1, 2) कम बार scan होती हैं (thresholds 10, 10)
```

---

## 🟡 Real World Example
A Swiggy order-analytics worker loads millions of objects at startup, then forks 8 child workers (Gunicorn preload). Instagram famously calls `gc.disable()` in the parent and `gc.freeze()` before forking so the child processes do not touch shared pages (copy-on-write saves RAM). A FastAPI service with strict p99 latency can also call `gc.collect()` between batches instead of at random moments.

## 🟡 Real Example Hindi mein
Swiggy का order-analytics worker startup में लाखों objects load करता है और फिर 8 child workers fork करता है (Gunicorn preload)। Instagram parent में `gc.disable()` और fork से पहले `gc.freeze()` चलाता है ताकि child processes shared memory pages को न छुएँ (copy-on-write से RAM बचती है)। सख्त p99 latency वाली FastAPI service भी random समय की जगह batches के बीच `gc.collect()` चला सकती है।

---

## 💻 Code Example — Basic
```python
# Basic gc module usage - every line commented
import gc  # the garbage collector interface

print(gc.isenabled())  # is automatic collection on?
# Output: True

print(gc.get_threshold())  # (gen0, gen1, gen2) thresholds
# Output: (2000, 10, 10)   # Python 3.13 value; 3.12 and older show (700, 10, 10)


class Node:  # a tiny class to build a cycle with
    def __init__(self, name: str) -> None:  # constructor with type hints
        self.name: str = name  # label
        self.other: "Node | None" = None  # link to another node


a: Node = Node("a")  # create first node
b: Node = Node("b")  # create second node
a.other = b  # a points to b
b.other = a  # b points to a -> reference cycle
del a, b  # names removed, but the cycle keeps both alive
unreachable: int = gc.collect()  # force a full collection; returns objects found
print(unreachable >= 2)  # the two Nodes (and their dicts) were found
# Output: True

x: Node = Node("x")  # a fresh instance
print(gc.is_tracked(x), gc.is_tracked(1), gc.is_tracked("s"), gc.is_tracked([]))  # which objects are tracked
# Output: True False False True   # ints/str cannot hold references, so not tracked

print(len(gc.get_stats()), sorted(gc.get_stats()[0].keys()))  # per-generation statistics
# Output: 3 ['collected', 'collections', 'uncollectable']
```

## 💻 Code Example — Advanced
```python
# Production style: disable/enable, callbacks, freeze, and a safe context manager
import gc  # garbage collector
from contextlib import contextmanager  # for a reusable pause helper
from typing import Iterator, List  # type hints


class Node:  # object used to create cycles
    def __init__(self) -> None:  # constructor
        self.ref: "Node | None" = None  # reference to a peer


def make_cycles(n: int) -> None:  # creates n garbage cycles
    for _ in range(n):  # repeat n times
        a, b = Node(), Node()  # two nodes
        a.ref, b.ref = b, a  # point at each other


@contextmanager
def gc_paused() -> Iterator[None]:  # pause GC only inside a critical section
    was_enabled: bool = gc.isenabled()  # remember previous state
    gc.disable()  # stop automatic collections
    try:  # run caller code
        yield  # critical section runs here
    finally:  # always restore, even on error
        if was_enabled:  # only re-enable if it was on before
            gc.enable()  # restore automatic GC


with gc_paused():  # automatic GC is off inside this block
    make_cycles(1000)  # garbage piles up, nothing is collected
    freed: int = gc.collect()  # we choose WHEN to collect (still inside the quiet section)
print(freed >= 2000)  # at least the 2000 Node objects (exact number varies)
# Output: True
print(gc.isenabled())  # the helper restored automatic GC
# Output: True

# Callbacks: observe every collection (metrics!)
events: List[str] = []  # where we record events


def on_gc(phase: str, info: dict) -> None:  # called with "start" and "stop"
    events.append(f"{phase}:{info['generation']}")  # remember phase and generation


gc.callbacks.append(on_gc)  # register callback
gc.collect()  # full collection = generation 2
gc.callbacks.remove(on_gc)  # always unregister
print(events)  # one start, one stop
# Output: ['start:2', 'stop:2']

# freeze(): move all current objects to a permanent generation (good before fork)
gc.freeze()  # exclude existing objects from future scans
print(gc.get_freeze_count() > 0)  # many objects are now frozen
# Output: True
gc.unfreeze()  # put them back (undo for this demo)
print(gc.get_freeze_count())  # nothing frozen now
# Output: 0
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: reference counting + cycle GC that you CAN control
import gc
gc.collect()          # run now
gc.disable()          # stop automatic cycle collection
print(gc.get_threshold())
```

```javascript
// JavaScript (V8): tracing GC only, no public control
// global.gc() exists ONLY if node runs with: node --expose-gc app.js
if (global.gc) { global.gc(); }   // force a collection (debug only)
// You cannot disable or tune thresholds from code.
```

Key differences: V8 uses a pure tracing collector, so cycles are never a problem and there is nothing to configure. CPython frees most objects immediately by reference count and uses `gc` only for cycles, which is why you get a real API to control it.

---

## 🟠 FastAPI Connection
Expose a small admin endpoint to inspect GC state and force a collection. Protect it with authentication in production (never public).

```python
import gc  # gc module
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # test without server

app: FastAPI = FastAPI()  # create app

@app.get("/debug/gc")  # admin-only in real life
def gc_info() -> Dict[str, object]:
    return {
        "enabled": gc.isenabled(),  # is automatic GC on?
        "threshold": list(gc.get_threshold()),  # gen0/gen1/gen2 limits
        "tracked_objects": len(gc.get_objects()) > 0,  # sanity flag
    }

@app.post("/debug/gc/collect")  # force a full collection
def gc_collect() -> Dict[str, int]:
    return {"unreachable_found": gc.collect()}  # number of objects freed

client = TestClient(app)
print(client.get("/debug/gc").json())
# Output: {'enabled': True, 'threshold': [2000, 10, 10], 'tracked_objects': True}
print(client.post("/debug/gc/collect").json())
# Output: {'unreachable_found': 0}   (count depends on your garbage)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `gc.collect()` after every request "to be safe"
```python
# Wrong - a full collection is expensive and pauses the whole process
@app.get("/x")
def x():
    gc.collect()      # adds latency to every request
    return {}

# Correct - let refcounting do its job; collect between batches only
```

❌ Mistake 2: Disabling GC and forgetting to enable it again
```python
# Wrong - memory leaks from cycles forever
gc.disable()
run_job()

# Correct - restore in finally (or use the gc_paused() context manager above)
gc.disable()
try:
    run_job()
finally:
    gc.enable()
```

❌ Mistake 3: Thinking `del obj` calls `gc` or that gc is needed for normal objects
```python
# Wrong belief: "I must call gc.collect() to free this list"
data = [1, 2, 3]
del data              # refcount hits 0 -> freed immediately, gc not involved

# Correct: gc matters only for reference cycles
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import gc

class A:
    def __del__(self) -> None:
        print("A freed")

a = A()
a.me = a          # self-cycle
del a
print("after del")
print(gc.collect() > 0)
```

**Answer**:
```
after del
A freed
True
```
`del a` only removes the name; the self-reference keeps the refcount at 1, so nothing is printed yet. `gc.collect()` finds the cycle and runs `__del__` (since Python 3.4 objects with `__del__` in cycles are collected safely). Without the collect, it would be freed at some later automatic collection.

---

## ⚫ Interview Questions + Answers

Q1: If CPython has reference counting, why does it need a GC?
A1: Reference counting cannot free cycles (A -> B -> A). The cyclic GC detects unreachable groups of container objects and frees them.

Q2: What are the three generations?
A2: Young objects start in generation 0. Survivors move to 1, then 2. Younger generations are scanned often because most objects die young. Thresholds come from `gc.get_threshold()`.

Q3: When would you call `gc.disable()`?
A3: In pre-fork servers (with `gc.freeze()`), short latency-critical sections, or benchmarks. Re-enable afterwards, or collect manually at safe points.

Q4: Which objects are not tracked?
A4: Atomic types that cannot contain references, such as `int`, `str`, `float`, and tuples containing only such values (a tuple may be untracked lazily). Check with `gc.is_tracked()`.

Q5: Does the GC behaviour differ across versions?
A5: Yes. 3.12 and earlier use threshold0 = 700, 3.13 reports 2000. Python 3.14 introduces an incremental collector with only two generations (young and old), so verify with `gc.get_threshold()` on your own version.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Debugging a memory leak (`gc.get_objects()`, `gc.get_referrers()`)
- Preparing a pre-fork server (`gc.freeze()`)
- Adding GC metrics via `gc.callbacks`

❌ Avoid when:
- You think it speeds up normal code (it rarely does)
- You disable it permanently to "gain performance"
- You call `gc.collect()` per request

---

## 📊 Visual Diagram

```
 new object ──► Gen 0 ──survives──► Gen 1 ──survives──► Gen 2
                 │ scan often        │ scan less          │ scan rarely
                 ▼                   ▼                    ▼
           unreachable? ──► free   unreachable? ──► free  unreachable? ──► free

 gc.freeze()  ──► permanent generation (never scanned)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reference cycle | Objects pointing to each other | आपस में point करते objects |
| Generation | Age bucket of tracked objects | objects की उम्र का group |
| Threshold | Allocation count that triggers a scan | scan शुरू करने की सीमा |
| gc.collect() | Force a full collection | पूरा collection ज़बरदस्ती चलाना |
| gc.freeze() | Exclude current objects from scans | मौजूदा objects को scan से बाहर करना |
| Tracked | Watched by the GC | GC की निगरानी में |

---

## ⚡ 3-Line Summary
English: `gc` controls the cycle collector that complements reference counting. Use `collect`, `disable`/`enable`, `freeze` and `callbacks` deliberately, never as a habit. Thresholds differ between Python versions.
Hindi: `gc` cycle collector को control करता है जो reference counting की मदद करता है। `collect`, `disable`/`enable`, `freeze` और `callbacks` सोच-समझकर इस्तेमाल करें, आदत की तरह नहीं। Thresholds Python version के हिसाब से बदलते हैं।

---

## ➡️ Next Topic
**159. Memory Profiling** — measure real memory use with `tracemalloc`, `sys.getsizeof` and snapshots.
