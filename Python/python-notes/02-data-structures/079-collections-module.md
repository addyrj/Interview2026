---

# 079. collections Module — Complete Guide
# हिंदी में: collections Module — पूरी Guide

---

## 🔵 Simple Definition (English)
The `collections` module provides specialized container types that extend built-in `dict`, `list`, and `tuple`. The most important: `Counter` (counting), `defaultdict` (auto-default values), `OrderedDict` (LRU cache), `namedtuple` (lightweight data classes), `deque` (fast both-end operations). Knowing these shows Python depth in interviews.

## 🔵 सरल परिभाषा (Hindi)
`collections` module specialized containers provide करता है जो built-in `dict`, `list`, `tuple` को extend करते हैं। Most important: `Counter` (counting), `defaultdict` (auto-default), `OrderedDict` (LRU cache), `namedtuple` (lightweight data class), `deque` (fast both-end)।

---

## 💻 Code Example — Counter
```python
from collections import Counter

# ─── Counter — count hashable objects ────────────────────────────
# Create from iterable:
word_count = Counter(["apple", "banana", "apple", "cherry", "apple", "banana"])
print(word_count)          # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Create from string:
char_count = Counter("abracadabra")
print(char_count)          # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})

# From dict:
manual = Counter({"a": 3, "b": 1})

# Access — like dict:
print(word_count["apple"])   # 3
print(word_count["missing"]) # 0 (not KeyError! — counter returns 0)

# Most common:
print(word_count.most_common(2))   # [('apple', 3), ('banana', 2)]
print(word_count.most_common())    # all, sorted by count

# Arithmetic:
c1 = Counter(a=3, b=2)
c2 = Counter(a=1, b=5, c=2)
print(c1 + c2)    # Counter({'b': 7, 'a': 4, 'c': 2}) — add counts
print(c1 - c2)    # Counter({'a': 2}) — subtract (drop negatives/zeros)
print(c1 & c2)    # Counter({'a': 1, 'b': 2}) — intersection (min counts)
print(c1 | c2)    # Counter({'b': 5, 'a': 3, 'c': 2}) — union (max counts)

# Update (add more counts):
word_count.update(["apple", "date"])
print(word_count["apple"])   # 4

# Convert to dict:
print(dict(word_count))

# Real use: find most common characters:
def top_chars(text: str, n: int = 3) -> list[tuple[str, int]]:
    return Counter(text.lower()).most_common(n)

print(top_chars("Hello, World!", 3))   # [('l', 3), ('o', 2), ('h', 1)]
```

