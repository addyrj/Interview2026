---

# 419. __slots__ Optimization
# हिंदी में: __slots__ Optimization (Memory बचाने की तकनीक)

---

## 🔵 Simple Definition (English)
`__slots__` tells Python to store an object's attributes in a small fixed array instead of a per-object `__dict__`. This cuts memory per object and makes attribute access a little faster. The price: you cannot add new attributes later.

## 🔵 सरल परिभाषा (Hindi)
`__slots__` Python को बताता है कि object के attributes हर object के अलग `__dict__` की जगह एक छोटे fixed array में रखे। इससे हर object की memory कम होती है और attribute access थोड़ा तेज होता है। कीमत: बाद में नए attributes नहीं जोड़ सकते।

---

## 🔴 Problem it Solves
By default every instance carries its own `__dict__` (a hash table). For one object this is fine, but for 1 million small objects (points, order rows, log records) the dicts waste hundreds of MB. Also, typos like `obj.nmae = 1` silently create a new attribute. `__slots__` removes the dict, saves memory, and turns typos into errors.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से हर instance के पास अपना `__dict__` (hash table) होता है। एक object के लिए यह ठीक है, लेकिन 10 लाख छोटे objects (points, order rows, log records) के लिए dicts सैकड़ों MB बर्बाद करते हैं। साथ ही `obj.nmae = 1` जैसी typo चुपचाप नया attribute बना देती है। `__slots__` dict हटाकर memory बचाता है और typo को error बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normal class: every object has a __dict__  {'x': 1, 'y': 2}
Step 2 → Declare __slots__ = ("x", "y") inside the class body
Step 3 → Python creates one descriptor per name on the CLASS (fixed offsets)
Step 4 → Each instance stores values in a compact array, no __dict__
Step 5 → Setting an attribute not in __slots__ raises AttributeError
Step 6 → Subclass must ALSO declare __slots__, else __dict__ comes back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सामान्य class: हर object के पास __dict__ होता है  {'x': 1, 'y': 2}
Step 2 → class body में __slots__ = ("x", "y") लिखो
Step 3 → Python CLASS पर हर नाम के लिए एक descriptor बनाता है (fixed offset)
Step 4 → हर instance values को compact array में रखता है, __dict__ नहीं होता
Step 5 → __slots__ में न लिखा attribute set करने पर AttributeError आता है
Step 6 → Subclass को भी __slots__ लिखना पड़ता है, वरना __dict__ वापस आ जाता है
```

---

## 🟡 Real World Example
A trading or analytics backend (Zerodha-style tick processing, a Swiggy order-event pipeline) keeps millions of tiny records in memory: `Tick(symbol, price, ts)`. Using `__slots__` (or `@dataclass(slots=True)`) lets the service hold far more rows in the same RAM and lowers garbage-collector pressure. A web route handler handling one request does not need it.

## 🟡 Real Example Hindi mein
Trading या analytics backend (Zerodha जैसा tick processing, Swiggy का order-event pipeline) memory में लाखों छोटे records रखता है: `Tick(symbol, price, ts)`। `__slots__` (या `@dataclass(slots=True)`) से उतनी ही RAM में कई गुना ज्यादा rows आ जाती हैं और garbage collector पर दबाव घटता है। एक request संभालने वाले route handler को इसकी जरूरत नहीं।

---

## 💻 Code Example — Basic
```python
# Basic __slots__ example
import sys                                    # to measure object size


class PointDict:
    def __init__(self, x: int, y: int) -> None:
        self.x = x                            # stored in per-instance __dict__
        self.y = y                            # stored in per-instance __dict__


class PointSlots:
    __slots__ = ("x", "y")                    # fixed attributes, no __dict__

    def __init__(self, x: int, y: int) -> None:
        self.x = x                            # stored in a fixed slot
        self.y = y                            # stored in a fixed slot


a: PointDict = PointDict(1, 2)                # normal object
b: PointSlots = PointSlots(1, 2)              # slotted object
print(hasattr(a, "__dict__"))                 # normal object has a dict
print(hasattr(b, "__dict__"))                 # slotted object has none
print(sys.getsizeof(a) + sys.getsizeof(a.__dict__) > sys.getsizeof(b))   # slots are smaller
try:                                          # try to add a new attribute
    b.z = 3                                   # not in __slots__
except AttributeError as e:                   # Python blocks it
    print("Error:", e)

# Output:
# True
# False
# True
# Error: 'PointSlots' object has no attribute 'z' and no __dict__ for setting new attributes
```

## 💻 Code Example — Advanced
```python
# Production style: measure memory of 100k objects, dataclass(slots=True), inheritance gotcha
import tracemalloc                            # measures memory allocated by Python
from dataclasses import dataclass             # dataclass helper


