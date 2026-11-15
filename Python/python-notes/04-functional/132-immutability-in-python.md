---

# 132. Immutability in Python
# हिंदी में: Python में Immutability (जो बदला नहीं जा सकता)

---

## 🔵 Simple Definition (English)
An immutable object cannot be changed after it is created. `int`, `float`, `str`, `tuple`, `frozenset`, `bytes` and `bool` are immutable. A "change" actually creates a NEW object. Mutable objects (`list`, `dict`, `set`) can be modified in place.

## 🔵 सरल परिभाषा (Hindi)
Immutable object बनने के बाद बदला नहीं जा सकता। `int`, `float`, `str`, `tuple`, `frozenset`, `bytes` और `bool` immutable हैं। "बदलाव" असल में NEW object बनाता है। Mutable objects (`list`, `dict`, `set`) उसी जगह बदले जा सकते हैं।

---

## 🔴 Problem it Solves
Shared mutable data causes bugs: a function changes a list that the caller still uses, a default argument remembers old data, two threads modify a dict at once, a cache key changes after insertion. Immutable values are safe to share, hash, cache and pass across threads, because nobody can change them behind your back.

## 🔴 यह क्यों बना? (Hindi)
Shared mutable data bugs पैदा करता है: function उस list को बदल देता है जो caller अभी भी use कर रहा है, default argument पुराना data याद रखता है, दो threads एक साथ dict बदलते हैं, insert के बाद cache key बदल जाती है। Immutable values को share, hash, cache और threads के बीच भेजना सुरक्षित है क्योंकि कोई उन्हें चुपके से नहीं बदल सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every object has an identity (id), a type and a value
Step 2 → Immutable: the value can never change while the object lives
Step 3 → s = s + "x" builds a NEW str and re-points the name s
Step 4 → Immutable objects with immutable contents are hashable -> usable as dict keys
Step 5 → A tuple is immutable but can HOLD a mutable list (shallow immutability)
Step 6 → Make your own: @dataclass(frozen=True), NamedTuple, __slots__ + no setters

x = (1, [2, 3]);  x[1].append(4)  works!   x[0] = 9  fails
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर object की identity (id), type और value होती है
Step 2 → Immutable: object के जीवित रहते value कभी नहीं बदलती
Step 3 → s = s + "x" NEW str बनाता है और नाम s को उस पर point करता है
Step 4 → Immutable contents वाले immutable objects hashable होते हैं -> dict key बन सकते हैं
Step 5 → Tuple immutable है पर उसमें mutable list रह सकती है (shallow immutability)
Step 6 → अपना बनाएं: @dataclass(frozen=True), NamedTuple, __slots__ + कोई setter नहीं
```

---

## 🟡 Real World Example
A Razorpay `Money(amount, currency)` object is frozen so a bug cannot change a paid amount after creation. Cache keys like `(user_id, "profile")` are tuples. App settings are loaded once into a frozen dataclass and shared by all requests/threads. Event-sourcing systems store immutable events that are never edited, only appended.

## 🟡 Real Example Hindi mein
Razorpay का `Money(amount, currency)` object frozen है ताकि कोई bug बनने के बाद paid amount न बदल सके। Cache keys जैसे `(user_id, "profile")` tuples हैं। App settings एक बार frozen dataclass में load होकर सभी requests/threads में साझा होती हैं। Event-sourcing systems immutable events रखते हैं जो कभी edit नहीं होते, सिर्फ जुड़ते हैं।

---

## 💻 Code Example — Basic
```python
# Basic immutability
s: str = "hello"                                   # strings are immutable
try:                                               # trying to change a character
    s[0] = "H"                                     # item assignment not allowed
except TypeError as e:                             # catch it
    print("Error:", e)                             # explains the rule

old_id: int = id(s)                                # remember identity
s += " world"                                      # creates a NEW string
print(s, id(s) != old_id)                          # name now points to a new object

t: tuple[int, int] = (1, 2)                        # tuple is immutable
try:                                               # trying to change an item
    t[0] = 9                                       # not allowed
except TypeError as e:
    print("Error:", e)

lst: list[int] = [1, 2]                            # list is mutable
alias = lst                                        # same object, second name
alias.append(3)                                    # change through the alias
print(lst)                                         # original sees the change

mixed = (1, [2, 3])                                # immutable container, mutable content
mixed[1].append(4)                                 # allowed: the LIST changes, not the tuple
print(mixed)                                       # (1, [2, 3, 4])

print({(1, 2): "ok"})                              # tuple works as a dict key
try:                                               # list cannot be a key
    {[1, 2]: "bad"}                                # unhashable
except TypeError as e:
    print("Error:", e)

fs = frozenset({1, 2})                             # immutable set
print(fs | {3}, type(fs | {3}).__name__)           # operations return NEW frozensets