## 💻 Code Example — defaultdict, namedtuple, deque
```python
from collections import defaultdict, namedtuple, deque, OrderedDict

# ─── defaultdict — auto-creates missing keys ──────────────────────
# Group items by category:
products = [
    ("phones", "iPhone 15"),
    ("laptops", "MacBook Pro"),
    ("phones", "Pixel 8"),
    ("laptops", "Dell XPS"),
    ("phones", "Samsung S24"),
]

by_category = defaultdict(list)
for category, product in products:
    by_category[category].append(product)

print(dict(by_category))
# {'phones': ['iPhone 15', 'Pixel 8', 'Samsung S24'], 'laptops': ['MacBook Pro', 'Dell XPS']}

# Counting (defaultdict(int)):
word_freq = defaultdict(int)
for word in "the quick brown fox jumps over the lazy dog the".split():
    word_freq[word] += 1    # no KeyError — starts at 0

# Nested defaultdict:
nested = defaultdict(lambda: defaultdict(int))
nested["city"]["count"] += 1
nested["city"]["total"] += 100

# ─── namedtuple — lightweight immutable data object ───────────────
# Old style:
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)      # 3 4 — access by name
print(p[0], p[1])    # 3 4 — still works as tuple
print(p)             # Point(x=3, y=4)

# With defaults (Python 3.6.1+):
Point3D = namedtuple("Point3D", ["x", "y", "z"], defaults=[0])
p = Point3D(1, 2)    # z defaults to 0
print(p)             # Point3D(x=1, y=2, z=0)

# Convert to dict:
print(p._asdict())   # {'x': 1, 'y': 2, 'z': 0}

# Real use — API response data:
TariffCode = namedtuple("TariffCode", ["code", "description", "rate"])
tariff = TariffCode("8517.12.00", "Smartphones", 0.0)
print(tariff.description)   # "Smartphones"

# Modern alternative — dataclass (mutable, more features):
from dataclasses import dataclass
@dataclass(frozen=True)  # frozen=True → immutable (like namedtuple)
class TariffItem:
    code: str
    description: str
    rate: float = 0.0

# ─── deque — double-ended queue ──────────────────────────────────
# O(1) append/pop from BOTH ends (list is O(n) for left side!)
d = deque([1, 2, 3])

d.append(4)          # add to right
d.appendleft(0)      # add to left — O(1)!
d.pop()              # remove from right
d.popleft()          # remove from left — O(1)!

print(d)   # deque([1, 2, 3])

# Bounded deque (auto-drops oldest when full):
recent = deque(maxlen=3)
for i in range(5):
    recent.append(i)
print(recent)   # deque([2, 3, 4], maxlen=3) — oldest dropped

# BFS (breadth-first search) pattern:
from collections import deque

def bfs(graph: dict, start: str) -> list[str]:
    visited = set()
    queue = deque([start])
    order = []
    
    while queue:
        node = queue.popleft()   # O(1) — use deque, not list!
        if node not in visited:
            visited.add(node)
            order.append(node)
            queue.extend(graph.get(node, []))
    
    return order

# ─── OrderedDict — dict with guaranteed order + move_to_end ───────
# Python 3.7+ dicts maintain insertion order, so OrderedDict is mainly
# used for LRU cache implementation (move_to_end() is the key feature):

lru = OrderedDict()
lru["a"] = 1
lru["b"] = 2
lru["c"] = 3

# Access "a" → move to end (most recently used):
lru.move_to_end("a")
print(list(lru.keys()))   # ['b', 'c', 'a']

# Evict least recently used (first item):
lru.popitem(last=False)   # removes 'b'
print(list(lru.keys()))   # ['c', 'a']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python Counter:
from collections import Counter
c = Counter(["a", "b", "a", "c", "a"])
print(c.most_common(2))   # [('a', 3), ('b', 1)]

# Python deque:
from collections import deque
q = deque()
q.append(1); q.appendleft(0)   # O(1) both ends
```

```javascript
// JavaScript — no built-in Counter equivalent:
const items = ["a", "b", "a", "c", "a"];
const counts = items.reduce((acc, x) => ({...acc, [x]: (acc[x]||0)+1}), {});

// No built-in deque — use Array:
const q = [];
q.push(1);       // append right O(1)
q.unshift(0);    // append left — O(n)! (shifts all elements)
q.shift();       // remove left — O(n)!
```

Key difference: JS has no `deque` — `Array.unshift/shift` are O(n). Python `deque.appendleft/popleft` are O(1). For BFS in JS: use array + shift (slow) or implement linked list queue.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using list instead of deque for queue
```python
# Wrong — list.pop(0) is O(n):
queue = [1, 2, 3]
queue.pop(0)    # shifts all elements left — O(n)!

# Correct — deque.popleft() is O(1):
queue = deque([1, 2, 3])
queue.popleft()    # O(1)
```

❌ Mistake 2: Expecting Counter to handle missing keys like a regular dict
```python
c = Counter(["a", "b"])

# Counter returns 0 for missing keys (NO KeyError):
print(c["z"])   # 0 — not KeyError!

# But 'z' not actually added to counter:
print("z" in c)   # False (still not in counter)
print(c["z"])     # 0 — but doesn't add 'z'
```

---

## 🧠 Tricky Interview Question

**Q**: When would you use `Counter` vs `defaultdict(int)` for counting?

**Answer**: Both count. `Counter` has extras: `.most_common(n)`, arithmetic (`c1 + c2`, `c1 - c2`), returns `0` for missing keys (not error), and `update()` to add more counts. `defaultdict(int)` is simpler — just a dict that creates `0` for missing keys. Use `Counter` when: you need most common items, want to add/subtract counts, or want set operations. Use `defaultdict(int)` when: you just need counting without the extras — slightly simpler to reason about.