@dataclass
class OrderDict:
    order_id: int                             # id
    amount: float                             # price


@dataclass(slots=True)                        # Python 3.10+: generates __slots__ for us
class OrderSlots:
    order_id: int                             # id
    amount: float                             # price


def measure(cls: type, n: int = 100_000) -> float:
    """Return approximate MB used by n objects of cls."""
    tracemalloc.start()                       # begin tracking
    items = [cls(i, i * 1.5) for i in range(n)]   # build n objects
    current, _peak = tracemalloc.get_traced_memory()   # bytes now
    tracemalloc.stop()                        # stop tracking
    del items                                 # free objects
    return current / 1_000_000                # convert to MB


mb_dict: float = measure(OrderDict)           # normal dataclass
mb_slots: float = measure(OrderSlots)         # slotted dataclass
print(f"slots uses less memory: {mb_slots < mb_dict}")
print(f"dict={mb_dict:.1f} MB, slots={mb_slots:.1f} MB")


class Base:
    __slots__ = ("a",)                        # base has slots


class ChildNoSlots(Base):                     # forgot __slots__ in child
    pass


class ChildSlots(Base):
    __slots__ = ("b",)                        # child declares only NEW names


print(hasattr(ChildNoSlots(), "__dict__"))    # True: __dict__ is back!
print(hasattr(ChildSlots(), "__dict__"))      # False

o = OrderSlots(1, 9.5)                        # slotted dataclass
try:
    o.__dict__                                # no __dict__
except AttributeError:
    print("no __dict__")
try:
    import weakref                            # weak reference needs __weakref__ slot
    weakref.ref(o)                            # fails for plain slots
except TypeError as e:
    print("Error:", e)

# Output:
# slots uses less memory: True
# dict=15.2 MB, slots=11.2 MB
# True
# False
# no __dict__
# Error: cannot create weak reference to 'OrderSlots' object
```

Note: the exact MB numbers differ by machine and Python version (measured on Python 3.13). Savings come only from removing `__dict__`; the int and float objects themselves still cost memory, so expect roughly 20-40% saving here, not 90%. `@dataclass(slots=True)` needs Python 3.10+.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Fixed shape object | `__slots__` | class fields + V8 hidden classes (automatic) |
| Block new attributes | AttributeError with slots | `Object.seal()` / `Object.freeze()` |
| Memory per object | dict-based by default | V8 optimizes shape automatically |
| Opt in? | manual, per class | automatic |

```python
# Python way
class Point:
    __slots__ = ("x", "y")                   # fixed attributes only
    def __init__(self, x: int, y: int) -> None:
        self.x = x                           # stored in slot
        self.y = y                           # stored in slot
p = Point(1, 2)                              # no __dict__ created
```
```javascript
// JavaScript way
class Point {
  constructor(x, y) { this.x = x; this.y = y; }   // V8 gives all Points the same hidden class
}
const p = Object.seal(new Point(1, 2));           // seal: cannot add new properties
p.z = 3;                                          // silently ignored (throws in strict mode)
```

Key difference: JavaScript engines (V8) automatically share one hidden class between objects of the same shape, so you rarely think about memory layout. In Python, objects are dict-based by default and `__slots__` is a manual, opt-in optimization.

---

## 🟠 FastAPI Connection
FastAPI uses Pydantic models for request/response validation, so you normally do not add `__slots__` there. The place `__slots__` helps in a FastAPI service is internal data: millions of cached rows, in-memory event buffers, or parsed log lines. Keep Pydantic for the API boundary and use slotted dataclasses inside.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from dataclasses import dataclass
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


@dataclass(slots=True)                        # light internal row object
class Row:
    id: int
    name: str


@app.get("/rows")
def rows() -> list[dict[str, int | str]]:
    data = [Row(i, f"user{i}") for i in range(3)]          # many small objects
    return [{"id": r.id, "name": r.name} for r in data]    # convert for JSON


print(TestClient(app).get("/rows").json())

# Output:
# [{'id': 0, 'name': 'user0'}, {'id': 1, 'name': 'user1'}, {'id': 2, 'name': 'user2'}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `__slots__` in the subclass
✅ Correct: declare `__slots__` in every class of the chain (only NEW names)

```python
class Base:
    __slots__ = ("a",)
class Wrong(Base):                 # Wrong: gets a __dict__ again, memory saving lost
    pass
class Right(Base):
    __slots__ = ("b",)             # Right: only the new attribute, no repeat of "a"
```

❌ Mistake 2: Giving a slot a class-level default value
✅ Correct: set defaults inside `__init__`

```python
class Wrong:
    __slots__ = ("x",)
    x = 5                          # Wrong: ValueError: 'x' in __slots__ conflicts with class variable
