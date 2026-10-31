---

# 014. Python Data Types Overview
# हिंदी में: Python Data Types का Overview

---

## 🔵 Simple Definition (English)
A data type tells Python what kind of value an object holds and what you can do with it. Python's built-in types are: numbers (`int`, `float`, `complex`), `bool`, text (`str`), bytes, sequences (`list`, `tuple`, `range`), mappings (`dict`), sets (`set`, `frozenset`) and `None`. Everything in Python is an object of some type.

## 🔵 सरल परिभाषा (Hindi)
Data type बताता है कि object में किस तरह की value है और उसके साथ क्या किया जा सकता है। Python के built-in types: numbers (`int`, `float`, `complex`), `bool`, text (`str`), bytes, sequences (`list`, `tuple`, `range`), mapping (`dict`), sets (`set`, `frozenset`) और `None`। Python में सब कुछ किसी न किसी type का object है।

---

## 🔴 Problem it Solves
Computers store only bits. Types give meaning: `65` as an int is a number, as text it is the letter "A". Without types you could not know whether `+` should add or join, or whether an item can be changed or used as a dictionary key. Good type knowledge prevents bugs such as mutating shared lists or using a list as a dict key.

## 🔴 यह क्यों बना? (Hindi)
Computer सिर्फ bits रखता है। Types उन्हें मतलब देते हैं: `65` int है तो संख्या, text है तो अक्षर "A"। Types के बिना पता नहीं चलता कि `+` जोड़ेगा या चिपकाएगा, या item बदला जा सकता है या dict key बन सकता है। Types की समझ से bugs बचते हैं, जैसे shared list को mutate करना या list को dict key बनाना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a value (literal):  42, 3.14, "hi", [1,2], {"a":1}
Step 2 → Python builds an object and attaches its type automatically
Step 3 → type(obj) tells you the class; isinstance(obj, T) checks it
Step 4 → The type decides: allowed operations, mutability, hashability
Step 5 → Operations on the wrong type raise TypeError at runtime

THE MAP OF BUILT-IN TYPES
Numbers   : int  float  complex          (immutable)
Boolean   : bool                         (immutable, subclass of int)
Text      : str                          (immutable)
Binary    : bytes (immutable)  bytearray (mutable)
Sequences : list (mutable)  tuple (immutable)  range (immutable)
Mapping   : dict                         (mutable, keys must be hashable)
Sets      : set (mutable)  frozenset (immutable)
Nothing   : NoneType  (the single value None)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप value लिखते हैं (literal): 42, 3.14, "hi", [1,2], {"a":1}
Step 2 → Python object बनाती है और type अपने आप जोड़ देती है
Step 3 → type(obj) class बताता है; isinstance(obj, T) जाँचता है
Step 4 → Type तय करता है: कौन-से operations चलेंगे, mutable है या नहीं, hashable है या नहीं
Step 5 → गलत type पर operation करने से runtime पर TypeError आता है

Immutable: int, float, complex, bool, str, bytes, tuple, frozenset, range, None
Mutable  : list, dict, set, bytearray
```

---

## 🟡 Real World Example
A Razorpay-style payment record in Python mixes many types: `amount` is an `int` in paise (never float for money), `currency` is a `str`, `captured` is a `bool`, `refunds` is a `list` of dicts, `notes` is a `dict`, `error` is `None` when all is fine, and `allowed_methods` is a `set` (fast membership test). Choosing the right type decides correctness and speed.

## 🟡 Real Example Hindi mein
Razorpay जैसे payment record में कई types मिलते हैं: `amount` paise में `int` (पैसों के लिए float कभी नहीं), `currency` `str`, `captured` `bool`, `refunds` dicts की `list`, `notes` `dict`, सब ठीक हो तो `error` `None`, और `allowed_methods` एक `set` (तेज़ membership test)। सही type चुनना correctness और speed दोनों तय करता है।

---

## 💻 Code Example — Basic
```python
# Basic: one value of every built-in type
values: list[object] = [  # a list holding objects of many types
    42,  # int
    3.14,  # float
    2 + 3j,  # complex
    True,  # bool
    "hello",  # str
    b"hi",  # bytes
    [1, 2, 3],  # list
    (1, 2, 3),  # tuple
    range(3),  # range
    {"k": 1},  # dict
    {1, 2, 3},  # set
    frozenset({1, 2}),  # frozenset
    None,  # NoneType
]

for v in values:  # loop over every sample value
    print(f"{type(v).__name__:<10} {v!r}")  # type name padded, then repr of value
# Output:
# int        42
# float      3.14
# complex    (2+3j)
# bool       True
# str        'hello'
# bytes      b'hi'
# list       [1, 2, 3]
# tuple      (1, 2, 3)
# range      range(0, 3)
# dict       {'k': 1}
# set        {1, 2, 3}
# frozenset  frozenset({1, 2})
# NoneType   None
```

## 💻 Code Example — Advanced
```python
# Advanced: classify mutability and hashability programmatically
from __future__ import annotations  # modern hints on all 3.x

