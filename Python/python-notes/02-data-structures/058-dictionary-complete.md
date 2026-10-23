---

# 058. Dictionary — Complete Guide
# हिंदी में: Dictionary — पूरी Guide

---

## 🔵 Simple Definition (English)
A Python dictionary is an ordered (Python 3.7+), mutable collection of key-value pairs. Keys must be hashable (immutable: str, int, tuple) — values can be anything. O(1) average lookup, insert, and delete. Equivalent to JavaScript objects / Maps. The most important data structure after lists — used everywhere in Python (function kwargs, JSON, configs, caches).

## 🔵 सरल परिभाषा (Hindi)
Python dictionary ordered (3.7+), mutable key-value pairs का collection है। Keys hashable होनी चाहिए (str, int, tuple)। O(1) lookup, insert, delete। JavaScript object/Map का equivalent। Python में सबसे important data structure।

---

## 💻 Code Example — Basic
```python
# ─── Creating dicts ──────────────────────────────────────────────
empty = {}
person = {"name": "Priya", "age": 25, "city": "Mumbai"}
mixed  = {"count": 10, "active": True, "data": [1, 2, 3]}

# From sequences:
keys   = ["a", "b", "c"]
values = [1, 2, 3]
d = dict(zip(keys, values))    # {'a': 1, 'b': 2, 'c': 3}

# fromkeys — same value for all keys:
d = dict.fromkeys(["host", "port", "db"], None)   # {'host': None, 'port': None, 'db': None}

# ─── Access ──────────────────────────────────────────────────────
person = {"name": "Priya", "age": 25}

print(person["name"])              # "Priya" — KeyError if missing!
print(person.get("name"))          # "Priya"
print(person.get("email"))         # None (no KeyError)
print(person.get("email", "N/A"))  # "N/A" (custom default)

# ─── Modifying ───────────────────────────────────────────────────
person["email"] = "priya@example.com"   # add new key
person["age"] = 26                       # update existing key

person.update({"city": "Bangalore", "age": 27})   # update multiple
person.update(role="admin", level=3)              # keyword style

# ─── Removing ────────────────────────────────────────────────────
removed = person.pop("email")            # removes + returns value (KeyError if missing)
removed = person.pop("phone", None)      # returns None if missing (safe)
del person["city"]                       # removes key (KeyError if missing)
last_item = person.popitem()             # removes + returns LAST inserted (key, value) pair
person.clear()                           # removes all items

# ─── Iteration ───────────────────────────────────────────────────
config = {"host": "localhost", "port": 5432, "db": "mydb"}

for key in config:                   # iterates keys
    print(key)

for key in config.keys():            # explicit keys iterator
    print(key)

for value in config.values():        # values iterator
    print(value)

for key, value in config.items():    # key-value pairs (most common)
    print(f"{key}: {value}")

# ─── Useful methods ──────────────────────────────────────────────
print("host" in config)              # True — key membership (O(1))
print("localhost" in config.values()) # True — value membership (O(n)!)
print(len(config))                    # 3

# setdefault — get or create:
config.setdefault("timeout", 30)     # adds "timeout": 30 if not present
config.setdefault("host", "remote")  # does NOTHING — "host" already exists
print(config["host"])                # "localhost" (unchanged)
```

