---

# 154. Slots vs Dict
# हिंदी में: `__slots__` बनाम `__dict__` (Memory बचाने का तरीका)

---

## 🔵 Simple Definition (English)
By default every Python object stores its attributes in a per-instance dictionary called `__dict__`. If a class declares `__slots__ = ("x", "y")`, Python removes that dictionary and keeps the attributes in fixed slots instead. This uses less memory, but you cannot add new attributes on the fly.

## 🔵 सरल परिभाषा (Hindi)
Default रूप से हर Python object अपने attributes एक per-instance dictionary `__dict__` में रखता है। अगर class में `__slots__ = ("x", "y")` लिखा है, तो Python वह dictionary हटा देता है और attributes को fixed slots में रखता है। इससे memory कम लगती है, लेकिन आप बाद में नए attributes नहीं जोड़ सकते।

---

## 🔴 Problem it Solves
A dictionary per object is flexible but costly. When you create hundreds of thousands of small objects (market ticks, log records, graph nodes), each carries a dict, and the memory adds up and slows the garbage collector. `__slots__` cuts the per-object overhead and also protects against typos like `tick.prise = 5` silently creating a new attribute.

## 🔴 यह क्यों बना? (Hindi)
हर object के लिए dictionary flexible है पर महंगी है। जब आप छोटे objects के लाखों instances बनाते हैं (market ticks, log records, graph nodes), हर एक के साथ dict आती है, जिससे memory बढ़ती है और garbage collector धीमा होता है। `__slots__` per-object overhead घटाता है और `tick.prise = 5` जैसी typo से चुपचाप नया attribute बनने से भी बचाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normal class: each instance gets a __dict__ (hash table) holding its attributes
Step 2 → With __slots__ = ("x", "y"): Python reserves two fixed fields inside the object
Step 3 → Each slot name becomes a descriptor on the class (member_descriptor)
Step 4 → obj.x reads the fixed field directly; no dictionary lookup
Step 5 → No __dict__ is created, so obj.z = 1 raises AttributeError
Step 6 → No __weakref__ either, unless you add "__weakref__" to __slots__
Step 7 → Inheritance: a child without __slots__ gets a __dict__ again

Memory idea:
   normal : [object header][ptr to __dict__] -> [hash table with keys and values]
   slots  : [object header][x][y]
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सामान्य class: हर instance को __dict__ (hash table) मिलता है जिसमें attributes रहते हैं
Step 2 → __slots__ = ("x", "y") के साथ: Python object के अंदर दो fixed fields रखता है
Step 3 → हर slot का नाम class पर descriptor बनता है (member_descriptor)
Step 4 → obj.x सीधे fixed field पढ़ता है; dictionary lookup नहीं होता
Step 5 → __dict__ बनता ही नहीं, इसलिए obj.z = 1 से AttributeError आता है
Step 6 → __weakref__ भी नहीं मिलता, जब तक __slots__ में "__weakref__" न जोड़ें
Step 7 → Inheritance: जो child class __slots__ नहीं लिखती उसे फिर से __dict__ मिल जाता है

Memory का विचार:
   सामान्य : [object header][__dict__ का ptr] -> [keys और values वाली hash table]
   slots   : [object header][x][y]
```

---

## 🟡 Real World Example
A stock-trading backend (Zerodha/Groww style) receives millions of price ticks per minute and keeps the last few hundred thousand in memory. Each tick has only `symbol`, `price` and `qty`. Switching the tick class to `@dataclass(slots=True)` lowers memory use and keeps the process smaller. Game servers, graph libraries and parsers do the same for their node objects.

## 🟡 Real Example Hindi mein
Stock-trading backend (Zerodha/Groww जैसा) हर मिनट लाखों price ticks पाता है और आखिरी कुछ लाख memory में रखता है। हर tick में सिर्फ `symbol`, `price` और `qty` होते हैं। Tick class को `@dataclass(slots=True)` कर देने से memory कम लगती है और process छोटा रहता है। Game servers, graph libraries और parsers अपने node objects के लिए यही करते हैं।

---

## 💻 Code Example — Basic
```python
# __slots__ vs __dict__: behaviour and size
import sys                                                # getsizeof


class WithDict:
    def __init__(self, x: int, y: int) -> None:
        self.x = x                                        # stored in per-instance dict
        self.y = y


class WithSlots:
    __slots__ = ("x", "y")                                # fixed attribute names, no __dict__

    def __init__(self, x: int, y: int) -> None:
        self.x = x                                        # stored in a fixed slot
        self.y = y


a, b = WithDict(1, 2), WithSlots(1, 2)
print(hasattr(a, "__dict__"), hasattr(b, "__dict__"))     # True False
print(sys.getsizeof(a) + sys.getsizeof(a.__dict__), sys.getsizeof(b))   # size in bytes (varies by version)
a.z = 3                                                   # dynamic attribute: allowed
try:
    b.z = 3                                               # not in __slots__
except AttributeError as e:
    print("AttributeError:", e)
