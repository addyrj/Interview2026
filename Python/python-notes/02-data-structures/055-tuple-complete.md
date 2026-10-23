---

# 055. Tuple — Complete Guide
# हिंदी में: Tuple — पूरी Guide

---

## 🔵 Simple Definition (English)
A tuple is an **immutable**, ordered sequence. Like a list but cannot be changed after creation. Tuples are hashable when all elements are hashable — meaning they can be used as **dict keys** and **set elements**. Faster than lists for iteration. Used for: multi-value returns, function arguments, data records, namedtuples. `(1, 2, 3)` not `[1, 2, 3]`.

## 🔵 सरल परिभाषा (Hindi)
Tuple **immutable**, ordered sequence है। List की तरह लेकिन create होने के बाद बदल नहीं सकता। Hashable होने पर dict key और set element बन सकता है। Iteration में list से fast। Multi-value returns, function args, data records के लिए।

---

## 💻 Code Example — Basic
```python
# ─── Creating tuples ──────────────────────────────────────────────
empty    = ()
single   = (42,)          # trailing comma REQUIRED for single element!
single2  = 42,            # parentheses optional for packing
coords   = (10, 20)
rgb      = (255, 128, 0)
mixed    = (1, "hello", True, None)
nested   = ((1, 2), (3, 4))

# From iterable:
from_list = tuple([1, 2, 3])
from_str  = tuple("abc")     # ('a', 'b', 'c')
from_range = tuple(range(5)) # (0, 1, 2, 3, 4)

# ─── Immutability ─────────────────────────────────────────────────
t = (1, 2, 3)
# t[0] = 99    # TypeError: 'tuple' object does not support item assignment
# t.append(4)  # AttributeError: tuple has no 'append'

# But mutable elements inside CAN be modified:
t = ([1, 2], [3, 4])
t[0].append(99)         # OK — modifying the list, not the tuple
print(t)   # ([1, 2, 99], [3, 4])
# This makes t unhashable! (contains mutable element)

# ─── Accessing elements ───────────────────────────────────────────
coords = (10, 20, 30)
print(coords[0])    # 10
print(coords[-1])   # 30
print(coords[1:])   # (20, 30)

# ─── Tuple methods (only 2!) ─────────────────────────────────────
t = (1, 2, 3, 2, 4, 2)
print(t.count(2))    # 3 — count occurrences
print(t.index(3))    # 2 — first index of value

# ─── Tuple unpacking ─────────────────────────────────────────────
# Basic:
x, y = (10, 20)
print(x, y)   # 10 20

# With *:
first, *rest = (1, 2, 3, 4, 5)
print(first, rest)   # 1 [2, 3, 4, 5]

*start, last = (1, 2, 3, 4, 5)
print(start, last)   # [1, 2, 3, 4] 5

a, *middle, z = (1, 2, 3, 4, 5)
print(a, middle, z)   # 1 [2, 3, 4] 5

# Swap variables (tuple packing/unpacking):
a, b = 10, 20
a, b = b, a   # swap — no temp variable needed!
print(a, b)   # 20 10

# ─── Tuple as dict key (hashable!) ───────────────────────────────
locations = {}
locations[(40.7128, -74.0060)] = "New York"
locations[(51.5074, -0.1278)] = "London"

print(locations[(40.7128, -74.0060)])   # "New York"

# Grid coordinates cache:
cache: dict[tuple[int, int], str] = {}
cache[(0, 0)] = "origin"
cache[(1, 2)] = "point A"

# Set of tuples:
visited: set[tuple[int, int]] = {(0, 0), (1, 1), (2, 2)}
print((0, 0) in visited)   # True — O(1) lookup!
```

