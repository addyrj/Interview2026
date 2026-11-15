---

# 157. Garbage Collection
# हिंदी में: Garbage Collection (कचरा साफ करना)

---

## 🔵 Simple Definition (English)
Garbage collection in CPython is the extra mechanism that finds and frees objects that reference counting cannot free: groups of objects pointing to each other in a cycle but unreachable from the program. The cyclic garbage collector groups tracked objects into three generations and scans the young ones often and the old ones rarely.

## 🔵 सरल परिभाषा (Hindi)
CPython में garbage collection वह अतिरिक्त mechanism है जो उन objects को ढूंढकर free करता है जिन्हें reference counting free नहीं कर सकती: ऐसे objects के समूह जो cycle में एक-दूसरे की ओर इशारा करते हैं पर program से पहुंच के बाहर हैं। Cyclic garbage collector tracked objects को तीन generations में बांटता है और नई generations को बार-बार, पुरानी को कभी-कभी scan करता है।

---

## 🔴 Problem it Solves
Reference counting alone has one blind spot: a cycle (`a.peer = b; b.peer = a`) keeps both counts at 1 forever, even after your code lost access to both objects. In a long-running server, parent-child links, linked lists, graphs, callbacks that capture `self` and exception tracebacks create cycles constantly. Without the cyclic collector this memory would leak.

## 🔴 यह क्यों बना? (Hindi)
Reference counting का एक अंधा कोना है: cycle (`a.peer = b; b.peer = a`) दोनों के count को हमेशा 1 रखती है, भले ही आपके code की दोनों तक पहुंच खत्म हो चुकी हो। लंबे चलने वाले server में parent-child links, linked lists, graphs, `self` पकड़ने वाले callbacks और exception tracebacks लगातार cycles बनाते हैं। Cyclic collector के बिना यह memory leak हो जाती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Only "container" objects that can hold references (list, dict, class instances...) are tracked
Step 2 → Each tracked object belongs to a generation: 0 (young), 1, 2 (old)
Step 3 → New objects start in generation 0. Counter: allocations minus deallocations
Step 4 → When the gen-0 counter exceeds threshold0 (2000 by default), a gen-0 collection runs
Step 5 → The collector copies each object's refcount, subtracts references that come from
         INSIDE the group; objects still having outside references are reachable
Step 6 → Everything reachable from those is kept; the rest is unreachable garbage -> freed
Step 7 → Survivors are promoted to the next generation (0 -> 1 -> 2)
Step 8 → Gen 1 is collected after threshold1 (10) gen-0 runs, gen 2 after threshold2 (10) gen-1 runs
Step 9 → Since Python 3.4 (PEP 442) objects with __del__ in cycles can also be collected
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सिर्फ "container" objects जो references रख सकते हैं (list, dict, class instances...) track होते हैं
Step 2 → हर tracked object किसी generation में होता है: 0 (नई), 1, 2 (पुरानी)
Step 3 → नए objects generation 0 में शुरू होते हैं। Counter: allocations घटा deallocations
Step 4 → जब gen-0 counter threshold0 (default 2000) से ऊपर जाता है, gen-0 collection चलता है
Step 5 → Collector हर object का refcount copy करता है, group के अंदर से आने वाले references घटाता है;
         जिन objects के बाहरी references बचे हैं वे reachable हैं
