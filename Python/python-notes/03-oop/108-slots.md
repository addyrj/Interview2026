---

# 108. __slots__
# हिंदी में: __slots__ (Memory बचाने वाला Attribute Restriction)

---

## 🔵 Simple Definition (English)
`__slots__` is a class variable that lists the only attributes an object may have. Python then stores them in a fixed compact layout instead of a per-object dictionary (`__dict__`). Result: less memory, slightly faster attribute access, and typos like `obj.nmae = 1` raise an error.

## 🔵 सरल परिभाषा (Hindi)
`__slots__` एक class variable है जो बताता है कि object में सिर्फ कौन से attributes हो सकते हैं। Python तब हर object के लिए dictionary (`__dict__`) बनाने की बजाय fixed compact layout में attributes रखता है। नतीजा: कम memory, थोड़ा तेज attribute access, और `obj.nmae = 1` जैसी typo पर error आता है।

---

## 🔴 Problem it Solves
By default every instance carries a `__dict__` - a full hash table. For one object that is fine. For millions of small objects (points, ticks, events, rows) the dictionaries dominate memory. In the test below a plain instance costs 48 bytes plus a 296-byte dict, while a slotted instance costs 48 bytes in total. Also, normal classes silently accept misspelled attributes, which creates hard-to-find bugs.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से हर instance के साथ `__dict__` होता है - पूरी hash table। एक object के लिए ठीक है, लेकिन लाखों छोटे objects (points, ticks, events, rows) में dictionaries ही ज्यादातर memory खा जाती हैं। नीचे के test में सामान्य instance 48 bytes + 296 bytes की dict लेता है, जबकि slotted instance कुल 48 bytes। साथ ही normal class गलत spelling वाले attribute को चुपचाप स्वीकार कर लेती है, जिससे bugs ढूंढना मुश्किल होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write __slots__ = ("x", "y") inside the class body
Step 2 → At class creation, Python makes a "member descriptor" for x and y
Step 3 → Each instance gets fixed memory cells for x and y (no __dict__)
Step 4 → obj.x reads/writes its cell through the descriptor
Step 5 → obj.z = 1 fails: AttributeError (no __dict__ to hold z)
Step 6 → Subclass without its own __slots__ gets a __dict__ again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप class body में __slots__ = ("x", "y") लिखते हो
Step 2 → Class बनते समय Python x और y के लिए "member descriptor" बनाता है
Step 3 → हर instance को x और y के fixed memory cells मिलते हैं (__dict__ नहीं)
Step 4 → obj.x descriptor के जरिए उसी cell को पढ़ता/लिखता है
Step 5 → obj.z = 1 fail होता है: AttributeError (z रखने को __dict__ नहीं है)
Step 6 → जिस subclass में अपना __slots__ नहीं, उसे फिर से __dict__ मिल जाता है
```

---

## 🟡 Real World Example
A trading app (Zerodha-style) keeps 5 million `Tick(symbol, price, ts)` objects in memory for a chart. A game or map service holds millions of `Point(lat, lng)`. A log pipeline creates one small `LogRecord` object per line. Using `__slots__` cuts memory by roughly a third or more and makes the objects strict. Python's own libraries use it in many places for the same reason.

## 🟡 Real Example Hindi mein
Trading app (Zerodha जैसा) chart के लिए memory में 50 लाख `Tick(symbol, price, ts)` objects रखता है। Game या map service में लाखों `Point(lat, lng)` होते हैं। Log pipeline हर line के लिए एक छोटा `LogRecord` बनाता है। `__slots__` से memory लगभग एक-तिहाई या ज्यादा घटती है और objects strict बन जाते हैं। Python की अपनी libraries भी इसी कारण कई जगह इसे use करती हैं।

---

## 💻 Code Example — Basic
```python
# Basic __slots__ examples
import sys                                        # for getsizeof


class PlainPoint:                                 # normal class: has __dict__
    def __init__(self, x: int, y: int) -> None:   # constructor
        self.x: int = x                           # stored in __dict__
        self.y: int = y                           # stored in __dict__