## 💻 Code Example — Advanced
```python
from collections import defaultdict, Counter, OrderedDict
from typing import Any

# ─── Dict comprehension ───────────────────────────────────────────
# {key_expr: value_expr for item in iterable if condition}

squares = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Invert a dict:
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}

# Filter dict:
scores = {"Alice": 90, "Bob": 55, "Charlie": 78, "Dave": 45}
passing = {name: score for name, score in scores.items() if score >= 60}
# {'Alice': 90, 'Charlie': 78}

# ─── Merging dicts ────────────────────────────────────────────────
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}

# Python 3.9+ — merge operator:
merged = d1 | d2        # {'a':1, 'b':3, 'c':4}  ← d2 wins on conflict
d1 |= d2                # update d1 in-place

# Python 3.5+ — unpack:
merged = {**d1, **d2}   # same result as |

# ─── defaultdict — automatic default for missing keys ─────────────
from collections import defaultdict

# Group by category:
products = [("phone","iPhone"),("phone","Samsung"),("laptop","Dell"),("phone","Pixel")]

by_category: dict[str, list] = defaultdict(list)
for category, product in products:
    by_category[category].append(product)   # no KeyError, auto-creates []

print(dict(by_category))
# {'phone': ['iPhone', 'Samsung', 'Pixel'], 'laptop': ['Dell']}

# Word frequency count:
text = "apple banana apple cherry banana apple"
freq: dict[str, int] = defaultdict(int)
for word in text.split():
    freq[word] += 1   # no KeyError, auto-creates 0
print(dict(freq))   # {'apple': 3, 'banana': 2, 'cherry': 1}

# ─── Counter — specialized dict for counting ──────────────────────
from collections import Counter

c = Counter(["a","b","a","c","b","a"])
print(c)                    # Counter({'a': 3, 'b': 2, 'c': 1})
print(c.most_common(2))     # [('a', 3), ('b', 2)]

c2 = Counter(["a","a","d"])
print(c + c2)               # Counter({'a': 5, 'b': 2, 'c': 1, 'd': 1})
print(c - c2)               # Counter({'b': 2, 'c': 1, 'a': 1})

# ─── Nested dict operations ───────────────────────────────────────
config = {
    "database": {"host": "localhost", "port": 5432},
    "redis":    {"host": "localhost", "port": 6379},
}

# Safe nested access:
db_host = config.get("database", {}).get("host", "unknown")
# or use a helper:
def deep_get(d: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d

print(deep_get(config, "database", "host"))    # "localhost"
print(deep_get(config, "cache", "host"))       # None (no KeyError)

# ─── dict as cache (memoization pattern) ─────────────────────────
_cache: dict[int, int] = {}

def fib(n: int) -> int:
    if n <= 1:
        return n
    if n in _cache:
        return _cache[n]    # O(1) lookup
    result = fib(n-1) + fib(n-2)
    _cache[n] = result
    return result
# Or just use @functools.lru_cache(maxsize=None)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python dict:
d = {"name": "Priya", "age": 25}

# Access with default:
val = d.get("phone", "N/A")   # "N/A"

# Iteration:
for key, val in d.items():    # clean key-value iteration
    print(f"{key}: {val}")

# Merge (3.9+):
merged = {**d1, **d2}
merged = d1 | d2
```

```javascript
// JavaScript object:
const d = { name: "Priya", age: 25 };

// Access with default:
const val = d.phone ?? "N/A";    // nullish coalescing

// Iteration:
for (const [key, val] of Object.entries(d)) {
    console.log(`${key}: ${val}`);
}

// Merge:
const merged = { ...d1, ...d2 };  // same as Python {**d1, **d2}
// JS also has Map for non-string keys + guaranteed insertion order
```

Key differences:
- Python dict: string AND non-string keys (any hashable type). JS object: only string/Symbol keys.
- Python dict: ordered by insertion (3.7+). JS object: also ordered (modern engines).
- Python has `get(key, default)`, `setdefault()`. JS uses `??` operator.
- Python `defaultdict` = JS pattern `map[key] = map[key] || []`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `dict["key"]` when key might not exist
```python
# Wrong — KeyError if "email" not in dict:
email = user["email"]

# Correct options:
email = user.get("email")           # None if missing
email = user.get("email", "N/A")    # custom default
if "email" in user:                 # explicit check
    email = user["email"]
```

❌ Mistake 2: Mutating dict while iterating
```python
# Wrong — RuntimeError: dictionary changed size during iteration:
for key in my_dict:
    if condition(key):
        del my_dict[key]

# Correct — iterate over a copy of keys:
for key in list(my_dict.keys()):
    if condition(key):
        del my_dict[key]
```

---

## 🧠 Tricky Interview Question