Step 6 → उनसे पहुंचने योग्य सब कुछ रखा जाता है; बाकी unreachable कचरा है -> free
Step 7 → बचे हुए objects अगली generation में promote होते हैं (0 -> 1 -> 2)
Step 8 → Gen 1 threshold1 (10) gen-0 runs के बाद, gen 2 threshold2 (10) gen-1 runs के बाद collect होता है
Step 9 → Python 3.4 (PEP 442) से cycles में __del__ वाले objects भी collect हो सकते हैं
```

---

## 🟡 Real World Example
An ORM-style code base links `Order.items` and `Item.order` both ways. Each request loads such graphs, and when the request ends the whole graph is unreachable but its counts never hit zero. The cyclic collector cleans those graphs in the background. Teams also tune it: Instagram famously disabled and later tuned the GC in their Django workers to keep memory shared after fork, using `gc.freeze()`.

## 🟡 Real Example Hindi mein
ORM-style code base में `Order.items` और `Item.order` दोनों तरफ जुड़े हैं। हर request ऐसे graphs load करती है, और request खत्म होने पर पूरा graph unreachable होता है पर उसके counts 0 नहीं होते। Cyclic collector इन graphs को background में साफ करता है। Teams इसे tune भी करती हैं: Instagram ने अपने Django workers में fork के बाद memory साझा रखने के लिए GC को बंद और बाद में tune किया और `gc.freeze()` इस्तेमाल किया।

---

## 💻 Code Example — Basic
```python
# Garbage collection: cycles, generations, thresholds
import gc                                                 # cyclic garbage collector


class Node:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.peer: "Node | None" = None                   # link used to build a cycle

    def __del__(self) -> None:
        print(f"{self.name} collected")


print("thresholds:", gc.get_threshold())                  # (gen0, gen1, gen2) trigger values
print("enabled:", gc.isenabled())                         # automatic GC on by default
gc.disable()                                              # stop automatic runs to demo manually

a, b = Node("a"), Node("b")                               # two objects
a.peer, b.peer = b, a                                     # a <-> b cycle
del a, b                                                  # refcounts stay at 1 each
print("deleted names; objects still alive (cycle)")
found: int = gc.collect()                                 # run a full collection now
print("unreachable objects found:", found > 0)

gc.enable()                                               # restore normal behaviour
print("counts (gen0 allocations - deallocations, gen1 runs, gen2 runs):", len(gc.get_count()))

# Output (threshold values can differ between versions):
# thresholds: (2000, 10, 10)
# enabled: True
# deleted names; objects still alive (cycle)
# a collected
# b collected
# unreachable objects found: True
# counts (gen0 allocations - deallocations, gen1 runs, gen2 runs): 3
```

## 💻 Code Example — Advanced
```python
# Production style: parent/child cycle vs weakref fix, GC callbacks, generation stats
import gc                                                 # collector control
import weakref                                            # break cycles
from typing import Any                                    # any type


class Parent:
    def __init__(self) -> None:
        self.children: list[Any] = []                     # parent -> child (strong)


class Child:
    def __init__(self, parent: Parent) -> None:
        self.parent: Parent = parent                      # child -> parent (strong): CYCLE
        parent.children.append(self)


class SafeChild:
    def __init__(self, parent: Parent) -> None:
        self._parent = weakref.ref(parent)                # child -> parent (weak): no cycle
        parent.children.append(self)

    @property
    def parent(self) -> Parent | None:
        return self._parent()                             # None if parent is gone


gc.disable()                                              # deterministic demo
gc.collect()                                              # start clean

p1 = Parent(); Child(p1)
probe1 = weakref.ref(p1)                                  # lets us see if p1 is still alive
del p1
print("cycle alive after del:", probe1() is not None)     # True: refcount alone can't free it
gc.collect()
print("cycle alive after gc :", probe1() is not None)     # False

p2 = Parent(); SafeChild(p2)
probe2 = weakref.ref(p2)
del p2
print("weakref design alive after del:", probe2() is not None)   # False: freed by refcount alone

events: list[str] = []


def on_gc(phase: str, info: dict[str, Any]) -> None:
    if phase == "stop":                                   # called after each collection
        events.append(f"gen{info['generation']} collected={info['collected']}")


gc.callbacks.append(on_gc)                                # observe every collection
tmp = Parent(); Child(tmp); del tmp                       # create garbage cycle
gc.collect(0)                                             # collect youngest generation only
gc.callbacks.remove(on_gc)
print(events)
print([sorted(s) for s in gc.get_stats()][0])             # keys per generation
gc.enable()

