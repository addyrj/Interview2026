---

# 160. Weak References
# हिंदी में: Weak References (कमज़ोर संदर्भ)

---

## 🔵 Simple Definition (English)
A weak reference points to an object without keeping it alive. If every normal (strong) reference is gone, Python frees the object and the weak reference starts returning `None`. The `weakref` module gives you this tool.

## 🔵 सरल परिभाषा (Hindi)
Weak reference किसी object को point करता है, लेकिन उसे ज़िंदा नहीं रखता। जब सारे सामान्य (strong) references खत्म हो जाते हैं तो Python object को free कर देता है और weak reference `None` लौटाने लगता है। `weakref` module यही सुविधा देता है।

---

## 🔴 Problem it Solves
Python frees an object when its reference count reaches zero. A cache, an observer list or a parent-child tree normally stores strong references, so the objects never die even when nobody else uses them. This is a silent memory leak. Cyclic references (child points to parent, parent points to child) also delay cleanup. Weak references let these helper structures "look" at objects without owning them.

## 🔴 यह क्यों बना? (Hindi)
Python object तब free करता है जब उसका reference count शून्य हो जाए। Cache, observer list या parent-child tree सामान्यतः strong references रखते हैं, इसलिए objects तब भी नहीं मरते जब कोई और उन्हें use नहीं कर रहा। यह चुपचाप memory leak बन जाता है। Cyclic references (child parent को, parent child को point करे) भी सफाई में देरी करते हैं। Weak references इन helper structures को objects का मालिक बने बिना उन्हें "देखने" देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every object has a reference count (strong refs) plus an optional weak-ref list
Step 2 → weakref.ref(obj) stores a pointer but does NOT increase the reference count
Step 3 → ref() returns the object if alive, else None
Step 4 → When the strong count hits 0, CPython frees the object at once
Step 5 → Python clears all weak refs to it and runs their callbacks
Step 6 → WeakValueDictionary / WeakSet remove dead entries automatically
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर object का reference count (strong refs) होता है और weak-ref की list भी हो सकती है
Step 2 → weakref.ref(obj) pointer रखता है लेकिन reference count नहीं बढ़ाता
Step 3 → ref() object ज़िंदा हो तो object देता है, वरना None
Step 4 → Strong count 0 होते ही CPython object को तुरंत free करता है
Step 5 → Python उस पर लगे सारे weak refs साफ़ करता है और उनके callbacks चलाता है
Step 6 → WeakValueDictionary / WeakSet मरे हुए entries खुद हटा देते हैं
```

---

## 🟡 Real World Example
An AI inference service loads big models (500 MB each). A cache keyed by model name should reuse a model while some request uses it, but must not hold it forever. A `WeakValueDictionary` does exactly that. Another example: a Razorpay-style webhook bus keeps its listeners weakly so a deleted listener object does not stay in memory and does not get called by mistake. GUI frameworks and Django signals use the same idea.

## 🟡 Real Example Hindi mein
एक AI inference service बड़े models (हर एक 500 MB) load करती है। Model name वाला cache तब तक model reuse करे जब तक कोई request उसे use कर रही है, पर उसे हमेशा के लिए पकड़कर न रखे। `WeakValueDictionary` यही करता है। दूसरा उदाहरण: Razorpay जैसे webhook bus अपने listeners को weakly रखता है, ताकि हटाया हुआ listener memory में न रहे और गलती से call न हो। GUI frameworks और Django signals भी यही idea use करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic weakref examples
import gc                                         # garbage collector control
import weakref                                    # weak reference tools


class Node:                                       # a normal class (supports weakrefs)
    def __init__(self, name: str) -> None:        # constructor
        self.name: str = name                     # store a name


n: Node = Node("a")                               # one strong reference: n
r: weakref.ReferenceType[Node] = weakref.ref(n)   # weak reference, does NOT keep n alive
print(r() is n)                                   # calling r() returns the object -> True
print(r().name)                                   # use it like the real object
print(weakref.getweakrefcount(n))                 # how many weak refs point to n
del n                                             # drop the only strong reference
gc.collect()                                      # CPython frees at once; collect() is just safe
print(r())                                        # object is gone -> None

try:                                              # some builtin types cannot be weak-referenced
    weakref.ref([1, 2])                           # list does not support weakref
except TypeError as e:                            # catch the error
    print("TypeError:", e)                        # explain it

# Output:
# True
# a
# 1
# None
# TypeError: cannot create weak reference to 'list' object
```

