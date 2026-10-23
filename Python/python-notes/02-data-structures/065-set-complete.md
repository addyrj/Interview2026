---

# 065. Set — Complete Guide
# हिंदी में: Set — पूरी Guide

---

## 🔵 Simple Definition (English)
A Python set is an unordered, mutable collection of unique, hashable elements. No duplicates allowed — adding an existing element is silently ignored. O(1) average for add, remove, and `in` checks (same as dict — uses hash tables). Use sets for: deduplication, membership testing, and set math (union, intersection, difference).

## 🔵 सरल परिभाषा (Hindi)
Python set unordered, mutable collection है unique hashable elements का। Duplicates नहीं — existing element add करो तो silently ignore। O(1) add, remove, `in` check। Deduplication, membership testing, set math के लिए use करो।

---

## 💻 Code Example — Basic
```python
# ─── Creating sets ────────────────────────────────────────────────
empty   = set()              # NOT {} — that creates empty dict!
numbers = {1, 2, 3, 4, 5}
mixed   = {1, "hello", (1,2)}   # tuple OK (hashable); list NOT OK

from_list  = set([1, 2, 2, 3, 3, 3])   # {1, 2, 3} — duplicates removed
from_str   = set("hello")               # {'h', 'e', 'l', 'o'} — unique chars

# ─── Core operations ─────────────────────────────────────────────
s = {1, 2, 3}

s.add(4)             # {1,2,3,4}
s.add(2)             # {1,2,3,4} — silently ignored (already exists)
s.remove(2)          # {1,3,4} — KeyError if not present!
s.discard(99)        # {1,3,4} — NO error if not present (safe)
popped = s.pop()     # removes and returns ARBITRARY element (order undefined)
s.clear()            # removes all elements

# ─── Membership testing — O(1) vs list O(n) ──────────────────────
valid_codes = {"8517.12.00", "8471.30.00", "6101.20.00"}

code = "8517.12.00"
print(code in valid_codes)     # True — O(1)! vs O(n) for list

# ─── Set math ────────────────────────────────────────────────────
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# Union — all elements from both:
print(a | b)           # {1,2,3,4,5,6,7,8}
print(a.union(b))      # same

# Intersection — only elements in BOTH:
print(a & b)           # {4, 5}
print(a.intersection(b))

# Difference — in a but NOT in b:
print(a - b)           # {1, 2, 3}
print(a.difference(b))

# Symmetric difference — in one but NOT both:
print(a ^ b)           # {1,2,3,6,7,8}
print(a.symmetric_difference(b))

# Subset / superset:
print({1,2} <= {1,2,3})      # True — {1,2} is subset of {1,2,3}
print({1,2,3} >= {1,2})      # True — {1,2,3} is superset of {1,2}
print({1,2}.isdisjoint({3})) # True — no common elements

# In-place operations (modify a):
a |= b    # a.update(b) — add all from b
a &= b    # a.intersection_update(b)
a -= b    # a.difference_update(b)
```

## 💻 Code Example — Advanced
```python
# Production use cases for sets

from typing import Any

# ─── Deduplication (preserving order — Python 3.7+) ───────────────
def deduplicate_ordered(lst: list) -> list:
    """Remove duplicates while preserving insertion order."""
    return list(dict.fromkeys(lst))       # dict.fromkeys preserves order

def deduplicate_set(lst: list) -> list:
    """Remove duplicates — order NOT preserved."""
    return list(set(lst))

data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(deduplicate_ordered(data))   # [3,1,4,5,9,2,6] — order preserved
print(deduplicate_set(data))       # [1,2,3,4,5,6,9] — sorted (hash order)

# ─── Fast membership check (10K-item lookup) ─────────────────────
import time

items = list(range(100_000))
lookup = 99_999

# List: O(n) scan:
as_list = items[:]
start = time.perf_counter()
for _ in range(10_000):
    _ = lookup in as_list
list_time = time.perf_counter() - start

# Set: O(1) lookup:
as_set = set(items)
start = time.perf_counter()
for _ in range(10_000):
    _ = lookup in as_set
set_time = time.perf_counter() - start

print(f"List: {list_time:.3f}s, Set: {set_time:.3f}s")
# List: ~0.5s, Set: ~0.001s — set is ~500x faster

# ─── Common interview patterns ────────────────────────────────────
# Find duplicates in a list:
def find_duplicates(lst: list) -> set:
    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return duplicates

print(find_duplicates([1,2,3,2,4,3,5]))   # {2, 3}

# Find common elements in two lists:
list1 = [1, 2, 3, 4, 5]
list2 = [3, 4, 5, 6, 7]
common = set(list1) & set(list2)     # {3, 4, 5}

# Check if all characters unique (isogram):
def is_isogram(word: str) -> bool:
    word = word.lower()
    return len(set(word)) == len(word)    # set removes duplicates

print(is_isogram("Python"))    # True
print(is_isogram("banana"))    # False

# ─── frozenset — immutable set (can be dict key or set element) ────
tags_a = frozenset(["python", "fastapi", "backend"])
tags_b = frozenset(["python", "react", "frontend"])

# frozenset can be a dict key:
tag_cache = {tags_a: "backend stack", tags_b: "frontend stack"}
print(tag_cache[frozenset(["python", "fastapi", "backend"])])  # "backend stack"

# set of frozensets:
all_combos = {frozenset([1,2]), frozenset([2,3]), frozenset([1,2])}
print(len(all_combos))   # 2 — duplicate frozenset removed

# ─── Set comprehension ───────────────────────────────────────────
squares = {x**2 for x in range(1, 6)}
print(squares)   # {1, 4, 9, 16, 25} — unordered, unique

# Extract unique domains from email list:
emails = ["a@gmail.com", "b@yahoo.com", "c@gmail.com"]
domains = {email.split("@")[1] for email in emails}
print(domains)   # {'gmail.com', 'yahoo.com'}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python set:
s = {1, 2, 3}
s.add(4)
2 in s        # True — O(1)

# Set operations:
{1,2,3} | {3,4,5}   # {1,2,3,4,5}  union
{1,2,3} & {3,4,5}   # {3}          intersection
{1,2,3} - {3,4,5}   # {1,2}        difference
```