# Output:
# cycle alive after del: True
# cycle alive after gc : False
# weakref design alive after del: False
# ['gen0 collected=3']
# ['collected', 'collections', 'uncollectable']
```
Both blocks were run on Python 3.13.3 and printed exactly this. The `collected=3` counts Parent, Child and the `children` list. Python 3.14 introduces an incremental, two-generation collector, so thresholds and generation behaviour change there; check `gc.get_threshold()` on your version.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (CPython) | JavaScript (V8) |
|---------|------------------|-----------------|
| Primary freeing | reference counting | tracing (mark-and-sweep) |
| Cycles | extra cyclic GC | no problem, tracing handles them |
| Generations | 3 (young to old) | young (scavenger) and old space |
| Manual trigger | `gc.collect()` | `global.gc()` only with `--expose-gc` |
| Tuning | `gc.set_threshold`, `gc.freeze` | V8 flags like `--max-old-space-size` |

```python
# Python way
import gc
class N: pass
a, b = N(), N()
a.o, b.o = b, a          # cycle
del a, b                 # still alive until the cyclic GC runs
print(gc.collect() > 0)  # True
```
```javascript
// JavaScript way — cycles are collected without any special handling
let a = {}, b = {};
a.o = b; b.o = a;        // cycle
a = null; b = null;      // both unreachable: collected by V8 on its own schedule
// no API to force it in normal code (needs node --expose-gc, then global.gc())
```

Key difference: JavaScript has only a tracing collector, so cycles are not a special case. Python frees most garbage immediately by counting and uses the cyclic collector as a safety net just for cycles.

---

## 🟠 FastAPI Connection
Gunicorn/Uvicorn workers often preload the app and then fork. Calling `gc.freeze()` before forking moves all existing objects to a permanent generation, so the collector does not touch them and copy-on-write memory stays shared among workers. You can also expose GC stats on a diagnostics route.

```python
# FastAPI example — GC diagnostics endpoints + freeze before fork
import gc                                                   # collector
from fastapi import FastAPI                                 # FastAPI app
from fastapi.testclient import TestClient                   # in-process client

app: FastAPI = FastAPI()


@app.get("/gc")
def gc_info() -> dict[str, object]:
    return {
        "enabled": gc.isenabled(),                          # is automatic GC on?
        "threshold": list(gc.get_threshold()),              # trigger values
        "collections_per_gen": [s["collections"] for s in gc.get_stats()],   # runs per generation
    }


@app.post("/gc/collect")
def collect() -> dict[str, int]:
    return {"unreachable": gc.collect()}                    # force a full collection (admin only!)


client = TestClient(app)
print(client.get("/gc").json()["threshold"])                # [2000, 10, 10]
print(client.post("/gc/collect").status_code)               # 200

gc.collect()                                                # clean first, then freeze long-lived objects
gc.freeze()                                                 # call in the master process before fork
print(gc.get_freeze_count() > 0)                            # True
gc.unfreeze()                                               # tests only
```
(Run with TestClient on Python 3.13.3; the `threshold` and status code lines match the comments.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Disabling the GC without understanding the consequences
✅ Correct: measure first; if you disable it, call `gc.collect()` at safe moments

```python
import gc
gc.disable()          # Wrong in a long-running server: cycles pile up and memory grows
# Right: keep it enabled, or tune it: gc.set_threshold(50_000, 20, 20) after measuring
```

❌ Mistake 2: Creating parent <-> child strong cycles for no reason
✅ Correct: make the back-reference weak

```python
import weakref
class Child:
    def __init__(self, parent):
        self._parent = weakref.ref(parent)     # Right: no cycle, freed immediately by refcount
# Wrong: self.parent = parent  together with parent.children.append(self)
```

❌ Mistake 3: Calling `gc.collect()` to "fix" memory that is not cyclic garbage
✅ Correct: find the real owner of the references (global cache, list, closure)

```python
cache = []                      # global list keeps everything alive
# gc.collect() will free NOTHING here: the objects are still reachable.
# Right: bound the cache (deque(maxlen=N), lru_cache(maxsize=N)) or remove entries.
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import gc, weakref
gc.disable()

class A:
    pass