---

## ⚫ Interview Questions + Answers

Q1: What is the time complexity of `deque` operations vs `list`?
A1: `deque`: append/pop from right O(1), appendleft/popleft O(1), middle access O(n). `list`: append/pop from right O(1), insert/pop from left O(n) (shifts all), index access O(1). Use `deque` when you need: FIFO queue (BFS), sliding window, bounded buffer. Use `list` when you need: index access, sorting, slicing. Rule: "queue behavior" → deque; "array behavior" → list.

Q2: How does `namedtuple` compare to `dataclass`?
A2: `namedtuple`: immutable (like tuple), hashable, accessible by index AND name, very memory efficient, no methods. `dataclass`: mutable by default (use `frozen=True` for immutable), not hashable by default, can have methods, supports type hints with defaults natively, `__post_init__` for validation. Use `namedtuple` for: simple data containers with no logic, when you need tuple unpacking or indexing. Use `dataclass` for: data with methods, validation, default factories. In Python 3.7+: prefer `dataclass` for new code — more features.

Q3: What are the use cases for `OrderedDict` in Python 3.7+?
A3: Since Python 3.7+ dicts maintain insertion order, `OrderedDict` is rarely needed for just ordering. Still valuable for: (1) `move_to_end(key, last=True/False)` — move any key to front/end in O(1). Critical for LRU cache. (2) `popitem(last=False)` — remove first (oldest) item in O(1). (3) Equality with order: `OrderedDict([('a',1),('b',2)]) != OrderedDict([('b',2),('a',1)])` but regular dicts compare equal. Use `OrderedDict` when you need `move_to_end()` — mainly for LRU cache implementation.

Q4: How does `Counter.most_common()` work and what is its time complexity?
A4: `counter.most_common(n)` returns the n most common elements as `[(element, count), ...]` sorted by count descending. Time: O(n log k) where k is number of unique elements (uses `heapq.nlargest`). `most_common()` with no argument returns ALL elements sorted: O(k log k). For "find top 3 words in document": `Counter(words.split()).most_common(3)`. `most_common` uses a heap — much faster than sorting when n << k (only need top 3 out of 10000 words).

Q5: What is `Counter.elements()` and `Counter.subtract()`?
A5: `counter.elements()` yields each element repeated by its count: `Counter({'a': 3, 'b': 1}).elements()` → `['a', 'a', 'a', 'b']`. Useful for: reconstructing the original sequence, creating test data, dealing cards (`Counter({'A':4,'K':4,...}).elements()`). `counter.subtract(iterable_or_counter)` subtracts counts in-place (unlike `-` which drops negatives): `c = Counter(a=4, b=2); c.subtract(a=1, b=3)` → `Counter({'a': 3, 'b': -1})`. Negative counts allowed with `subtract`, not with `-`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Counter | Dict for counting elements | Elements count करने वाला dict |
| defaultdict | Dict with auto-default values | Auto-default values वाला dict |
| namedtuple | Immutable data class | Immutable data class |
| deque | Double-ended queue | Double-ended queue |
| OrderedDict | Dict with move_to_end | Dict with move_to_end |
| most_common | Top n by count | Count से top n |
| move_to_end | Move key to front/back | Key को front/back move |

---

## ⚡ 3-Line Summary
English: `Counter` for counting + top-n; `defaultdict(list/int)` for grouping and counting; `deque` for O(1) queue operations (not list!). `namedtuple` for simple immutable data; `dataclass` for richer data objects. These containers show Python expertise in interviews — always prefer them over manual dict/list patterns.
Hindi: `Counter` = counting + top-n। `defaultdict(list)` = grouping। `deque` = O(1) queue (list नहीं!)। `namedtuple` = simple immutable data। Interviews में ये dikhane से Python expertise show होती है।

---

## ➡️ Next Topic
**080. Choosing the Right Data Structure** — when to use which. **081. OOP Introduction** — classes, objects, self. **109. dataclasses** — modern data containers.