```javascript
// JavaScript Set:
const s = new Set([1, 2, 3]);
s.add(4);
s.has(2);     // true — O(1)

// No built-in set operations! Must implement manually:
const union = new Set([...setA, ...setB]);
const inter = new Set([...setA].filter(x => setB.has(x)));
const diff  = new Set([...setA].filter(x => !setB.has(x)));
```

Key difference: Python has built-in `|`, `&`, `-`, `^` operators for sets. JavaScript requires manual implementation.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating empty set with `{}`
```python
empty_dict = {}       # creates dict, NOT set!
empty_set  = set()    # correct way to create empty set
```

❌ Mistake 2: Trying to put unhashable items in set
```python
# Wrong — list is unhashable:
s = {[1, 2], [3, 4]}   # TypeError: unhashable type: 'list'

# Correct — use tuples (immutable, hashable):
s = {(1, 2), (3, 4)}   # OK

# Or frozenset for nested sets:
s = {frozenset([1,2]), frozenset([3,4])}   # OK
```

---

## 🧠 Tricky Interview Question

```python
a = {1, 2, 3}
b = a
b.add(4)
print(a)
```
Answer: `{1, 2, 3, 4}` — same object reference as lists and dicts. `b = a` doesn't copy. Use `b = a.copy()` for independent copy.

Also: `a = {True, 1, 1.0}` → `{True}`. Why? `True == 1 == 1.0` and `hash(True) == hash(1) == hash(1.0)` — they're all the same key. First one in wins (True was first).

---

## ⚫ Interview Questions + Answers

Q1: What is the time complexity of set operations?
A1: Add, remove, `in`: O(1) average (hash table). Set union `|`: O(len(s1) + len(s2)). Intersection `&`: O(min(len(s1), len(s2))). Difference `-`: O(len(s1)). Iteration: O(n). Worst case for add/remove/in: O(n) (hash collisions — extremely rare in practice).

Q2: When should you use a set vs a list?
A2: Use a set when: (1) you need O(1) membership testing (`in` operator), (2) you need unique elements automatically, (3) you need set operations (union/intersection/difference). Use a list when: (1) order matters, (2) duplicates are valid, (3) you need index access, (4) elements must be unhashable (lists, dicts). Rule of thumb: "Do I need uniqueness or fast lookup?" → set. "Do I need sequence?" → list.

Q3: What is a frozenset and what are its use cases?
A3: `frozenset` is an immutable version of `set` — same operations (|, &, -, ^, `in`) but cannot add/remove elements. Use cases: (1) dict key (mutable set can't be a key), (2) element of another set, (3) when you want set operations on data that shouldn't change, (4) passing sets to functions that shouldn't modify them. `frozenset(["tag1", "tag2"])` is how you store "sets as data."

Q4: How do you find the intersection of multiple sets?
A4: `set.intersection(*others)` or `s1 & s2 & s3`. For a list of sets: `sets = [{1,2,3},{2,3,4},{3,4,5}]; result = sets[0].intersection(*sets[1:])` → `{3}`. Or: `from functools import reduce; import operator; reduce(operator.and_, sets)` → `{3}`.

Q5: What is the difference between `remove()` and `discard()` for sets?
A5: `remove(elem)`: removes the element, raises `KeyError` if not present. `discard(elem)`: removes the element, does NOTHING if not present (no error). Use `discard()` when unsure if element exists — avoids try/except. Use `remove()` when the element MUST be present (its absence is a bug you want to catch).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Set | Unique, unordered collection | Unique, unordered collection |
| frozenset | Immutable set | Immutable set |
| Union (|) | All elements from both | दोनों के सभी elements |
| Intersection (&) | Only common elements | सिर्फ common elements |
| Difference (-) | In A but not in B | A में है, B में नहीं |
| Symmetric difference (^) | In one but not both | एक में है, दोनों में नहीं |
| Hashable | Can be in a set (immutable) | Set में रह सकता है |

---

## ⚡ 3-Line Summary
English: Sets are unordered unique collections — O(1) `add`, `remove`, and `in` (unlike list's O(n)). Use them for deduplication, fast membership checks, and set math (`|`, `&`, `-`, `^`). `frozenset` is the immutable version — usable as dict keys or as set elements.
Hindi: Sets unique, unordered हैं — O(1) add/remove/in (list O(n) से fast)। Deduplication, fast lookup, set math के लिए। `frozenset` = immutable set — dict key बन सकता है।

---

## ➡️ Next Topic
**066. Set Methods** — update, intersection_update, symmetric_difference_update. **068. frozenset** — deep dive. **079. collections Module** — Counter, deque, OrderedDict, namedtuple.
