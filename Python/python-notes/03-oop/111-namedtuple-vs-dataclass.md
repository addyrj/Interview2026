---

# 111. NamedTuple vs Dataclass
# हिंदी में: NamedTuple बनाम Dataclass (कौन सा कब चुनें)

---

## 🔵 Simple Definition (English)
Both give you a small class to hold related values with named fields. `NamedTuple` is an immutable tuple with names: you can unpack it, index it and use it as a dict key. `@dataclass` is a regular class with generated methods: mutable by default, flexible, and not a tuple.

## 🔵 सरल परिभाषा (Hindi)
दोनों named fields के साथ related values रखने वाली छोटी class देते हैं। `NamedTuple` नामों वाला immutable tuple है: इसे unpack, index और dict key की तरह use कर सकते हैं। `@dataclass` generated methods वाली सामान्य class है: default रूप से mutable, flexible, और tuple नहीं।

---

## 🔴 Problem it Solves
A plain tuple `(28.6, 77.2)` is compact but unclear: what is index 0? A plain dict is clear but heavy and has no type checking for keys. A hand-written class is clear but needs boilerplate. `NamedTuple` and `dataclass` both give names, type hints and a nice `repr` with almost no code. The problem for beginners is choosing: each has different behavior around mutability, unpacking, hashing, memory and inheritance.

## 🔴 यह क्यों बना? (Hindi)
सामान्य tuple `(28.6, 77.2)` compact है लेकिन अस्पष्ट: index 0 क्या है? सामान्य dict साफ है लेकिन भारी है और keys पर type checking नहीं। हाथ से लिखी class साफ है लेकिन boilerplate चाहिए। `NamedTuple` और `dataclass` दोनों बहुत कम code में नाम, type hints और अच्छा `repr` देते हैं। Beginners की दिक्कत चुनना है: mutability, unpacking, hashing, memory और inheritance में दोनों अलग व्यवहार करते हैं।

---

## 🟢 How it Works — Step by Step

```
NamedTuple                              dataclass
----------                              ---------
Step 1 → class P(NamedTuple): x: int    Step 1 → @dataclass class P: x: int
Step 2 → Python builds a tuple SUBCLASS Step 2 → Python writes __init__/__repr__/__eq__
Step 3 → fields = tuple positions       Step 3 → fields = instance attributes (__dict__)
Step 4 → p.x is p[0]; immutable         Step 4 → p.x = 5 allowed (unless frozen)
Step 5 → unpack: x, y = p               Step 5 → no unpack (unless you add __iter__)
Step 6 → hashable if values hashable    Step 6 → unhashable unless frozen=True
```

## 🟢 कैसे काम करता है? (Hindi)
```
NamedTuple                              dataclass
----------                              ---------
Step 1 → class P(NamedTuple): x: int    Step 1 → @dataclass class P: x: int
Step 2 → Python tuple का SUBCLASS बनाता है  Step 2 → Python __init__/__repr__/__eq__ लिखता है
Step 3 → fields = tuple की positions     Step 3 → fields = instance attributes (__dict__)
Step 4 → p.x ही p[0] है; immutable       Step 4 → p.x = 5 allowed (frozen न हो तो)
Step 5 → unpack: x, y = p               Step 5 → unpack नहीं (जब तक __iter__ न जोड़ें)
Step 6 → values hashable हों तो hashable   Step 6 → frozen=True के बिना unhashable
```

---

## 🟡 Real World Example
Map service: `Coordinate(lat, lng)` is a `NamedTuple` - immutable, used as a dict key for a cache, and unpacked as `lat, lng = c`. A DB driver returns rows as named tuples (`row.id`, `row.name`). Swiggy cart: `CartItem(sku, qty, price)` is a dataclass because qty changes while the user edits the cart, and it needs defaults and validation hooks.

## 🟡 Real Example Hindi mein
Map service में `Coordinate(lat, lng)` एक `NamedTuple` है - immutable, cache के dict key की तरह use होती है, और `lat, lng = c` से unpack होती है। DB driver rows को named tuples में लौटाता है (`row.id`, `row.name`)। Swiggy cart में `CartItem(sku, qty, price)` dataclass है क्योंकि user के edit करने पर qty बदलती है, और defaults व validation hooks चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic NamedTuple vs dataclass examples
from dataclasses import dataclass                 # dataclass decorator
from typing import NamedTuple                     # typed NamedTuple base


class CoordNT(NamedTuple):                        # immutable tuple with names
    lat: float                                    # field 0
    lng: float                                    # field 1
    label: str = "unknown"                        # fields can have defaults


