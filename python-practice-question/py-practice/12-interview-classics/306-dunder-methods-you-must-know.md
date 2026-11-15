---

# Q306. Dunder Methods You Must Know
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a small `Vector` class that works with `print`, `==`, `+`, `*`, `len`, indexing, iteration, `in`, `bool`, `hash` and calling like a function. Which dunder (magic) method powers each of these?

```python
# NOT RUN (question stub)
v = Vector(1, 2)
w = Vector(3, 4)
print(v + w)        # want: <4, 6>
print(2 * v)        # want: Vector(2, 4)
print(len(v), v[0], list(v), 2 in v)
print(bool(Vector(0, 0)), {v: "a"}[Vector(1, 2)])
```

---

## 💡 Quick Concept (2 lines only)
Python syntax is just sugar for special methods: `a + b` -> `type(a).__add__(a, b)`, `len(x)` -> `__len__`, `x[i]` -> `__getitem__`, `print(x)` -> `__str__` (falls back to `__repr__`). Dunders are looked up on the TYPE, not the instance.
हिंदी: हर operator/built-in के पीछे एक dunder method होता है; Python उसे class पर ढूँढता है, instance पर नहीं।

---

## ✅ Answer / Solution

```python
from __future__ import annotations                       # allow "Vector" type hints inside the class
from collections.abc import Iterator                     # type for __iter__


class Vector:
    def __init__(self, *items: float) -> None:           # constructor (after __new__)
        self.items = tuple(items)                        # store immutably

    def __repr__(self) -> str:                           # for developers / REPL / debugging
        return f"Vector{self.items}"                     # unambiguous text

    def __str__(self) -> str:                            # for print() / str()
        return "<" + ", ".join(map(str, self.items)) + ">"  # friendly text

    def __eq__(self, other: object) -> bool:             # powers ==
        if not isinstance(other, Vector):                # different type?
            return NotImplemented                        # let Python try the other side
        return self.items == other.items                 # compare contents

    def __hash__(self) -> int:                           # needed because we defined __eq__
        return hash(self.items)                          # equal objects -> equal hash

    def __add__(self, other: Vector) -> Vector:          # powers v + w
        return Vector(*(a + b for a, b in zip(self.items, other.items)))  # element-wise add

    def __mul__(self, k: float) -> Vector:               # powers v * 2
        return Vector(*(a * k for a in self.items))      # scale every item

    __rmul__ = __mul__                                   # powers 2 * v (reflected operand)

    def __len__(self) -> int:                            # powers len(v)
        return len(self.items)                           # number of items

    def __getitem__(self, i: int) -> float:              # powers v[i] (and old-style iteration)
        return self.items[i]                             # delegate to the tuple

    def __iter__(self) -> Iterator[float]:               # powers for-loops / list(v)
        return iter(self.items)                          # tuple iterator

    def __contains__(self, x: float) -> bool:            # powers `x in v`
        return x in self.items                           # membership test

    def __bool__(self) -> bool:                          # powers bool(v) / if v:
        return any(self.items)                           # False if all zeros

    def __call__(self, scale: float) -> Vector:          # powers v(3): instance acts like a function
        return self * scale                              # reuse __mul__


# ============================================
# TEST CASES
# ============================================
v, w = Vector(1, 2), Vector(3, 4)                        # two sample vectors
print(v + w)                                             # __add__ then __str__
print(repr(2 * v))                                       # __rmul__ then __repr__
print(len(v), v[0], list(v), 2 in v)                     # __len__, __getitem__, __iter__, __contains__
print(bool(Vector(0, 0)), bool(v))                       # __bool__
print({v: "a"}[Vector(1, 2)])                            # __eq__ + __hash__ make it a dict key
print(v == Vector(1, 2), v == (1, 2))                    # NotImplemented -> falls back to False
print(v(10))                                             # __call__

# Expected output:
# <4, 6>
# Vector(2, 4)
# 2 1 [1, 2] True
# False True
# a
# True False
# <10, 20>
```

---

## 🔍 Why This Works (3 lines max)
The interpreter translates syntax into calls on `type(obj)`: `+` -> `__add__`, and `2 * v` -> `int.__mul__` returns `NotImplemented`, so Python tries `Vector.__rmul__`. Defining `__eq__` sets `__hash__` to `None` unless you also define it, so both go together.
हिंदी: `__eq__` लिखो तो `__hash__` भी लिखो, वरना object unhashable हो जाता है; `NotImplemented` return करने से Python दूसरी तरफ try करता है।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass                        # generates __init__/__repr__/__eq__/__hash__
from functools import total_ordering                     # derive <,>,<=,>= from __eq__ + one of them


@total_ordering                                          # only __lt__ needed below
@dataclass(frozen=True)                                  # frozen -> __hash__ is generated too
class Version:
    major: int                                           # first field
    minor: int                                           # second field

    def __lt__(self, other: "Version") -> bool:          # the one comparison we write by hand
        return (self.major, self.minor) < (other.major, other.minor)  # tuple comparison


print(Version(1, 2) < Version(1, 10))                    # __lt__
print(Version(2, 0) >= Version(1, 99))                   # derived by total_ordering
print(Version(1, 2))                                     # dataclass __repr__
print(max(Version(1, 2), Version(1, 10)))                # works because ordering exists

# Context manager dunders: __enter__ / __exit__ (see Q305)
class Tag:
    def __enter__(self) -> "Tag":                        # runs at `with` start
        print("<b>")                                     # open
        return self                                      # bound to `as`
    def __exit__(self, *exc) -> bool:                    # runs at `with` end
        print("</b>")                                    # close
        return False                                     # do not swallow exceptions

with Tag():                                              # triggers both dunders
    print("hi")                                          # body

# Expected output:
# True
# True
# Version(major=1, minor=2)
# Version(major=1, minor=10)
# <b>
# hi
# </b>
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: __eq__ without __hash__ -> instances become unhashable
class P:
    def __init__(self, x): self.x = x
    def __eq__(self, o): return self.x == o.x

try:
    {P(1): "a"}                                          # TypeError
except TypeError as e:
    print(e)

# ❌ Wrong: putting dunders on the instance
class Q: pass
q = Q()
q.__len__ = lambda: 5                                    # instance attribute is IGNORED by len()
try:
    len(q)
except TypeError as e:
    print(e)

# ✅ Correct: define dunders on the class, and use len(x), not x.__len__()

# Expected output:
# unhashable type: 'P'
# object of type 'Q' has no len()
```

---

## 🎯 Interview Tip (1 line)
Say: "Dunders are the protocol hooks of the data model: `__repr__`/`__str__`, `__eq__`+`__hash__`, `__len__`/`__getitem__`/`__iter__`, arithmetic with reflected `__r*__` variants, `__enter__`/`__exit__`, `__call__`."

---

## 🔗 Related Questions
→ Q034 (__eq__ without __hash__) | Q035 (__repr__ vs __str__) | Q300 (__init__ vs __new__) | Q305 (the with statement)
