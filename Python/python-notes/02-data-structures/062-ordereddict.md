---

# 062. OrderedDict
# हिंदी में: OrderedDict (क्रम याद रखने वाला Dict)

---

## 🔵 Simple Definition (English)
`OrderedDict` is a dict subclass from `collections` that remembers insertion order and adds order-aware tools: `move_to_end()`, `popitem(last=False)`, and order-sensitive equality. Since Python 3.7 normal dicts also keep insertion order, so OrderedDict is now needed only for these extra features.

## 🔵 सरल परिभाषा (Hindi)
`OrderedDict` `collections` का dict subclass है जो insertion order याद रखता है और order वाले extra tools देता है: `move_to_end()`, `popitem(last=False)`, और order-sensitive equality। Python 3.7 से normal dict भी order रखता है, इसलिए OrderedDict अब सिर्फ इन extra features के लिए चाहिए।

---

## 🔴 Problem it Solves
Before Python 3.7, a dict had no guaranteed order, so you needed OrderedDict for predictable output. Today the ordering part is solved by plain `dict`, but a plain dict cannot cheaply move a key to the end or pop from the front. Those operations are exactly what you need for an LRU cache, a queue of recent items, or when order must be part of equality.

## 🔴 यह क्यों बना? (Hindi)
Python 3.7 से पहले dict का order guaranteed नहीं था, तब OrderedDict चाहिए था। अब order का काम plain dict करता है, पर plain dict में key को सस्ते में end तक ले जाना या front से pop करना नहीं होता। LRU cache, recent-items queue, या equality में order चाहिए तो OrderedDict।

---

## 🟢 How it Works — Step by Step

```
Step 1 → od = OrderedDict()           → a dict + a doubly linked list of keys
Step 2 → od["a"] = 1                  → key appended at the end of the list
Step 3 → od.move_to_end("a")          → relinks that key to the end in O(1)
Step 4 → od.move_to_end("a", last=False) → moves key to the front
Step 5 → od.popitem(last=False)       → removes the OLDEST item (FIFO); last=True removes newest (LIFO)
Step 6 → od1 == od2                   → True only if same items AND same order
```

## 🟢 कैसे काम करता है? (Hindi)
```
OrderedDict = dict + keys की doubly linked list
नई key → list के end में
move_to_end(k) → key को end में O(1) में ले जाता है
popitem(last=False) → सबसे पुराना item निकालता है
दो OrderedDict equal तभी जब items और order दोनों same
```

---

## 🟡 Real World Example
An LRU (Least Recently Used) cache for a FastAPI service: store the last 100 product lookups. When a key is read, `move_to_end(key)` marks it as recently used. When the cache is full, `popitem(last=False)` drops the oldest. Same idea powers "recently viewed restaurants" on Zomato.

## 🟡 Real Example Hindi mein
FastAPI service में LRU cache: आख़िरी 100 product lookups store करो। Key पढ़ने पर `move_to_end(key)` से उसे "हाल में use हुआ" mark करो। Cache full हो तो `popitem(last=False)` सबसे पुराना हटाता है। Zomato के "recently viewed restaurants" में भी यही idea है।

---

## 💻 Code Example — Basic
```python
# Basic: OrderedDict special features
from collections import OrderedDict          # import the class

od: OrderedDict[str, int] = OrderedDict()    # empty ordered dict
od["a"] = 1                                  # insert first
od["b"] = 2                                  # insert second
od["c"] = 3                                  # insert third
print(list(od))                              # Output: ['a', 'b', 'c']

od.move_to_end("a")                          # move key 'a' to the end
print(list(od))                              # Output: ['b', 'c', 'a']

od.move_to_end("a", last=False)              # move 'a' back to the front
print(list(od))                              # Output: ['a', 'b', 'c']

print(od.popitem(last=False))                # Output: ('a', 1)  (removes oldest)
print(od.popitem())                          # Output: ('c', 3)  (removes newest)
print(od)                                    # Output: OrderedDict({'b': 2})

# Equality: order matters between two OrderedDicts
x = OrderedDict([("a", 1), ("b", 2)])        # a then b
y = OrderedDict([("b", 2), ("a", 1)])        # b then a
print(x == y)                                # Output: False (different order)

# But a plain dict ignores order in equality
print(dict(x) == dict(y))                    # Output: True
```