@dataclass                                        # mutable class with generated methods
class CoordDC:
    lat: float                                    # attribute
    lng: float                                    # attribute
    label: str = "unknown"                        # default


nt: CoordNT = CoordNT(28.6, 77.2)                 # create NamedTuple
dc: CoordDC = CoordDC(28.6, 77.2)                 # create dataclass
print(nt, dc)                                     # both have a nice repr

lat, lng, label = nt                              # NamedTuple can be unpacked
print(lat, lng, label)                            # 28.6 77.2 unknown
print(nt[0], nt.lat, len(nt))                     # index, name, length all work

try:                                              # unpacking a dataclass
    a, b, c = dc                                  # dataclass is not iterable
except TypeError as e:                            # catch it
    print("dataclass:", e)                        # not iterable

dc.lat = 19.07                                    # dataclass is mutable
try:                                              # NamedTuple is immutable
    nt.lat = 19.07                                # not allowed
except AttributeError as e:                       # catch it
    print("namedtuple:", e)                       # can't set attribute

print(nt == (28.6, 77.2, "unknown"))              # NamedTuple equals a plain tuple!
print(dc == (28.6, 77.2, "unknown"))              # dataclass does not (different type)
print(nt._replace(label="Delhi"))                 # "copy with change" for NamedTuple
print(nt._asdict())                               # to dict
cache: dict = {nt: "cached"}                      # NamedTuple is hashable -> dict key
print(cache[CoordNT(28.6, 77.2)])                 # lookup works

# Output:
# CoordNT(lat=28.6, lng=77.2, label='unknown') CoordDC(lat=28.6, lng=77.2, label='unknown')
# 28.6 77.2 unknown
# 28.6 28.6 3
# dataclass: cannot unpack non-iterable CoordDC object
# namedtuple: can't set attribute
# True
# False
# CoordNT(lat=28.6, lng=77.2, label='Delhi')
# {'lat': 28.6, 'lng': 77.2, 'label': 'unknown'}
# cached
```

## 💻 Code Example — Advanced
```python
# Production style: memory, speed, frozen dataclass, methods, collections.namedtuple
import sys                                        # getsizeof
from collections import namedtuple               # older functional style
from dataclasses import dataclass                 # dataclass
from typing import NamedTuple                     # typed version


class Row(NamedTuple):                            # DB-row style record
    id: int                                       # primary key
    name: str                                     # user name
    balance: float                                # current balance

    def is_rich(self) -> bool:                    # NamedTuple can have methods
        return self.balance > 100_000             # simple business rule


@dataclass(frozen=True, slots=True)               # immutable + low memory (3.10+)
class FrozenRow:
    id: int
    name: str
    balance: float

    def is_rich(self) -> bool:                    # methods work the same way
        return self.balance > 100_000


@dataclass(slots=True)                            # mutable + slots
class MutableRow:
    id: int
    name: str
    balance: float


r1: Row = Row(1, "Amit", 250_000.0)               # build one of each
r2: FrozenRow = FrozenRow(1, "Amit", 250_000.0)
r3: MutableRow = MutableRow(1, "Amit", 250_000.0)
print(r1.is_rich(), r2.is_rich())                 # True True
print(sys.getsizeof(r1), sys.getsizeof(r2))       # size in bytes (CPython 3.13: 64 and 56)

id_, name, balance = r1                           # unpack NamedTuple in loops
rows: list[Row] = [Row(1, "A", 10.0), Row(2, "B", 50.0), Row(3, "C", 20.0)]
print(max(rows, key=lambda r: r.balance).name)    # B
print(sorted(rows, key=lambda r: r.balance)[0])   # smallest by balance
print(sorted([Row(2, "x", 0), Row(1, "y", 0)]))   # tuples sort by field order automatically

r3.balance += 500                                 # mutable dataclass supports updates
print(r3)                                         # updated in place

try:                                              # frozen dataclass blocks changes too
    r2.balance = 0                                # not allowed
except Exception as e:                            # FrozenInstanceError
    print(type(e).__name__)                       # name only (message varies)

Legacy = namedtuple("Legacy", ["a", "b"])         # pre-3.6 style, no type hints
print(Legacy(1, 2), Legacy._fields)               # fields are available as a tuple

# Gotcha: NamedTuple equals any tuple with the same values
class A(NamedTuple):                              # two different "types"
    v: int
class B(NamedTuple):
    v: int
print(A(1) == B(1))                               # True (both are just (1,))