class Right:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 5                 # Right: default set per instance
```

❌ Mistake 3: Using `__slots__` and then needing weak references or dynamic attributes
✅ Correct: add `"__weakref__"` (or `"__dict__"`) to `__slots__` when you really need them

```python
import weakref
class Wrong:
    __slots__ = ("x",)
# weakref.ref(Wrong())             # Wrong: TypeError: cannot create weak reference to 'Wrong' object
class Right:
    __slots__ = ("x", "__weakref__")   # Right: weakref allowed
weakref.ref(Right())
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    __slots__ = ("x",)                        # A has slots
class B(A):                                   # B forgets __slots__
    pass
b = B()
b.y = 1                                       # works?
print(hasattr(A(), "__dict__"), hasattr(b, "__dict__"))
try:
    class C:
        __slots__ = ("x",)
        x = 5                                 # class attr with same name
except ValueError as e:
    print(e)
```
Answer: First line: `False True`. `A` has slots so no `__dict__`, but `B` does not declare `__slots__`, so Python gives `B` a normal `__dict__`; `b.y = 1` therefore works and `hasattr(b, '__dict__')` is True. Second line: defining `C` raises `ValueError: 'x' in __slots__ conflicts with class variable` at class-creation time, because the slot descriptor and the class attribute `x` would clash.

---

## ⚫ Interview Questions + Answers

Q1: What does `__slots__` actually do?
A1: It replaces the per-instance `__dict__` with fixed-position storage. Python creates a descriptor on the class for each name. Instances become smaller and attribute access slightly faster, but you cannot add attributes not listed.

Q2: When is `__slots__` worth it?
A2: When you create very many instances (100k+) of a small class. Measure first with `tracemalloc` or `sys.getsizeof`. For a few objects it only adds restrictions.

Q3: What is the easiest way to use slots with dataclasses?
A3: `@dataclass(slots=True)` (Python 3.10+). It generates `__slots__` for you. Note that it creates a new class, so `super()` without arguments inside methods needs care, and default values work normally.

Q4: Does `__slots__` inherit?
A4: Partially. A subclass without `__slots__` gets a `__dict__` again. A subclass that declares `__slots__` should list only new names. Multiple inheritance from two classes that both have non-empty slots raises a layout conflict TypeError.

Q5: Does `__slots__` help pickling, weakrefs, or `vars(obj)`?
A5: No, it makes them harder: `vars(obj)` fails (no `__dict__`), weakrefs need `__weakref__` in slots, and old pickle protocols need `__getstate__`. Modern pickle (protocol 2+) handles slots automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You create hundreds of thousands of small, similar objects
- Records are fixed-shape (Tick, Point, LogLine)
- You want typos in attribute names to fail loudly
- Memory (RAM) is the bottleneck, proven by measurement

❌ Avoid when:
- Few objects: no visible benefit
- You need dynamic attributes, monkey patching, or `vars(obj)`
- Heavy multiple inheritance with other slotted classes
- You have not measured: avoid premature optimization

---

## 📊 Visual Diagram
```
Normal object                 Slotted object
+----------------+           +----------------+
| object header  |           | object header  |
| __dict__ ptr --+--> {x:1,  | x slot  -> 1   |
| __weakref__    |      y:2}  | y slot  -> 2   |
+----------------+  (hash    +----------------+
                     table)   no dict, no extra table

100,000 objects:  15.2 MB (dict)   vs   11.2 MB (slots)   <- numbers vary
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| __slots__ | Fixed list of allowed attributes | Allowed attributes की fixed list |
| __dict__ | Per-object attribute dictionary | हर object का attribute dictionary |
| Descriptor | Class-level object managing attribute access | Attribute access संभालने वाला class-level object |
| Hidden class | V8's automatic shape sharing | V8 का automatic shape sharing |
| tracemalloc | Stdlib memory tracker | Memory नापने वाला stdlib tool |

---

## ⚡ 3-Line Summary
English: `__slots__` stores attributes in fixed slots instead of a per-object dict, saving memory for millions of small objects. You cannot add new attributes, and subclasses must declare their own slots. Use `@dataclass(slots=True)` on Python 3.10+ and always measure first.
Hindi: `__slots__` attributes को हर object के dict की जगह fixed slots में रखता है, जिससे लाखों छोटे objects की memory बचती है। नए attributes नहीं जोड़ सकते और subclass को अपने slots खुद लिखने पड़ते हैं। Python 3.10+ पर `@dataclass(slots=True)` इस्तेमाल करें और पहले हमेशा measure करें।

---

## ➡️ Next Topic
**420. String Concatenation Performance** — why `+=` on strings in a loop is slow and how `''.join()` fixes it.