## 💻 Code Example — Advanced
```python
# Advanced: production-style LRU cache using OrderedDict
from __future__ import annotations           # modern hints
from collections import OrderedDict          # ordered storage
from typing import Generic, TypeVar          # generic cache types

K = TypeVar("K")                             # key type
V = TypeVar("V")                             # value type


class LRUCache(Generic[K, V]):
    """Least Recently Used cache with fixed capacity."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:                    # validate input
            raise ValueError("capacity must be > 0")   # clear error
        self._capacity: int = capacity       # max items allowed
        self._data: OrderedDict[K, V] = OrderedDict()  # key -> value, oldest first
        self.hits: int = 0                   # statistics: found in cache
        self.misses: int = 0                 # statistics: not found

    def get(self, key: K) -> V | None:
        """Return value and mark it as recently used."""
        if key not in self._data:            # cache miss
            self.misses += 1                 # count the miss
            return None                      # nothing to return
        self._data.move_to_end(key)          # mark as most recent (O(1))
        self.hits += 1                       # count the hit
        return self._data[key]               # return stored value

    def put(self, key: K, value: V) -> None:
        """Insert/update value, evicting the oldest item if full."""
        if key in self._data:                # updating existing key
            self._data.move_to_end(key)      # refresh its recency
        self._data[key] = value              # store the value
        if len(self._data) > self._capacity: # over capacity?
            self._data.popitem(last=False)   # evict least recently used (front)

    def keys(self) -> list[K]:
        """Keys from least to most recently used."""
        return list(self._data)              # copy of current order


cache: LRUCache[str, int] = LRUCache(capacity=2)   # tiny cache for demo
cache.put("a", 1)                            # cache: a
cache.put("b", 2)                            # cache: a, b
print(cache.get("a"))                        # Output: 1  (a becomes most recent)
cache.put("c", 3)                            # full -> evicts 'b' (least recent)
print(cache.get("b"))                        # Output: None
print(cache.keys())                          # Output: ['a', 'c']
print(cache.hits, cache.misses)              # Output: 1 1

try:                                         # invalid capacity
    LRUCache(0)                              # should raise
except ValueError as err:                    # handle it
    print("Error:", err)                     # Output: Error: capacity must be > 0

# Python's built-in alternative for functions:
from functools import lru_cache              # decorator version of same idea


@lru_cache(maxsize=2)                        # keeps last 2 results
def square(n: int) -> int:
    """Pretend expensive computation."""
    return n * n                             # simple work


square(2); square(3); square(2)              # fill and reuse the cache
print(square.cache_info().hits)              # Output: 1
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import OrderedDict
od = OrderedDict(a=1, b=2)
od.move_to_end("a")                  # a moves last
od.popitem(last=False)               # remove first
```

```javascript
// JavaScript: Map keeps insertion order and is the closest match
const m = new Map([["a", 1], ["b", 2]]);
const v = m.get("a"); m.delete("a"); m.set("a", v);   // "move to end" = delete + set
const firstKey = m.keys().next().value; m.delete(firstKey); // pop first
// Note: plain JS objects order integer-like keys numerically first!
```

Key difference: JS `Map` is always ordered but has no `move_to_end`; you delete and re-insert. Python plain `dict` is also ordered (3.7+). FastAPI link: use OrderedDict (or `functools.lru_cache`) for in-process caches of expensive lookups; for multi-worker setups use Redis instead because each worker has its own memory.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using OrderedDict just for ordering
```python
# Wrong (old habit):
# d = OrderedDict()   # not needed only for order
# Correct:
d = {}                # plain dict keeps insertion order in 3.7+
```