```python
d = {}
d[1] = "one"
d[1.0] = "ONE"
d[True] = "TRUE"
print(len(d))
print(d)
```
Answer: `len(d) == 1`, `d == {1: "TRUE"}`. In Python: `1 == 1.0 == True` (all equal as numbers) and `hash(1) == hash(1.0) == hash(True)` — so they're the same key! Python dictionaries use hash + equality to identify keys. The last value `"TRUE"` overwrites all previous values for that key.

---

## ⚫ Interview Questions + Answers

Q1: What makes a valid dict key?
A1: Any hashable (immutable) object. Valid: `str`, `int`, `float`, `bool`, `tuple` (of hashable items), `frozenset`. Invalid: `list`, `dict`, `set` — they're mutable, so their hash could change. Rule: if `hash(obj)` doesn't raise `TypeError`, it can be a dict key. Custom objects are hashable by default (uses `id()`), unless you define `__eq__` without `__hash__`.

Q2: What is the time complexity of dict operations?
A2: Lookup `d[key]`: O(1) average, O(n) worst case (hash collision — very rare). Insert `d[key] = val`: O(1) average. Delete `del d[key]`: O(1) average. `key in d`: O(1). Iteration: O(n). Python dicts are implemented as open-addressing hash tables — memory overhead ~50% above actual data. For very large dicts, memory can be a concern.

Q3: What is `defaultdict` and when should you use it?
A3: `defaultdict(factory)` is a dict subclass that calls `factory()` to create a default value for missing keys instead of raising `KeyError`. `defaultdict(list)`: missing key → `[]`. `defaultdict(int)`: missing key → `0`. Use it for: grouping (accumulate items by category), counting (word frequency), building adjacency lists (graphs). Alternative: `d.setdefault(key, []).append(val)` works but is slightly less clean.

Q4: How do you sort a dictionary by value?
A4: `sorted(d.items(), key=lambda item: item[1])` returns a sorted list of `(key, value)` tuples. For descending: add `reverse=True`. To get a sorted dict: `dict(sorted(d.items(), key=lambda item: item[1]))`. Python 3.7+ dicts maintain insertion order, so the resulting dict is ordered by value. For most-common pattern: use `Counter.most_common(n)`.

Q5: What is the `|` dict merge operator (Python 3.9+)?
A5: `d1 | d2` creates a new dict merging d1 and d2 — d2 values win on key conflict. `d1 |= d2` updates d1 in-place. Pre-3.9: `{**d1, **d2}` (same semantics). The `|` operator works on any dict-like object, while `**` unpacking requires actual dicts. Use `|` for readability when merging configs, headers, defaults: `headers = default_headers | request_headers`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Key | Dict identifier (must be hashable) | Dict identifier (hashable होना चाहिए) |
| Value | Data stored for each key | Key के लिए stored data |
| Hashable | Can compute a hash (immutable) | Hash compute हो सकता है |
| defaultdict | Dict with auto-default for missing keys | Missing keys के लिए auto-default |
| Counter | Dict specialized for counting | Counting के लिए specialized dict |
| .get() | Safe access with optional default | KeyError-safe access |
| .items() | Iterator of (key, value) pairs | key-value pairs का iterator |

---

## ⚡ 3-Line Summary
English: Python dicts are O(1) hash tables — always use `.get(key, default)` instead of `dict[key]` when the key might not exist. Use `defaultdict(list)` for grouping and `Counter` for frequency counting. Dict comprehensions `{k: v for k, v in ...}` and the merge operator `d1 | d2` are the modern Python patterns.
Hindi: Python dicts O(1) hash tables हैं। Missing keys के लिए `.get(key, default)` use करो। Grouping के लिए `defaultdict(list)`, counting के लिए `Counter`। Comprehension और `|` merge operator modern pattern हैं।

---

## ➡️ Next Topic
**059. Dict Methods** — complete reference. **060. Dict Comprehension** — advanced patterns. **061. defaultdict** — deep dive with real use cases.
