---

# Q148. Complete Dataclass
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete the dataclass so instances are comparable by `price`, have a safe default list for `tags`, and validate `price >= 0`.

```python
from dataclasses import ____, field                # BLANK 1: the decorator


@____(order=True)                                  # BLANK 2: decorator generating __init__/__repr__/__eq__/<
class Product:
    price: float                                   # first field -> used for ordering
    name: str = field(compare=False)               # excluded from comparisons
    tags: list[str] = field(____=list)             # BLANK 3: safe mutable default

    def ____(self) -> None:                        # BLANK 4: hook that runs after __init__
        if self.price < 0:
            raise ValueError("price must be >= 0")
```

---

## 💡 Quick Concept (2 lines only)
`@dataclass` generates `__init__`, `__repr__`, `__eq__` (and ordering/hash on request) from annotated fields; mutable defaults need `default_factory`.
हिंदी: `@dataclass` annotations से `__init__`, `__repr__`, `__eq__` खुद बना देता है; mutable default के लिए `default_factory`।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from dataclasses import dataclass, field           # BLANK 1: tools we need


@dataclass(order=True)                             # BLANK 2: also generates <, <=, >, >=
class Product:
    price: float                                   # compared first (field order matters)
    name: str = field(compare=False)               # ignored by ==, <, ...
    tags: list[str] = field(default_factory=list)  # BLANK 3: new list per instance

    def __post_init__(self) -> None:               # BLANK 4: runs right after generated __init__
        if self.price < 0:                         # Step 1: validate
            raise ValueError("price must be >= 0") # reject bad data


# ============================================
# TEST CASES
# ============================================
a = Product(5.0, "pen")                            # tags defaults to []
b = Product(9.5, "book", ["paper"])                # explicit tags
print(a)                                           # Expected: Product(price=5.0, name='pen', tags=[])
print(a < b)                                       # Expected: True
print(Product(5.0, "pen") == Product(5.0, "ink"))  # Expected: True  (name excluded from compare)
print(sorted([b, a])[0].name)                      # Expected: pen

a.tags.append("x")                                 # mutate only a's list
print(Product(1.0, "z").tags)                      # Expected: []  (not shared)

try:
    Product(-1, "bad")                             # triggers __post_init__
except ValueError as e:
    print(e)                                       # Expected: price must be >= 0
```

---

## 🔍 Why This Works (3 lines max)
The decorator writes the boilerplate; `order=True` compares fields as tuples in declaration order, skipping `compare=False`. `default_factory=list` builds a fresh list per instance; `__post_init__` validates.
हिंदी: Decorator boilerplate लिखता है, `default_factory` हर object को नई list देता है, `__post_init__` में validation होती है।

---

## ⚡ Alternative Solution
```python
# Immutable + memory-light: frozen + slots (3.10+)
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)                # immutable, hashable, no __dict__
class Point:
    x: int
    y: int = 0                                     # default value

p = Point(1)                                       # y defaults to 0
print(p)                                           # Expected: Point(x=1, y=0)
print(replace(p, y=5))                             # Expected: Point(x=1, y=5)
print({p: "ok"}[Point(1, 0)])                      # Expected: ok  (hashable)
try:
    p.x = 9                                        # frozen -> not allowed
except Exception as e:
    print(type(e).__name__)                        # Expected: FrozenInstanceError
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: tags: list[str] = []   -> ValueError: mutable default <class 'list'> for field tags
#    is not allowed: use default_factory   (dataclass protects you from the classic bug)
# ❌ Wrong: non-default field after a default field -> TypeError
# ✅ Correct: field(default_factory=list), and put fields without defaults first
```

---

## 🎯 Interview Tip (1 line)
Say: "Dataclasses remove boilerplate; know `default_factory`, `frozen`, `order`, `slots` and `__post_init__` — and when to prefer Pydantic for validation."

---

## 🔗 Related Questions
→ Q001 (mutable default) | Q134 (__eq__ without __hash__) | Q169 (__slots__) | Q246 (dataclasses)