class SlotPoint:                                  # slotted class: no __dict__
    __slots__ = ("x", "y")                        # the only allowed attributes

    def __init__(self, x: int, y: int) -> None:   # constructor
        self.x: int = x                           # stored in a fixed slot
        self.y: int = y                           # stored in a fixed slot


p: PlainPoint = PlainPoint(1, 2)                  # create plain object
s: SlotPoint = SlotPoint(1, 2)                    # create slotted object
print(hasattr(p, "__dict__"), hasattr(s, "__dict__"))   # who has a dict?
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__))     # plain: object + its dict (bytes)
print(sys.getsizeof(s))                           # slotted: object only (bytes)

p.z = 10                                          # plain class accepts any new attribute
print(p.z)                                        # 10
try:                                              # slotted class refuses
    s.z = 10                                      # not in __slots__
except AttributeError as e:                       # catch the error
    print(e)                                      # message tells why

print(SlotPoint.__slots__)                        # the declared slots
print(type(SlotPoint.x))                          # each slot is a member descriptor

# Output (sizes are for CPython 3.13 64-bit; they differ by version/platform):
# True False
# 344
# 48
# 10
# 'SlotPoint' object has no attribute 'z' and no __dict__ for setting new attributes
# ('x', 'y')
# <class 'member_descriptor'>
```

## 💻 Code Example — Advanced
```python
# Production style: measure memory, inheritance rules, __weakref__, pickling-safe design
import tracemalloc                                # measures Python memory allocations
import weakref                                    # to show the __weakref__ rule
from dataclasses import dataclass                 # dataclass(slots=True) needs 3.10+


class Tick:                                       # normal class
    def __init__(self, symbol: str, price: float) -> None:
        self.symbol: str = symbol                 # instance attribute
        self.price: float = price                 # instance attribute


class SlotTick:                                   # slotted version of the same class
    __slots__ = ("symbol", "price")               # fixed attributes

    def __init__(self, symbol: str, price: float) -> None:
        self.symbol: str = symbol                 # slot
        self.price: float = price                 # slot


def measure(cls: type, n: int = 100_000) -> int:
    """Return memory (bytes) used by n objects of cls."""
    tracemalloc.start()                           # begin tracking
    items: list = [cls("INFY", 1500.0) for _ in range(n)]   # keep objects alive
    used: int = tracemalloc.get_traced_memory()[0]   # current traced bytes
    tracemalloc.stop()                            # stop tracking
    del items                                     # free them
    return used                                   # bytes used


plain: int = measure(Tick)                        # memory with __dict__
slotted: int = measure(SlotTick)                  # memory with slots
print("slots use less memory:", slotted < plain)  # True (exact numbers vary)
print("saving > 20%:", (plain - slotted) / plain > 0.20)   # typical saving is 30%+


class Base:                                       # slotted base class
    __slots__ = ("a",)                            # one slot

    def __init__(self) -> None:
        self.a: int = 1                           # set the slot


class GoodChild(Base):                            # subclass that stays slotted
    __slots__ = ("b",)                            # ONLY new names, do not repeat "a"

    def __init__(self) -> None:
        super().__init__()                        # initialise parent slot
        self.b: int = 2                           # set own slot


class LazyChild(Base):                            # subclass WITHOUT __slots__
    pass                                          # silently gets a __dict__ again


print(hasattr(GoodChild(), "__dict__"), hasattr(LazyChild(), "__dict__"))   # False True

try:                                              # weak references need __weakref__
    weakref.ref(Base())                           # Base has no __weakref__ slot
except TypeError as e:                            # catch
    print(e)                                      # cannot create weak reference ...


class Weakable:                                   # add "__weakref__" explicitly
    __slots__ = ("v", "__weakref__")              # now weakref works


w = weakref.ref(Weakable())                       # works (object dies at once, w() is None)
print("weakref ok")                               # no error


@dataclass(slots=True)                            # Python 3.10+: dataclass writes __slots__
class Order:
    id: int                                       # field 1
    amount: float                                 # field 2