# Output:
# Error: 'str' object does not support item assignment
# hello world True
# Error: 'tuple' object does not support item assignment
# [1, 2, 3]
# (1, [2, 3, 4])
# {(1, 2): 'ok'}
# Error: unhashable type: 'list'
# frozenset({1, 2, 3}) frozenset
```

## 💻 Code Example — Advanced
```python
# Production style: frozen dataclass, NamedTuple, MappingProxyType, safe updates
from dataclasses import dataclass, replace, FrozenInstanceError   # frozen records
from types import MappingProxyType                 # read-only dict view
from typing import NamedTuple                      # immutable tuple with names


@dataclass(frozen=True, slots=True)                # frozen: no attribute assignment
class Money:
    amount: int                                    # paise (never use floats for money)
    currency: str = "INR"                          # currency code

    def add(self, other: "Money") -> "Money":
        if other.currency != self.currency:        # protect from mixing currencies
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)   # NEW object


price = Money(10_000)                              # 100.00 INR
try:                                               # attempt to tamper
    price.amount = 1                               # blocked
except FrozenInstanceError as e:                   # dataclasses raises this
    print("Error:", type(e).__name__)
total = price.add(Money(500))                      # returns a new object
print(price, total)                                # original unchanged
print(replace(total, currency="USD"))              # copy with one field changed
print(hash(price) == hash(Money(10_000)))          # frozen dataclass is hashable by value
print({price: "cached"}[Money(10_000)])            # usable as a dict key


class Point(NamedTuple):
    x: int                                         # named, immutable fields
    y: int


p = Point(1, 2)                                    # create
print(p, p.x, p._replace(x=5))                     # _replace returns a copy


_DEFAULTS = {"timeout": 5, "retries": 3}           # private mutable dict
CONFIG = MappingProxyType(_DEFAULTS)               # read-only view for everyone else
try:
    CONFIG["timeout"] = 99                         # cannot assign through the view
except TypeError as e:
    print("Error:", e)

_DEFAULTS["timeout"] = 10                          # the view reflects the owner's change
print(CONFIG["timeout"])                           # 10 -> view is read-only, not frozen


def add_item(cart: tuple[str, ...], item: str) -> tuple[str, ...]:
    """Immutable update: return a new tuple instead of changing the old one."""
    return (*cart, item)                           # unpacking builds a new tuple


c1 = ("pen",)                                      # first cart
c2 = add_item(c1, "book")                          # second cart
print(c1, c2)                                      # both versions exist (undo is trivial)

# Output:
# Error: FrozenInstanceError
# Money(amount=10000, currency='INR') Money(amount=10500, currency='INR')
# Money(amount=10500, currency='USD')
# True
# cached
# Point(x=1, y=2) 1 Point(x=5, y=2)
# Error: 'mappingproxy' object does not support item assignment
# 10
# ('pen',) ('pen', 'book')
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Immutable primitives | `int float str bool bytes tuple frozenset` | `number string boolean` (strings immutable) |
| Immutable containers | `tuple`, `frozenset` | arrays/objects mutable |
| Freeze an object | `@dataclass(frozen=True)` | `Object.freeze(obj)` (shallow) |
| Constant | convention `UPPER_CASE` (not enforced) | `const` (binding only) |
| Read-only dict | `MappingProxyType` | `Object.freeze` |

```python
# Python way
from dataclasses import dataclass
@dataclass(frozen=True)
class User:
    name: str
u = User("Asha")
# u.name = "X"  -> FrozenInstanceError
```
```javascript
// JavaScript way
const u = Object.freeze({ name: "Asha" });         // shallow freeze
u.name = "X";                                      // silently ignored (throws in strict mode)
const arr = [1, 2];
arr.push(3);                                       // const does NOT make arrays immutable!
```

Key difference: JS `const` only stops re-assignment of the name; objects stay mutable unless frozen. Python has no `const` at all, but `tuple`/`frozenset`/frozen dataclasses give real immutability, and failed changes raise errors loudly.

---

## 🟠 FastAPI Connection
FastAPI settings and shared config should be immutable: read once, reused by every request and thread. Pydantic models can be frozen with `model_config = ConfigDict(frozen=True)`. Immutable response models also make caching safe. Never use a mutable default like `def route(tags: list = [])`; use `None` or `Field(default_factory=list)`.

```python
# FastAPI example — frozen config shared across requests
from fastapi import Depends, FastAPI               # app and DI
from fastapi.testclient import TestClient          # in-process test client
from pydantic import BaseModel, ConfigDict, ValidationError   # frozen pydantic model

app: FastAPI = FastAPI()                           # create app


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)         # attributes cannot be reassigned
    app_name: str = "shop"                         # config value
    max_items: int = 50                            # config value


SETTINGS = Settings()                              # created once


def get_settings() -> Settings:
    return SETTINGS                                # same immutable object always


@app.get("/limits")                                # GET /limits
def limits(s: Settings = Depends(get_settings)) -> dict[str, int]:
    return {"max_items": s.max_items}              # safe to read from any thread


try:                                               # tampering attempt
    SETTINGS.max_items = 1                         # pydantic v2 raises ValidationError
except ValidationError as e:
    print("blocked:", e.errors()[0]["type"])       # frozen_instance

print(TestClient(app).get("/limits").json())       # {'max_items': 50}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default argument
✅ Correct: use `None` and create inside

```python
# Wrong
def add(x, bag=[]):
    bag.append(x); return bag