from collections.abc import Hashable  # abstract base class for hashable objects
from typing import Any  # "any type" hint


def is_hashable(obj: Any) -> bool:
    """Hashable objects can be dict keys and set members."""
    return isinstance(obj, Hashable) and _try_hash(obj)  # also check tuple contents


def _try_hash(obj: Any) -> bool:
    try:
        hash(obj)  # tuples containing lists fail here
        return True  # hashing worked
    except TypeError:  # unhashable
        return False


def is_mutable(obj: Any) -> bool:
    """Practical check: try to change a copy of the object."""
    return isinstance(obj, (list, dict, set, bytearray))  # the mutable built-ins


samples: dict[str, Any] = {
    "int": 5,
    "str": "abc",
    "tuple": (1, 2),
    "tuple_with_list": (1, [2]),
    "list": [1],
    "dict": {"a": 1},
    "set": {1},
    "frozenset": frozenset({1}),
}
for label, obj in samples.items():  # report on each sample
    print(f"{label:<16} mutable={is_mutable(obj)!s:<5} hashable={is_hashable(obj)}")
# Output:
# int              mutable=False hashable=True
# str              mutable=False hashable=True
# tuple            mutable=False hashable=True
# tuple_with_list  mutable=False hashable=False
# list             mutable=True  hashable=False
# dict             mutable=True  hashable=False
# set              mutable=True  hashable=False
# frozenset        mutable=False hashable=True

# Real use: a dict key must be hashable, so a tuple works but a list does not
grid: dict[tuple[int, int], str] = {(0, 0): "start", (2, 3): "goal"}  # tuple keys
print(grid[(2, 3)])  # Output: goal
try:
    bad = {[1, 2]: "x"}  # type: ignore[dict-item]  # list as a key
except TypeError as exc:  # Python refuses
    print(exc)  # Output: unhashable type: 'list'

# bool is a subclass of int (a classic trap)
print(isinstance(True, int), True + True)  # Output: True 2
```

---

## 🟠 JavaScript vs Python Comparison
JS has 7 primitives (`number`, `string`, `boolean`, `null`, `undefined`, `symbol`, `bigint`) plus objects. Python has more specific built-in types. JS has ONE number type (float64); Python separates `int` (unlimited size), `float` and `complex`. JS arrays ~ Python `list`; JS objects used as maps ~ Python `dict`; JS `Set` ~ Python `set`. Python has `tuple` and `None` (single "no value"; JS has both `null` and `undefined`).

```python
# Python
print(type(5), type(5.0))  # <class 'int'> <class 'float'>  (two types)
print(2 ** 100)  # 1267650600228229401496703205376 (ints never overflow)
scores = [90, 85]  # list  (JS array)
user = {"name": "Asha"}  # dict  (JS object / Map)
point = (3, 4)  # tuple (no JS equivalent; immutable sequence)
```
```javascript
// JavaScript
console.log(typeof 5, typeof 5.0); // number number  (one type)
console.log(2 ** 100); // 1.2676506002282294e+30 (loses precision)
const scores = [90, 85]; // array
const user = { name: "Asha" }; // object
const point = Object.freeze([3, 4]); // closest thing to a tuple
```

---

## 🟠 FastAPI Connection
FastAPI maps Python types to JSON and OpenAPI types: `int` to integer, `float` to number, `str` to string, `bool` to boolean, `list[int]` to array, `dict[str, int]` to object, `None` to null. `X | None` marks a field optional. Using the correct type in your function signature or Pydantic model gives automatic validation and docs.

```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # data validation models

app: FastAPI = FastAPI()  # app object


class Payment(BaseModel):
    amount: int  # paise, never float for money
    currency: str = "INR"  # text with default
    captured: bool = False  # JSON true/false
    tags: list[str] = []  # JSON array of strings
    note: str | None = None  # optional, JSON null allowed


@app.post("/payments")  # POST /payments
def create(p: Payment) -> Payment:  # body is validated against Payment
    return p  # sends the validated object back as JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `float` for money
```python
# Wrong:
print(0.1 + 0.2)  # 0.30000000000000004
# Right: integers (paise) or Decimal
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))  # 0.3
```
✅ Correct: store money as integer paise/cents or `Decimal`.

❌ Mistake 2: Using a mutable object as a dict key or default argument
```python
# Wrong:
# d = {[1, 2]: "x"}            # TypeError: unhashable type: 'list'
# def add(item, bucket=[]):    # the same list is shared across calls!
# Right:
d = {(1, 2): "x"}  # tuple key works
def add(item: int, bucket: list[int] | None = None) -> list[int]:
    bucket = [] if bucket is None else bucket  # fresh list each call
    bucket.append(item)
    return bucket
```
✅ Correct: use tuples/frozensets as keys and `None` as the default for mutable arguments.