## 💻 Code Example — Advanced
```python
# Production style: cache, WeakSet observers, finalize, WeakMethod
import gc                                         # force collection in demo
import weakref                                    # weak reference tools
from typing import Callable                       # type for callbacks


class Model:                                      # pretend: big ML model object
    def __init__(self, name: str) -> None:
        self.name: str = name                     # model name

    def on_event(self, msg: str) -> None:         # bound method used as a callback
        print(f"{self.name} got {msg}")           # show who got the message


class ModelCache:
    """Cache that never keeps a model alive by itself."""

    def __init__(self) -> None:
        self._items: weakref.WeakValueDictionary[str, Model] = weakref.WeakValueDictionary()

    def get(self, name: str) -> Model:
        model: Model | None = self._items.get(name)   # may be None if collected
        if model is None:                         # cache miss
            model = Model(name)                   # "load" it
            self._items[name] = model             # store weakly
        return model                              # caller now holds a strong ref

    def __len__(self) -> int:
        return len(self._items)                   # live entries only


class Bus:
    """Event bus holding listeners weakly (no memory leak if a listener dies)."""

    def __init__(self) -> None:
        self._subs: list[weakref.WeakMethod[Callable[[str], None]]] = []   # weak method refs

    def subscribe(self, method: Callable[[str], None]) -> None:
        self._subs.append(weakref.WeakMethod(method))   # plain ref to a bound method would die at once

    def publish(self, msg: str) -> int:
        delivered: int = 0                        # count live listeners
        for ref in self._subs:                    # visit every subscription
            fn = ref()                            # None if the owner is dead
            if fn is not None:                    # still alive
                fn(msg)                           # call it
                delivered += 1                    # count it
        return delivered                          # how many received


cache: ModelCache = ModelCache()                  # create cache
m1: Model = cache.get("bert")                     # miss -> created
m2: Model = cache.get("bert")                     # hit -> same object
print(m1 is m2, len(cache))                       # True 1
del m1, m2                                        # drop all strong refs
gc.collect()                                      # make sure
print(len(cache))                                 # 0 -> cache emptied itself

bus: Bus = Bus()                                  # create bus
a: Model = Model("A")                             # listener 1
b: Model = Model("B")                             # listener 2
bus.subscribe(a.on_event)                         # register A
bus.subscribe(b.on_event)                         # register B
print(bus.publish("hello"))                       # both alive -> 2
del b                                             # B dies
gc.collect()                                      # clean up
print(bus.publish("again"))                       # only A -> 1

seen: weakref.WeakSet[Model] = weakref.WeakSet()  # set that forgets dead objects
x: Model = Model("X")                             # make an object
seen.add(x)                                       # track it weakly
print(len(seen))                                  # 1
weakref.finalize(x, print, "x was cleaned up")    # run a callback when x dies
del x                                             # die -> finalizer prints
gc.collect()                                      # safe
print(len(seen))                                  # 0

# Output:
# True 1
# 0
# A got hello
# B got hello
# 2
# A got again
# 1
# 1
# x was cleaned up
# 0
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Weak pointer | `weakref.ref(obj)` | `new WeakRef(obj)` (ES2021) |
| Weak-key map | `WeakKeyDictionary` | `WeakMap` |
| Weak-value map | `WeakValueDictionary` | none (use `Map` of `WeakRef`) |
| Weak set | `WeakSet` | `WeakSet` |
| Cleanup callback | `weakref.finalize` / ref callback | `FinalizationRegistry` |
| When object dies | immediately at refcount 0 | whenever the GC runs (not predictable) |

```python
# Python way
import weakref                                  # stdlib
class A: ...                                    # plain class
a = A()                                         # strong reference
r = weakref.ref(a)                              # weak reference
del a                                           # refcount hits 0
print(r())                                      # None right away in CPython
```
```javascript
// JavaScript way
let a = { name: "a" };                          // strong reference
const r = new WeakRef(a);                       // weak reference
a = null;                                       // drop strong ref
console.log(r.deref());                         // may STILL print the object until GC runs
```

Key difference: in CPython the weak reference dies immediately when the last strong reference goes. In JavaScript the timing is up to the garbage collector, so you cannot rely on it.

---

## 🟠 FastAPI Connection
FastAPI apps are long running, so any module-level dict that grows is a leak. Weak caches are used for expensive per-request objects, for WebSocket connection registries (a closed socket should disappear from the set) and for event subscribers.

```python
# FastAPI: per-request model cache that frees memory automatically
import gc                                         # force collection for the demo
import weakref                                    # weak cache
from fastapi import FastAPI                       # FastAPI app
from fastapi.testclient import TestClient         # in-process test client


class Model:                                      # heavy object stand-in
    def __init__(self, name: str) -> None:
        self.name: str = name                     # model name


app: FastAPI = FastAPI()                          # create app
cache: weakref.WeakValueDictionary[str, Model] = weakref.WeakValueDictionary()   # weak cache


@app.get("/predict/{name}")                       # GET /predict/bert
def predict(name: str) -> dict[str, object]:
    model: Model | None = cache.get(name)         # try the cache first
    hit: bool = model is not None                 # was it cached?
    if model is None:                             # miss
        model = Model(name)                       # load model
        cache[name] = model                       # cache weakly
    return {"model": model.name, "cache_hit": hit}   # model dies after the request ends


client: TestClient = TestClient(app)              # test client
print(client.get("/predict/bert").json())         # first call -> miss
gc.collect()                                      # free the unused model
print(len(cache))                                 # cache is empty again