## 💻 Code Example — Advanced
```python
from collections import namedtuple
from typing import NamedTuple

# ─── Named tuple — tuple with field names ─────────────────────────
# Old style (collections.namedtuple):
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)       # 3 4 — access by name
print(p[0], p[1])     # 3 4 — still works as tuple
print(p._asdict())    # {'x': 3, 'y': 4}

# Modern style (typing.NamedTuple) — with type hints:
class Coordinate(NamedTuple):
    latitude: float
    longitude: float
    altitude: float = 0.0   # default value

c = Coordinate(40.7128, -74.0060)
print(c.latitude)   # 40.7128
print(c)            # Coordinate(latitude=40.7128, longitude=-74.006, altitude=0.0)

# Hashable — usable as dict key:
cache: dict[Coordinate, str] = {}
cache[Coordinate(40.7128, -74.0060)] = "New York"

# ─── Multiple return values ───────────────────────────────────────
def get_min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)   # tuple packing

low, high = get_min_max([3, 1, 4, 1, 5, 9])   # tuple unpacking
print(f"Min: {low}, Max: {high}")   # Min: 1, Max: 9

# ─── zip() returns tuples ─────────────────────────────────────────
names = ["Priya", "Raj", "Anita"]
scores = [90, 85, 92]

for name, score in zip(names, scores):   # (Priya, 90), (Raj, 85), ...
    print(f"{name}: {score}")

# Unzip (reverse of zip):
pairs = [("Priya", 90), ("Raj", 85), ("Anita", 92)]
names, scores = zip(*pairs)   # unzip!
print(list(names))   # ['Priya', 'Raj', 'Anita']

# ─── enumerate() returns (index, value) tuples ────────────────────
for i, item in enumerate(["a", "b", "c"], start=1):
    print(f"{i}. {item}")   # 1. a, 2. b, 3. c

# ─── Sorting tuples ───────────────────────────────────────────────
data = [(3, "banana"), (1, "apple"), (2, "cherry")]
sorted_data = sorted(data)   # sorts by first element, then second
print(sorted_data)   # [(1, 'apple'), (2, 'cherry'), (3, 'banana')]

# Sort by second element:
sorted_by_name = sorted(data, key=lambda t: t[1])
print(sorted_by_name)   # [(1, 'apple'), (3, 'banana'), (2, 'cherry')]

# Sort list of dicts by multiple keys:
people = [("Bob", 25), ("Alice", 30), ("Bob", 20)]
# Sort by name, then by age:
people.sort(key=lambda p: (p[0], p[1]))
print(people)   # [('Alice', 30), ('Bob', 20), ('Bob', 25)]

# ─── Performance: tuple vs list ───────────────────────────────────
import timeit, sys

# Tuple is faster to create and uses less memory:
t = (1, 2, 3, 4, 5)
l = [1, 2, 3, 4, 5]

print(sys.getsizeof(t))   # 80 bytes
print(sys.getsizeof(l))   # 120 bytes — list uses more memory

# Creation time:
tuple_time = timeit.timeit("(1, 2, 3)", number=10_000_000)
list_time  = timeit.timeit("[1, 2, 3]", number=10_000_000)
print(f"tuple: {tuple_time:.2f}s, list: {list_time:.2f}s")
# tuple ~3x faster to create (Python can cache tuples)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python tuple (immutable):
t = (1, 2, 3)
x, y, z = t      # destructuring
x, *rest = t     # rest captures remaining

# Multi-return:
def stats(data): return min(data), max(data)
low, high = stats([1,2,3])

# Tuple as dict key:
cache = {(1, 2): "point"}
```

```javascript
// JavaScript — no native tuple (arrays are mutable):
// Use array for similar behavior:
const t = Object.freeze([1, 2, 3]);  // immutable array
const [x, y, z] = t;   // destructuring
const [first, ...rest] = t;  // rest

// Multi-return (array or object):
function stats(data) { return [Math.min(...data), Math.max(...data)]; }
const [low, high] = stats([1,2,3]);

// Arrays can't be object keys:
const cache = new Map();
cache.set(JSON.stringify([1,2]), "point");  // workaround
```

Key difference: Python tuples are truly immutable AND hashable (can be dict keys). JS arrays are mutable — no native immutable sequence with hash capability. TypeScript has `readonly` arrays but they're still not hashable.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting trailing comma for single-element tuple
```python
# Wrong — just parentheses around a value, NOT a tuple:
not_a_tuple = (42)
print(type(not_a_tuple))   # <class 'int'>

# Correct — trailing comma creates tuple:
is_a_tuple = (42,)
print(type(is_a_tuple))    # <class 'tuple'>

# Also works without parentheses:
also_tuple = 42,
print(type(also_tuple))    # <class 'tuple'>
```

❌ Mistake 2: Assuming tuple with mutable elements is hashable
```python
# Wrong — list inside tuple makes it unhashable:
t = ([1, 2], 3)
hash(t)   # TypeError: unhashable type: 'list'
{t: "value"}   # TypeError!

# Correct — all elements must be hashable:
t = ((1, 2), 3)   # tuple of tuple — all hashable
{t: "value"}   # OK
```

---

## 🧠 Tricky Interview Question