print(type(WithSlots.x).__name__)                         # slot is a descriptor (member_descriptor)

# Output (the byte counts depend on Python version and platform):
# True False
# 344 48
# AttributeError: 'WithSlots' object has no attribute 'z' and no __dict__ for setting new attributes
# member_descriptor
```

## 💻 Code Example — Advanced
```python
# Production style: measure memory of 200k objects and see slots + inheritance rules
import timeit                                             # attribute speed
import tracemalloc                                        # memory measurement
from dataclasses import dataclass                         # dataclass with slots=True (3.10+)


@dataclass
class TickDict:
    symbol: str
    price: float
    qty: int


@dataclass(slots=True)                                    # generates __slots__ for us
class TickSlots:
    symbol: str
    price: float
    qty: int


def build(cls: type, n: int = 200_000) -> list[object]:
    return [cls("INFY", 1500.5, i) for i in range(n)]    # n objects with different qty


def measure(cls: type) -> float:
    tracemalloc.start()                                   # start tracking allocations
    data = build(cls)                                     # allocate the objects
    current, _peak = tracemalloc.get_traced_memory()      # bytes currently allocated
    tracemalloc.stop()
    del data
    return current / 1024 / 1024                          # MiB


d, s = measure(TickDict), measure(TickSlots)
print(f"dict : {d:.1f} MiB")
print(f"slots: {s:.1f} MiB")
print("slots uses less memory:", s < d)

t1, t2 = TickDict("A", 1.0, 1), TickSlots("A", 1.0, 1)
print("read speed ratio ~", round(timeit.timeit(lambda: t1.qty, number=2_000_000) /
                                  timeit.timeit(lambda: t2.qty, number=2_000_000), 1))


class Base:
    __slots__ = ("a",)                                    # parent with slots


class ChildNoSlots(Base):                                 # child WITHOUT __slots__ gets a __dict__ again
    pass


class ChildSlots(Base):
    __slots__ = ("b",)                                    # only NEW names


print(hasattr(ChildNoSlots(), "__dict__"), hasattr(ChildSlots(), "__dict__"))

# Output (memory and speed numbers vary by machine/version; one real run on Python 3.13.3):
# dict : 26.0 MiB
# slots: 18.3 MiB
# slots uses less memory: True
# read speed ratio ~ 1.0
# True False
```
Both blocks were run on Python 3.13.3. In 3.13 the memory saving is smaller than in old versions (about 30% here) because instances already store their values compactly; read speed was practically equal. Treat the numbers as indicative, not as promises.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Default object | dynamic `__dict__` per instance | dynamic properties (hidden classes in V8) |
| Fixed fields | `__slots__` | class fields; `Object.seal` / `Object.freeze` blocks additions |
| Block new attributes | `__slots__` (AttributeError) | `Object.preventExtensions` / `seal` |
| Memory saving | yes, explicit | engine optimizes automatically with hidden classes |

```python
# Python way
class Point:
    __slots__ = ("x", "y")               # only these two attributes allowed
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y
p = Point(1, 2)
# p.z = 3   # AttributeError
```
```javascript
// JavaScript way
class Point {
  constructor(x, y) { this.x = x; this.y = y; Object.seal(this); }  // no new props, can't delete
}
const p = new Point(1, 2);
p.z = 3;            // ignored silently (sloppy mode) or TypeError (strict mode)
```

Key difference: V8 already shares object shapes (hidden classes) behind the scenes, so JavaScript developers rarely tune object memory by hand. In Python you opt in with `__slots__` or `dataclass(slots=True)`.

---

## 🟠 FastAPI Connection
FastAPI can return dataclasses directly and serialise them. In a data-heavy service (market data, telemetry) you can keep a large in-memory cache of `@dataclass(slots=True)` objects and return them from routes with `response_model`.

```python
# FastAPI example — slotted dataclass in an in-memory cache, returned from a route
from dataclasses import dataclass                           # dataclass decorator
from fastapi import FastAPI                                 # FastAPI app
from fastapi.testclient import TestClient                   # in-process client


@dataclass(slots=True)                                      # compact objects
class Tick:
    symbol: str
    price: float


app: FastAPI = FastAPI()
CACHE: list[Tick] = [Tick("INFY", 1500.5), Tick("TCS", 3900.0)]   # in-memory store


@app.get("/ticks", response_model=list[Tick])
def ticks() -> list[Tick]:
    return CACHE                                            # serialised to JSON


print(TestClient(app).get("/ticks").json())
# [{'symbol': 'INFY', 'price': 1500.5}, {'symbol': 'TCS', 'price': 3900.0}]
```
Note: Pydantic models do not use `__slots__` for fields; use slotted dataclasses (or plain classes) for internal bulk data and Pydantic at the API boundary.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding `__slots__` to a child but not parent (or the reverse) and expecting savings
✅ Correct: every class in the chain needs `__slots__`, listing only new names

```python
class Base:
    __slots__ = ("a",)
class Child(Base):             # Wrong: no __slots__ -> Child instances get a __dict__ again
    pass