a = A()
a.me = a                      # self-reference
r = weakref.ref(a)
del a
print(r() is None)
gc.collect()
print(r() is None)
```
Answer: `False` then `True`. The object points to itself, so its refcount stays at 1 after `del a`; it is alive, and the weak reference still returns it. Only `gc.collect()` finds that nothing outside the cycle reaches it and frees it, after which the weak reference returns `None`. (With the GC enabled, a collection might happen between the lines, so the demo disables it.)

---

## ⚫ Interview Questions + Answers

Q1: Why does Python need a garbage collector if it has reference counting?
A1: Counting cannot free reference cycles. The cyclic GC detects groups of objects that reference each other but are unreachable from roots and frees them.

Q2: What are generations in Python's GC?
A2: Three lists (0, 1, 2) of tracked objects. Most objects die young, so generation 0 is scanned often (cheap), survivors are promoted and scanned less often. Default thresholds are `(2000, 10, 10)`.

Q3: Which objects does the cyclic GC track?
A3: Only containers that can participate in cycles (lists, dicts, sets, instances, functions). Ints, floats and strings never form cycles, so they are not tracked; simple tuples and empty dicts can also become untracked as an optimization.

Q4: Can objects with `__del__` be collected in cycles?
A4: Yes since Python 3.4 (PEP 442). Before that they ended up in `gc.garbage` uncollected. Still, avoid `__del__`.

Q5: How would you reduce GC pauses in a big service?
A5: Create fewer cyclic structures (use weakrefs), raise thresholds via `gc.set_threshold`, call `gc.freeze()` after startup (especially before fork), and avoid creating millions of tracked containers; for example use tuples/arrays or `__slots__` classes.

---

## 🔷 When to Use + When Not to Use
✅ Tune or call the GC when:
- Profiling shows GC pauses or growing memory from cycles
- You preload a big app and fork workers (`gc.freeze`)
- You run tests that must detect leaks (`gc.collect()` then check `gc.garbage`/objects)

❌ Avoid touching it when:
- Memory growth comes from caches or globals, not cycles
- You have no measurements
- You think `gc.collect()` is needed after every request (it adds latency and rarely helps)

---

## 📊 Visual Diagram
```
 allocate ──► [ gen 0 ] ──survive──► [ gen 1 ] ──survive──► [ gen 2 ]
               young, scanned          scanned after          scanned rarely
               when count > 2000       10 gen-0 runs          (every 10 gen-1 runs)

 Cycle detection (conceptual):
   A ◄──► B        gc_refs(A)=1 (from B), gc_refs(B)=1 (from A)
   subtract internal references  →  both become 0  →  no outside reference
   → unreachable → free both
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cyclic GC | Collector that frees reference cycles | Cycles को free करने वाला collector |
| Generation | Age group of tracked objects (0, 1, 2) | Tracked objects का उम्र समूह |
| Threshold | Count that triggers a collection | Collection शुरू करने वाली गिनती |
| Unreachable | No path from program roots | Program से कोई रास्ता नहीं |
| Promotion | Moving survivors to an older generation | बचे objects को पुरानी generation में भेजना |
| `gc.freeze()` | Move all objects to a permanent generation | सब objects को स्थायी generation में डालना |

---

## ⚡ 3-Line Summary
English: Reference counting frees most objects, and the cyclic GC (three generations, default thresholds 2000/10/10) frees unreachable cycles. Use weakrefs to avoid cycles and `gc.freeze()` before forking workers. Leaks from global caches are not fixed by `gc.collect()`.
Hindi: Reference counting अधिकांश objects को free करती है, और cyclic GC (तीन generations, default thresholds 2000/10/10) unreachable cycles को free करता है। Cycles से बचने के लिए weakrefs और workers fork करने से पहले `gc.freeze()` इस्तेमाल करें। Global caches से हुई leaks `gc.collect()` से ठीक नहीं होतीं।

---

## ➡️ Next Topic
**158. gc Module** — the functions you use to inspect and control the collector: `collect`, `get_objects`, `get_referrers`, `set_debug` and more.