**Q**: `t = (1, 2, 3)` and `l = [1, 2, 3]`. Both have same data — what's the actual difference?

**Answer**: (1) **Mutability**: `t[0] = 99` raises TypeError; `l[0] = 99` works. (2) **Hash**: `hash(t)` works; `hash(l)` raises TypeError — tuples can be dict keys. (3) **Memory**: tuple ~33% less memory than equivalent list. (4) **Speed**: tuple creation ~3x faster (Python can intern tuples). (5) **Methods**: list has `append`, `insert`, `remove`, `sort` — tuple only has `count` and `index`. (6) **Semantics**: use list for homogeneous mutable sequences; use tuple for heterogeneous records (like a DB row: `(id, name, age)`).

---

## ⚫ Interview Questions + Answers

Q1: When should you use a tuple vs a list?
A1: **Tuple**: data that shouldn't change (coordinates, RGB color, database row, function return values), dict keys or set elements, named tuples for records. Signals to reader: "this data is fixed." **List**: mutable sequences, homogeneous items, order matters and changes (shopping cart, log entries, results). Rule: tuples are "records" (different fields), lists are "sequences" (same type). Example: `(name, age, email)` = tuple (a person record). `[name1, name2, name3]` = list (many names).

Q2: Is a tuple with a list inside it hashable?
A2: No. `hash((1, [2, 3]))` raises `TypeError: unhashable type: 'list'`. For a tuple to be hashable, ALL elements must be hashable. Since `list` is mutable (and thus unhashable), any tuple containing a list is unhashable. Fix: use nested tuples instead: `hash((1, (2, 3)))` works. `frozenset` is also hashable — can be inside a tuple as dict key.

Q3: What is tuple unpacking and how does `*` work in it?
A3: Tuple unpacking assigns tuple elements to variables: `x, y = (1, 2)`. `*var` captures multiple elements as a list: `first, *rest = (1,2,3,4)` → `rest=[2,3,4]`. Can be in middle: `a, *mid, z = (1,2,3,4,5)` → `mid=[2,3,4]`. Works with any iterable, not just tuples. Use `_` for values you don't need: `x, _ = (10, 20)`. Nested unpacking: `(a, b), c = (1,2), 3`.

Q4: What are the advantages of `typing.NamedTuple` over `collections.namedtuple`?
A4: `NamedTuple` class syntax supports: (1) Type annotations: `latitude: float`. (2) Default values: `altitude: float = 0.0`. (3) Methods and docstrings (add like regular class). (4) Better IDE support (autocomplete, type checking). (5) `__init_subclass__`. Both are still immutable tuples under the hood. For simple read-only data: use `NamedTuple`. For full-featured objects: use `dataclass`. `NamedTuple` is also indexable (backward compat with tuple APIs).

Q5: How does Python implement tuple optimization for small literal tuples?
A5: Python constant-folds literal tuples of constants at compile time — `(1, 2, 3)` is compiled to a single LOAD_CONST bytecode that loads the pre-built tuple. Lists `[1, 2, 3]` require BUILD_LIST bytecode at runtime. Python also interns ("caches") small tuples — accessing `(1, 2)` twice may return the same object. This is why tuple creation is ~3x faster than list creation. `timeit.timeit("(1,2,3)")` vs `timeit.timeit("[1,2,3]")` shows the difference clearly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable | Cannot change after creation | Create के बाद नहीं बदल सकते |
| Hashable | Can be used as dict key | Dict key बन सकता है |
| Packing | Multiple values → tuple | Multiple values → tuple |
| Unpacking | Tuple → multiple variables | Tuple → multiple variables |
| NamedTuple | Typed tuple with field names | Typed tuple with field names |
| Trailing comma | `(x,)` for single-element | Single element के लिए `,` |

---

## ⚡ 3-Line Summary
English: Tuples are immutable ordered sequences — use them for multi-value returns, dict keys, and data records that shouldn't change. The `(42,)` trailing comma is required for single-element tuples. `typing.NamedTuple` gives tuples field names + type hints — great for lightweight data objects.
Hindi: Tuples immutable ordered sequences हैं। Multi-value returns, dict keys, fixed data records के लिए। Single element: `(42,)` — trailing comma जरूरी। `NamedTuple` से field names + type hints मिलते हैं।

---

## ➡️ Next Topic
**058. Dictionary Complete** — O(1) key-value store. **065. Set Complete** — unique elements with O(1) lookup. **079. collections Module** — Counter, defaultdict, deque.