❌ Mistake 2: Assuming order is ignored in equality
```python
# OrderedDict([("a",1),("b",2)]) == OrderedDict([("b",2),("a",1)])  -> False
# Compare with plain dicts if order should not matter
```

❌ Mistake 3: Forgetting that updating a key keeps its OLD position
```python
from collections import OrderedDict
od = OrderedDict(a=1, b=2)
od["a"] = 99                  # 'a' stays FIRST, it is not moved to the end
od.move_to_end("a")           # Correct: call this if you want it moved
```

---

## 🧠 Tricky Interview Question

**Q**: "Plain dicts keep insertion order now. So what is the difference between `dict` and `OrderedDict`?"

**Answer**: Four differences. (1) `OrderedDict.__eq__` with another OrderedDict is order-sensitive, plain dict equality is not. (2) `OrderedDict` has `move_to_end()` and `popitem(last=False)`, which plain dict lacks (`dict.popitem()` is LIFO only). (3) OrderedDict is designed for frequent reordering (linked list inside), so it is good for LRU caches. (4) Plain dict uses less memory and is faster for normal use. So use OrderedDict only when you need reordering or order-aware equality.

---

## ⚫ Interview Questions + Answers

Q1: Is OrderedDict still useful after Python 3.7?
A1: Yes, but for niche cases: `move_to_end`, `popitem(last=False)`, order-sensitive equality, and explicit signalling that order is part of the logic. For simple "keep insertion order", plain `dict` is enough and faster.

Q2: How would you implement an LRU cache?
A2: Use an OrderedDict: on `get`, call `move_to_end(key)`; on `put`, insert/update and `move_to_end`; if `len > capacity`, `popitem(last=False)` to evict the oldest. All operations are O(1). In practice use `functools.lru_cache` for function results.

Q3: What does `popitem(last=False)` do?
A3: It removes and returns the first (oldest) key-value pair. With `last=True` (default) it removes the newest pair. Plain `dict.popitem()` can only remove the newest.

Q4: How does equality work for OrderedDict?
A4: OrderedDict vs OrderedDict: equal only if items and order match. OrderedDict vs plain dict: order is ignored. This asymmetry can surprise you, so be careful when comparing mixed types.

Q5: Does changing an existing key's value change its position?
A5: No. The key keeps its original position. To reposition it, call `move_to_end(key)` or delete and re-insert it. This is the same for plain dict and OrderedDict.

---

## 🔷 When to Use OrderedDict

✅ Use when:
- Building an LRU / recently-used cache
- You need `move_to_end` or FIFO `popitem(last=False)`
- Order must matter for equality

❌ Avoid when:
- You only need to preserve insertion order (plain dict)
- You need a shared cache across processes (use Redis)
- Memory/performance is critical for large simple dicts

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Insertion order | Order in which keys were added | Keys जोड़ने का क्रम |
| LRU | Least Recently Used eviction | सबसे कम हाल में use हुआ हटाना |
| FIFO | First in, first out | पहले आया, पहले गया |
| `move_to_end` | Reposition a key | Key को end/front में ले जाना |
| Eviction | Removing items to free space | जगह बनाने के लिए हटाना |
| Cache hit/miss | Found / not found in cache | Cache में मिला / नहीं मिला |

---

## ⚡ 3-Line Summary
English: Plain dicts keep insertion order since 3.7, so OrderedDict is only needed for `move_to_end`, `popitem(last=False)` and order-sensitive equality. It is the classic tool for an LRU cache. Updating a value never moves its key.
Hindi: Python 3.7 से plain dict order रखता है, इसलिए OrderedDict सिर्फ `move_to_end`, `popitem(last=False)` और order-sensitive equality के लिए चाहिए। LRU cache का classic tool है। Value update करने से key की position नहीं बदलती।

---

## ➡️ Next Topic
**063. Counter** — count hashable items fast, `most_common`, arithmetic between counters.