c = Child(); c.zzz = 1         # works silently
class Child2(Base):
    __slots__ = ("b",)         # Right: only the new names
```

❌ Mistake 2: Weak references fail on slotted classes
✅ Correct: add `"__weakref__"` to `__slots__` if you need `weakref`

```python
import weakref
class W:
    __slots__ = ("x",)
# weakref.ref(W())   # TypeError: cannot create weak reference to 'W' object
class W2:
    __slots__ = ("x", "__weakref__")   # Right
```

❌ Mistake 3: Class variable with the same name as a slot
✅ Correct: use different names (or set defaults in `__init__`)

```python
# Wrong:
# class B:
#     __slots__ = ("x",)
#     x = 5      # ValueError: 'x' in __slots__ conflicts with class variable
# Right: keep defaults in __init__  ->  self.x = 5
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    __slots__ = ("x",)

a = A()
try:
    print(a.x)
except AttributeError as e:
    print(e)

class M1: __slots__ = ("a",)
class M2: __slots__ = ("b",)
try:
    class M3(M1, M2): pass
except TypeError as e:
    print(e)
```
Answer: First `'A' object has no attribute 'x'`: a slot that was never assigned is empty, reading it raises `AttributeError` (not `None`). Second `multiple bases have instance lay-out conflict`: two parents that both define non-empty `__slots__` cannot be combined because each wants its own memory layout. Only one parent may have non-empty slots.

---

## ⚫ Interview Questions + Answers

Q1: What does `__slots__` do and what are the trade-offs?
A1: It replaces the per-instance `__dict__` with fixed storage. Pros: less memory, typo protection, slightly faster creation. Cons: no dynamic attributes, no weakrefs by default, multiple-inheritance limits, and every subclass must repeat it.

Q2: Does `__slots__` always make attribute access faster?
A2: Not significantly. Access is a descriptor read of a fixed offset instead of a dictionary lookup, but modern CPython caches attribute lookups, and in Python 3.13 the measured difference was close to zero. The main win is memory.

Q3: Can slotted classes be pickled and used with dataclasses?
A3: Yes. Pickle works (protocol 2+ handles slots) and `@dataclass(slots=True)` (Python 3.10+) generates `__slots__` for you. Note that `slots=True` builds a new class object, so references to the original class taken inside the class body can point to the old one.

Q4: How to still allow dynamic attributes with slots?
A4: Add `"__dict__"` to `__slots__`. You keep the fixed slots for the known names and get a dictionary for extra ones, losing most of the memory benefit.

Q5: When is it NOT worth it?
A5: When you create few objects, when you need `weakref`, multiple inheritance or dynamic attributes, or when Pydantic/ORM models are used (they manage their own storage).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You create very many instances of a small class (ticks, nodes, records)
- You want to forbid accidental new attributes
- Memory pressure or garbage-collector time is a problem

❌ Avoid when:
- Only a few objects exist (no gain)
- You need dynamic attributes, weakrefs or complicated multiple inheritance
- Frameworks must monkey-patch or add attributes to your objects (mocks, ORMs)

---

## 📊 Visual Diagram
```
 Normal object                       Slotted object
 ┌──────────────┐                    ┌──────────────┐
 │ header       │                    │ header       │
 │ __dict__ ptr ─┼─► ┌───────────┐   │ slot x ─────►│ 1
 │ __weakref__  │    │ "x": 1    │   │ slot y ─────►│ 2
 └──────────────┘    │ "y": 2    │   └──────────────┘
                     └───────────┘     no dict, no weakref
 obj.z = 3  works                      obj.z = 3  -> AttributeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__dict__` | Per-instance attribute dictionary | Instance की attribute dictionary |
| `__slots__` | Fixed list of allowed attributes | Allowed attributes की fixed सूची |
| member_descriptor | Descriptor behind each slot | हर slot के पीछे का descriptor |
| `__weakref__` | Slot enabling weak references | Weak references को सक्षम करने वाला slot |
| Instance layout | How an object is arranged in memory | Object memory में कैसे बैठा है |
| `dataclass(slots=True)` | Auto-generate slots (3.10+) | Slots अपने आप बनाना |

---

## ⚡ 3-Line Summary
English: `__slots__` replaces the per-instance `__dict__` with fixed storage, saving memory and blocking accidental attributes. Remember: no `__weakref__` by default, children need their own `__slots__`, and the speed gain is small. Use `@dataclass(slots=True)` for bulk data objects.
Hindi: `__slots__` per-instance `__dict__` की जगह fixed storage देता है, जिससे memory बचती है और गलती से नए attributes नहीं बनते। याद रखें: `__weakref__` default नहीं मिलता, children को अपना `__slots__` चाहिए, और speed का फायदा थोड़ा है। Bulk data objects के लिए `@dataclass(slots=True)` इस्तेमाल करें।

---

## ➡️ Next Topic
**155. Memory Management in Python** — how CPython allocates memory, object headers, private heaps and the two mechanisms that free memory.