❌ Mistake 3: Mixing up empty `{}`
```python
# Wrong: s = {}   # this is a dict, not a set!
# Right: s = set()   # empty set
print(type({}).__name__, type(set()).__name__)  # dict set
```
✅ Correct: `{}` is an empty dict; use `set()` for an empty set.

---

## 🧠 Tricky Interview Question

```python
# What will this output?
t = (1, 2, [3, 4])
t[2].append(5)
print(t)
t[2] += [6]
```
Answer: The first print shows `(1, 2, [3, 4, 5])`: a tuple is immutable, but it only holds references, and the list inside is still mutable. Then `t[2] += [6]` does two steps: the list is extended in place (so it becomes `[3, 4, 5, 6]`), and then Python tries to assign it back into the tuple slot, which raises `TypeError: 'tuple' object does not support item assignment`. After the error, `t` is already `(1, 2, [3, 4, 5, 6])`. So: the exception happens AND the change still occurs.

---

## ⚫ Interview Questions + Answers

Q1: Which built-in types are mutable and which are immutable?
A1: Mutable: `list`, `dict`, `set`, `bytearray`. Immutable: `int`, `float`, `complex`, `bool`, `str`, `bytes`, `tuple`, `frozenset`, `range`, `None`. Immutable objects are safe to share and can be hashed (if their contents are hashable too), which is why they work as dict keys.

Q2: What is the difference between a list and a tuple?
A2: A list is mutable, usually for a collection of similar items that changes; a tuple is immutable, usually a fixed record of mixed items (like a coordinate `(lat, lng)`). Tuples are slightly smaller and faster, and hashable when their elements are hashable, so they can be dict keys.

Q3: What is the difference between `set` and `dict`?
A3: A `set` stores unique hashable values with no order guarantee for lookups; `{1, 2}`. A `dict` maps unique hashable keys to values and keeps insertion order (guaranteed since 3.7). Both use hash tables, so lookup is O(1) on average.

Q4: Why is `bool` considered a subclass of `int`?
A4: Historical design: `True == 1` and `False == 0`, so `True + True` is `2` and `sum([True, False, True])` is `2` (handy for counting). The trap: `isinstance(True, int)` is `True`, so check for `bool` before `int` when branching on types.

Q5: How do you check or convert types?
A5: `type(x)` returns the exact class; `isinstance(x, (int, float))` accepts subclasses and is preferred. Convert with constructors: `int("42")`, `str(42)`, `list("abc")`, `set([1, 1, 2])`, `float("3.5")`. Invalid conversions raise `ValueError` (`int("abc")`).

---

## 🔷 When to Use + When Not to Use
✅ Use when choosing:
- `list` for ordered, changeable collections; `tuple` for fixed records
- `dict` for lookups by key; `set` for uniqueness and fast membership
- `Decimal` or integer paise for money; `str` for text; `bytes` for binary data

❌ Avoid when:
- `float` for money or exact comparison (`==`)
- `list` for membership tests on big data (use a `set`)
- Mutable objects as dict keys or default arguments

---

## 📊 Visual Diagram
```
                    Python objects
        ┌──────────────┬──────────────┬─────────────────┐
        ▼              ▼              ▼                 ▼
    Numbers          Text         Collections         Other
  int float         str bytes    ┌─────────────┐     bool  None
  complex                         │ Sequences   │
                                  │ list tuple  │
   IMMUTABLE ◄────────────────    │ range       │ ──► list = MUTABLE
   int float str bytes tuple      │ Mapping     │     tuple = immutable
   frozenset bool None            │ dict        │
                                  │ Sets        │
   MUTABLE: list dict set         │ set frozenset│
                                  └─────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot change after creation | बनने के बाद बदल नहीं सकता |
| Mutable | Can change in place | जगह पर बदल सकता है |
| Hashable | Has a fixed hash; usable as key | Fixed hash वाला; key बन सकता है |
| Sequence | Ordered, indexable collection | Ordered, index वाला collection |
| Mapping | Key-to-value collection | Key से value वाला collection |
| `NoneType` | Type of `None` | `None` का type |

---

## ⚡ 3-Line Summary
English: Python has built-in numeric, text, sequence, mapping, set, bool and None types, and every value is an object with a type. Know which are mutable and hashable, because that decides dict keys, shared-state bugs and safe defaults. Use `isinstance` for checks and `Decimal` or integers for money.
Hindi: Python में numeric, text, sequence, mapping, set, bool और None जैसे built-in types हैं, और हर value किसी type का object है। जानें कौन mutable और hashable है, क्योंकि dict keys, shared-state bugs और safe defaults इसी से तय होते हैं। Checks के लिए `isinstance` और पैसों के लिए `Decimal` या integers use करें।

---

## ➡️ Next Topic
**015. int + float + complex** — numbers in depth: precision, big ints, rounding and complex numbers.