# Output:
# {'model': 'bert', 'cache_hit': False}
# 0
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Weak-referencing a temporary object
✅ Correct: keep a strong reference somewhere else

```python
import weakref
class A: ...
# Wrong - the temporary A() dies at once
r = weakref.ref(A())
print(r())                 # None
# Right - hold it in a variable
a = A()
r = weakref.ref(a)
print(r() is a)            # True
```

❌ Mistake 2: Weak-referencing list, dict, int, str, tuple
✅ Correct: use your own class (or a subclass of list/dict, which allows weakrefs)

```python
import weakref
# Wrong
# weakref.ref({})          # TypeError: cannot create weak reference to 'dict' object
# Right
class Box(dict): ...       # a subclass supports weak references
b = Box()
r = weakref.ref(b)
print(r() is b)            # True
```

❌ Mistake 3: Using the result of `ref()` without a None check
✅ Correct: store it in a local variable and check it once

```python
import weakref
class A:
    def hi(self) -> str: return "hi"
a = A(); r = weakref.ref(a)
# Wrong - object can die between the two calls (in other threads / after del)
# if r(): r().hi()
# Right
obj = r()                  # one call, now a strong reference
if obj is not None:
    print(obj.hi())
```

❌ Mistake 4: `weakref.ref(self.method)` for a bound method
✅ Correct: use `weakref.WeakMethod` (the bound method object is temporary)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import weakref
class A: pass
a = A()
r = weakref.ref(a)
b = r()
del a
print(r() is None)
del b
print(r() is None)
print(weakref.ref(A())())
```
Answer: `False`, `True`, `None` (verified on Python 3.13). Calling `r()` created a new strong reference `b`, so deleting `a` did not free the object. After `del b` the count reached zero and the object was freed. The last line creates a temporary `A()` that dies right after the weak reference is built, so the call gives `None`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a strong and a weak reference?
A1: A strong reference increases the reference count and keeps the object alive. A weak reference does not. When only weak references remain the object is freed and the weak reference returns `None`.

Q2: Which types cannot be weakly referenced?
A2: Built-in `int`, `str`, `tuple`, `list`, `dict`, `set` instances. User classes work, classes using `__slots__` need `"__weakref__"` in the slots, and subclasses of `list`/`dict` work.

Q3: When would you use `WeakValueDictionary` over a normal dict cache?
A3: When the cache must not extend an object's lifetime, for example sharing heavy objects (models, DB sessions, parsed documents) while somebody uses them. Entries disappear on their own, so there is no manual eviction.

Q4: Do weak references fix reference cycles?
A4: Not directly. The cycle collector (`gc`) frees cycles. But a weak back-pointer (child to parent) avoids creating the cycle in the first place, so memory is freed immediately by reference counting.

Q5: What is `weakref.finalize` and why prefer it over `__del__`?
A5: `finalize(obj, func, *args)` runs `func` when `obj` dies, or at interpreter exit. It does not depend on the object, avoids `__del__` pitfalls (resurrection, ordering problems) and can be cancelled or called early.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caches of big shareable objects
- Observer / listener / event-bus registries
- Parent back-pointers in trees and graphs
- Per-object metadata kept outside the object (`WeakKeyDictionary`)

❌ Avoid when:
- You need the object to stay alive (you must hold a strong ref)
- The value is a plain `int`/`str`/`list` (cannot be weakly referenced)
- You need predictable cache eviction by size or time (use `functools.lru_cache`, Redis, TTL cache)

---

## 📊 Visual Diagram
```
 strong refs                 weak refs
 variable "n" ───────┐
                     ▼
                 ┌────────┐ ◄ - - - - weakref.ref   (does not count)
                 │ Node a │ ◄ - - - - WeakValueDictionary entry
                 └────────┘
 del n  -> strong count 0 -> object freed -> weak refs now return None
                                          -> WeakValueDictionary entry removed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Strong reference | Keeps object alive | मजबूत संदर्भ, object को ज़िंदा रखता है |
| Weak reference | Does not keep object alive | कमज़ोर संदर्भ, object को नहीं रोकता |
| Reference count | Number of strong refs | कितने strong refs हैं इसकी गिनती |
| Finalizer | Callback run when object dies | object मरने पर चलने वाला callback |
| WeakValueDictionary | Dict whose values are weak | ऐसा dict जिसकी values weak हैं |
| Dangling reference | Pointer to a freed object | मर चुके object का pointer |

---

## ⚡ 3-Line Summary
English: A weak reference watches an object without owning it. When the object dies the reference returns `None`. Use `WeakValueDictionary`, `WeakSet`, `WeakMethod` and `finalize` for caches, listeners and cleanup.
Hindi: Weak reference object को देखता है पर उसका मालिक नहीं बनता। Object मरने पर reference `None` देता है। Caches, listeners और cleanup के लिए `WeakValueDictionary`, `WeakSet`, `WeakMethod` और `finalize` use करें।

---

## ➡️ Next Topic
**161. Metaclasses — Deep Dive** — the class that builds classes: `type`, `__new__`/`__init__`/`__call__` of a metaclass, registries and singletons.