o: Order = Order(1, 99.5)                         # create
print(o, hasattr(o, "__dict__"))                  # slotted dataclass, no dict

# Output:
# slots use less memory: True
# saving > 20%: True
# False True
# cannot create weak reference to 'Base' object
# weakref ok
# Order(id=1, amount=99.5) False
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Restrict attributes | `__slots__` | `Object.seal()` / `Object.freeze()` / TypeScript types |
| Default object layout | dict per instance | engine "hidden classes" (automatic) |
| Add attribute later | allowed (unless slots) | allowed (unless sealed) |
| Memory saving control | explicit, by the developer | done by the V8 engine automatically |

```python
# Python way - slots reject unknown attributes
class User:
    __slots__ = ("name",)                     # only "name" allowed

    def __init__(self, name: str) -> None:
        self.name: str = name                 # set the slot

u: User = User("Amit")
try:
    u.nmae = "x"                              # typo
except AttributeError as e:
    print("blocked:", e)                      # blocked: 'User' object has no attribute 'nmae' ...
```
```javascript
// JavaScript way - seal the object after construction
class User {
  constructor(name) { this.name = name; Object.seal(this); }  // no new properties allowed
}
const u = new User("Amit");
u.nmae = "x";                                // silently ignored (throws in strict mode)
console.log(u.nmae);                         // undefined
```

Key difference: V8 optimizes object layout automatically, so JS developers rarely think about it. In Python the default layout is a dict per object, so `__slots__` is the manual tool for memory-heavy code.

---

## 🟠 FastAPI Connection
In FastAPI you use Pydantic models for request/response data, and those manage their own storage, so you do not add `__slots__` there. `__slots__` helps for internal high-volume objects: cached rows, events pushed to a queue, or `@dataclass(slots=True)` value objects kept in memory by a background worker.

```python
# FastAPI example - slotted dataclass for an in-memory event buffer
from dataclasses import asdict, dataclass         # dataclass helpers
from fastapi import FastAPI                       # FastAPI app
from fastapi.testclient import TestClient         # in-process testing


@dataclass(slots=True)                            # small, memory-efficient event object
class Event:
    user_id: int                                  # who did it
    action: str                                   # what they did


app: FastAPI = FastAPI()                          # create app
buffer: list[Event] = []                          # millions of events could live here


@app.post("/events")                              # POST /events?user_id=1&action=login
def add_event(user_id: int, action: str) -> dict[str, int]:
    buffer.append(Event(user_id, action))         # store slotted object
    return {"buffered": len(buffer)}              # report size


@app.get("/events")                               # GET /events
def list_events() -> list[dict]:
    return [asdict(e) for e in buffer]            # asdict works with slots too


client: TestClient = TestClient(app)              # client
client.post("/events", params={"user_id": 1, "action": "login"})
print(client.get("/events").json())               # [{'user_id': 1, 'action': 'login'}]

# Output:
# [{'user_id': 1, 'action': 'login'}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Giving a class variable the same name as a slot
✅ Correct: set defaults inside `__init__` (or use `dataclass(slots=True)`)

```python
# Wrong
try:
    class A:
        __slots__ = ("x",)
        x: int = 5                # ValueError: 'x' in __slots__ conflicts with class variable
except ValueError as e:
    print(e)
# Right
class B:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x: int = 5           # default set per instance
print(B().x)                      # 5
```

❌ Mistake 2: Forgetting that a subclass without `__slots__` gets a `__dict__`
✅ Correct: declare `__slots__ = ()` (or new names) in every subclass

```python
class Base:
    __slots__ = ("a",)
# Wrong - memory saving is lost
class Child1(Base):
    pass
# Right
class Child2(Base):
    __slots__ = ()
print(hasattr(Child1(), "__dict__"), hasattr(Child2(), "__dict__"))   # True False
```

❌ Mistake 3: Expecting weak references and multiple inheritance to just work
✅ Correct: add `"__weakref__"` when needed; do not combine two bases that both have non-empty slots

```python
import weakref
class A:
    __slots__ = ("x",)