# Output:
# True True
# 64 56
# B
# Row(id=1, name='A', balance=10.0)
# [Row(id=1, name='y', balance=0), Row(id=2, name='x', balance=0)]
# MutableRow(id=1, name='Amit', balance=250500.0)
# FrozenInstanceError
# Legacy(a=1, b=2) ('a', 'b')
# True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Immutable named record | `NamedTuple` / `frozen` dataclass | `Object.freeze({x, y})` |
| Mutable record | `@dataclass` | plain object / class |
| Destructure | `x, y = p` (NamedTuple) | `const {x, y} = p` |
| Equality | by value | by reference (`===`) |
| Dict key | hashable ones work | must `JSON.stringify` or use a string key |

```python
# Python way
from typing import NamedTuple

class Point(NamedTuple):
    x: int                                    # field
    y: int                                    # field

p: Point = Point(1, 2)
x, y = p                                      # positional unpack
seen: set = {Point(1, 2)}                     # value-based set membership
print(Point(1, 2) in seen)                    # True
```
```javascript
// JavaScript way
const p = Object.freeze({ x: 1, y: 2 });     // frozen object
const { x, y } = p;                          // destructure by name
const seen = new Set([p]);
console.log(seen.has({ x: 1, y: 2 }));       // false - different object reference
```

Key difference: JS destructures by name, Python NamedTuple unpacks by position. In Python, equal values mean equal records and the same hash, so Sets and dict keys work naturally; in JS you must serialize to a string.

---

## 🟠 FastAPI Connection
FastAPI accepts `NamedTuple` as a query/body type in some cases, but the clean pattern is: Pydantic at the API edge, then `NamedTuple` or `dataclass` inside for internal records. NamedTuples are good for repository results (SQLAlchemy rows are named-tuple-like) and as cache keys, frozen dataclasses for settings and value objects.

```python
# FastAPI example - NamedTuple as cache key, dataclass as internal record
from typing import NamedTuple                     # immutable cache key
from dataclasses import dataclass                 # mutable internal record
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # tests


class CacheKey(NamedTuple):                       # hashable -> usable in dict
    city: str
    day: str


@dataclass                                        # changes as requests arrive
class Stats:
    hits: int = 0


app: FastAPI = FastAPI()                          # create app
cache: dict[CacheKey, str] = {}                   # in-memory cache
stats: Stats = Stats()                            # shared counter


@app.get("/weather")                              # GET /weather?city=Pune&day=mon
def weather(city: str, day: str) -> dict[str, object]:
    key: CacheKey = CacheKey(city.lower(), day)   # normalized key
    if key in cache:                              # cache hit
        stats.hits += 1                           # update counter
        return {"data": cache[key], "hits": stats.hits}
    cache[key] = f"sunny in {city}"               # fake lookup
    return {"data": cache[key], "hits": stats.hits}


client: TestClient = TestClient(app)              # client
print(client.get("/weather", params={"city": "Pune", "day": "mon"}).json())
print(client.get("/weather", params={"city": "PUNE", "day": "mon"}).json())

# Output:
# {'data': 'sunny in Pune', 'hits': 0}
# {'data': 'sunny in Pune', 'hits': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to modify a NamedTuple
✅ Correct: use `_replace` to create a changed copy, or choose a dataclass

```python
from typing import NamedTuple
class P(NamedTuple):
    x: int
p = P(1)
# Wrong
try:
    p.x = 2
except AttributeError as e:
    print(e)              # can't set attribute
# Right
p = p._replace(x=2)
print(p)                  # P(x=2)
```

❌ Mistake 2: Relying on a mutable dataclass as a dict key / set member
✅ Correct: use `frozen=True` (or NamedTuple)

```python
from dataclasses import dataclass
@dataclass
class A:
    x: int
# Wrong
try:
    {A(1)}
except TypeError as e:
    print(e)              # unhashable type: 'A'
# Right
@dataclass(frozen=True)
class B:
    x: int
print({B(1)})             # {B(x=1)}
```

❌ Mistake 3: Comparing NamedTuples of different types, or with plain tuples
✅ Correct: compare `type(a) is type(b)` too, or use a dataclass where the type matters

```python
from typing import NamedTuple
class Meter(NamedTuple):
    v: float
class Feet(NamedTuple):
    v: float
# Wrong - unit mix-up goes unnoticed
print(Meter(3) == Feet(3))        # True
# Right
from dataclasses import dataclass
@dataclass(frozen=True)
class M:
    v: float