print(add(1), add(2))      # [1, 2] [1, 2]  <- shared list!
# Right
def add2(x, bag=None):
    bag = [] if bag is None else bag
    bag.append(x); return bag
print(add2(1), add2(2))    # [1] [2]
```

❌ Mistake 2: Thinking a tuple is deeply immutable
✅ Correct: only use immutable items inside if you need real safety

```python
t = (1, [2])
# Wrong assumption
t[1].append(3)             # works!
print(t)                   # (1, [2, 3])
# Right: use nested tuples / frozenset, or deep copy before mutating
```

❌ Mistake 3: Expecting `+=` to behave the same for lists and tuples
✅ Correct: know that `+=` mutates lists in place but rebinds immutables

```python
a = [1]; b = a; a += [2]
print(b)                   # [1, 2]  <- same object changed
x = (1,); y = x; x += (2,)
print(y, x)                # (1,) (1, 2)  <- new object
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
t = (1, [2, 3])
try:
    t[1] += [4]
except TypeError as e:
    print("error")
print(t)
a = "abc"
b = "abc"
print(a is b, id(a) == id(b))
```
Answer: It prints `error` AND `(1, [2, 3, 4])`. `t[1] += [4]` first runs `list.__iadd__`, which extends the list in place (this succeeds), and then tries to assign the result back to `t[1]`, which fails because tuples don't support item assignment. So the exception is raised but the change already happened. The last line is usually `True True` because CPython interns identical short string literals, but that is an implementation detail: never rely on `is` for strings.

---

## ⚫ Interview Questions + Answers

Q1: Which built-in types are immutable?
A1: `int`, `float`, `complex`, `bool`, `str`, `bytes`, `tuple`, `frozenset`, `range`, `NoneType`. Mutable: `list`, `dict`, `set`, `bytearray`, and most user-defined objects.

Q2: Why must dict keys be hashable and how does it relate to immutability?
A2: A key's hash must stay the same for its lifetime, or lookups would break. Immutable objects (with immutable contents) have stable hashes. Tuples containing lists are not hashable.

Q3: What is the difference between `is` and `==` for immutables?
A3: `==` compares values; `is` compares identity. Small ints (-5..256) and some strings are cached/interned by CPython, so `is` may give True, but it is an implementation detail. Use `==` for values and `is` only for `None`.

Q4: How do you make a custom class immutable?
A4: `@dataclass(frozen=True)`, `typing.NamedTuple`, or override `__setattr__`/use properties without setters and `__slots__`. Frozen is shallow: mutable fields inside can still change.

Q5: What are the benefits and the cost?
A5: Benefits: thread safety, hashability, easy caching, fewer bugs, simple undo/history. Cost: each change creates a new object (extra memory/time). Use immutable by default and mutable where performance needs it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Representing values (money, coordinates, config, IDs)
- Dict keys, set members, cache keys
- Data shared across threads/requests

❌ Avoid when:
- Building big collections incrementally (use a list, then convert)
- Heavy in-place algorithms (sorting big arrays, buffers)
- Copying cost dominates performance

---

## 📊 Visual Diagram
```
Mutable:    a ──► [1, 2]        b = a
            append(3)  →  a, b both see [1, 2, 3]   (same object)

Immutable:  x ──► (1, 2)        y = x
            x += (3,)  →  x ──► (1, 2, 3)  (NEW object)
                          y ──► (1, 2)     (unchanged)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot change after creation | बनने के बाद नहीं बदलता |
| Mutable | Can change in place | उसी जगह बदल सकता है |
| Hashable | Has a stable hash | स्थिर hash वाला |
| Frozen | Blocks attribute changes | Attribute बदलाव रोकता है |
| Shallow | Only the top level is protected | सिर्फ ऊपरी स्तर सुरक्षित |
| Interning | Reusing identical objects | समान objects दोबारा use करना |

---

## ⚡ 3-Line Summary
English: Immutable objects never change after creation; "changing" them builds a new object. They are hashable, thread-safe and easy to cache, but immutability is shallow: a tuple can hold a list. Use frozen dataclasses, NamedTuple, tuples and frozensets for values.
Hindi: Immutable objects बनने के बाद कभी नहीं बदलते; "बदलना" नया object बनाता है। ये hashable, thread-safe और cache करने में आसान हैं, पर immutability shallow है: tuple में list रह सकती है। Values के लिए frozen dataclass, NamedTuple, tuple और frozenset use करें।

---

## ➡️ Next Topic
**133. Pure Functions** — no side effects, same input gives same output.