# Wrong
try:
    weakref.ref(A())              # TypeError: cannot create weak reference to 'A' object
except TypeError as e:
    print(e)
# Right
class B:
    __slots__ = ("x", "__weakref__")
print(weakref.ref(B()) is not None)   # True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    __slots__ = ("x",)

class B(A):
    pass

b = B()
b.x = 1
b.y = 2
print(b.y, hasattr(b, "__dict__"))
a = A()
try:
    a.y = 2
except AttributeError:
    print("A blocked")
```
Answer: `2 True` then `A blocked`. `B` did not declare `__slots__`, so Python gives B instances a normal `__dict__` and `b.y = 2` works; `x` is still stored in A's slot. `A` itself is strict, so `a.y = 2` raises `AttributeError`. Slots are not enforced for subclasses that skip the declaration.

---

## ⚫ Interview Questions + Answers

Q1: What does `__slots__` do and why use it?
A1: It declares a fixed set of attributes, and CPython stores them in the object itself instead of in `__dict__`. Benefits: lower memory per instance (often 30-50% for small objects), faster attribute access, and protection against attribute typos.

Q2: What are the drawbacks?
A2: No dynamic attributes, no `__weakref__` unless added, no default values as class attributes with the same name, tricky multiple inheritance, and slightly harder pickling/copying in old protocols. Also it only pays off when you have many instances.

Q3: Does `__slots__` work with inheritance?
A3: Yes, but each subclass must declare its own `__slots__` (new names only) to stay dict-free. A subclass without it gets `__dict__`. Do not repeat parent slot names - it wastes memory.

Q4: How do `@dataclass(slots=True)` and `__slots__` relate?
A4: Since Python 3.10 the dataclass decorator can generate `__slots__` from the fields and return a new class. Note that because it creates a new class, `super()` without arguments in methods and class-level defaults can behave differently from hand-written slots.

Q5: Can you still have a `__dict__` with slots?
A5: Yes, put `"__dict__"` in the slots tuple. You then allow dynamic attributes while the listed ones stay fast. It is rarely worth it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You create very many small objects (ticks, points, events)
- You want strict attributes and early typo errors
- Memory is the bottleneck of a worker or data pipeline

❌ Avoid when:
- You only create a handful of objects
- You need dynamic attributes, monkey patching or heavy mocking
- You use Pydantic models (they manage storage themselves)
- You rely on multiple inheritance with several slotted bases

---

## 📊 Visual Diagram
```
Normal instance                      Slotted instance
+----------------+                   +----------------+
| object header  |                   | object header  |
| __dict__ ------+--> {"x":1,"y":2}  | x -> 1         |
| __weakref__    |    (hash table,   | y -> 2         |
+----------------+     ~300 bytes)   +----------------+
 object + dict                        one compact block

obj.z = 5   -> works                 obj.z = 5   -> AttributeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__slots__` | Fixed list of allowed attributes | allowed attributes की fixed list |
| `__dict__` | Per-instance attribute dictionary | हर instance की attribute dictionary |
| Descriptor | Object that controls attribute access | attribute access control करने वाला object |
| `__weakref__` | Slot that enables weak references | weak reference सक्षम करने वाला slot |
| Instance | One object created from a class | class से बना एक object |
| Memory footprint | Total memory used | कुल memory उपयोग |

---

## ⚡ 3-Line Summary
English: `__slots__` replaces the per-object dictionary with a fixed compact layout. It saves memory, speeds up attribute access and blocks typo attributes. Use it for huge numbers of small objects, and remember subclasses need their own `__slots__`.
Hindi: `__slots__` हर object की dictionary की जगह fixed compact layout देता है। इससे memory बचती है, attribute access तेज होता है और typo वाले attributes रुक जाते हैं। लाखों छोटे objects के लिए use करें, और याद रखें कि subclass को अपना `__slots__` चाहिए।

---

## ➡️ Next Topic
**109. Dataclasses** - generate `__init__`, `__repr__` and `__eq__` automatically for data-holding classes (and `slots=True` for memory savings).