@dataclass(frozen=True)
class F:
    v: float
print(M(3) == F(3))               # False
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from typing import NamedTuple

class P(NamedTuple):
    x: int
    tags: list

p = P(1, ["a"])
p.tags.append("b")
print(p)
try:
    hash(p)
except TypeError as e:
    print("unhashable")
x, t = p
print(len(p), p == (1, ["a", "b"]))
```
Answer: `P(x=1, tags=['a', 'b'])`, then `unhashable`, then `2 True`. A NamedTuple is immutable only shallowly: the tuple slots cannot be rebound, but the list inside is a mutable object and can change. Because a tuple's hash is built from its items' hashes and a list is unhashable, `hash(p)` raises TypeError. The tuple has two items, so `len(p)` is 2, and it equals the plain tuple `(1, ['a', 'b'])`.

---

## ⚫ Interview Questions + Answers

Q1: Main differences between NamedTuple and dataclass?
A1: NamedTuple is an immutable tuple subclass: supports unpacking, indexing, iteration, hashing and equals plain tuples. Dataclass is a normal class: mutable by default, attribute access only, richer options (`field()`, `__post_init__`, `slots`, `kw_only`, inheritance with new fields).

Q2: Which uses less memory or is faster?
A2: A NamedTuple has no `__dict__` and is stored like a tuple, so it is small and fast to create. A plain dataclass has a `__dict__`; `@dataclass(slots=True)` closes most of the gap. Measure before optimizing.

Q3: When do you choose a frozen dataclass over NamedTuple?
A3: When you do not want it to behave like a tuple (no accidental unpacking or equality with tuples), when you need `__post_init__` validation, defaults with `default_factory`, or inheritance that adds fields.

Q4: What is `collections.namedtuple` and how is it different from `typing.NamedTuple`?
A4: `namedtuple("P", ["x", "y"])` is the old function form without type hints. `typing.NamedTuple` is the class form with annotations, defaults and methods. Both create the same kind of tuple subclass.

Q5: Can NamedTuple be used for database rows?
A5: Yes. Many drivers return rows as named tuples (`cursor` with `namedtuple_row`, SQLAlchemy `Row`). They are cheap, support `row.id` and unpacking, and are read-only, which is what you want for query results.

---

## 🔷 When to Use + When Not to Use
✅ Use NamedTuple when:
- The record is small, immutable, and may be unpacked or used as a dict key
- You return multiple values from a function with names
- You map DB rows or CSV lines

✅ Use dataclass when:
- Fields change over time, or need defaults/validation hooks
- You need inheritance that adds fields, or `kw_only`
- You do not want tuple behavior

❌ Avoid both when:
- You need runtime validation of untrusted input (use Pydantic)
- You need behavior-heavy objects (write a normal class)

---

## 📊 Visual Diagram
```
                     NamedTuple              dataclass
isinstance tuple?    yes                     no
mutable?             no                      yes (frozen=True -> no)
unpack x, y = p      yes                     no
index p[0]           yes                     no
hashable?            if items hashable       only if frozen
equals plain tuple?  yes (gotcha)            no
__dict__ ?           no                      yes (unless slots=True)
defaults / methods   yes                     yes, plus field(), __post_init__
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| NamedTuple | Tuple whose positions have names | नाम वाले positions का tuple |
| Immutable | Cannot be changed after creation | बनने के बाद बदला नहीं जा सकता |
| Unpacking | `a, b = pair` | tuple को variables में बांटना |
| Hashable | Can be a dict key / set member | dict key / set member बन सकता है |
| `_replace` | Copy a NamedTuple with changes | बदलाव के साथ copy बनाना |
| Value object | Compared by content, not identity | content से compare होने वाला object |

---

## ⚡ 3-Line Summary
English: NamedTuple is an immutable, unpackable, hashable record; dataclass is a flexible, mutable class with generated methods. Pick NamedTuple for small read-only records and keys, dataclass for changing data and richer features. Use `frozen=True, slots=True` for a safe, light dataclass.
Hindi: NamedTuple immutable, unpack होने वाला, hashable record है; dataclass flexible, mutable class है जिसके methods अपने-आप बनते हैं। छोटे read-only records और keys के लिए NamedTuple, बदलने वाले data और ज्यादा features के लिए dataclass चुनें। सुरक्षित और हल्के dataclass के लिए `frozen=True, slots=True` use करें।

---

## ➡️ Next Topic
**112. Metaclasses Basics** - the class of a class: how `type` creates classes and how to customize class creation.
