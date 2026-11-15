---

# Q115. Implement itertools.groupby
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `groupby(iterable, key=None)` that yields `(key, group)` for each run of **consecutive** items sharing the same key. (Unlike the real one, yours may return lists for groups.)

```python
[(k, list(g)) for k, g in groupby("AAABBA")]
# [('A', ['A','A','A']), ('B', ['B','B']), ('A', ['A'])]
```

---

## 💡 Quick Concept (2 lines only)
Walk once through the data, start a new group whenever the key changes from the previous item. It does NOT sort — equal keys far apart become separate groups.
हिंदी: सिर्फ लगातार (consecutive) बराबर keys group होती हैं — sort नहीं करता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any, Callable, Iterable, Iterator   # type hints

_SENTINEL = object()                                  # unique "no key yet" marker

def groupby(iterable: Iterable, key: Callable[[Any], Any] | None = None) -> Iterator[tuple[Any, list]]:
    key = key or (lambda x: x)                        # Step 1: default key = identity
    current_key: Any = _SENTINEL                      # key of the group being built
    group: list = []                                  # items of current group
    for item in iterable:                             # Step 2: single pass over input
        k = key(item)                                 # compute key once
        if current_key is _SENTINEL or k != current_key:  # Step 3: key changed -> new group
            if group:                                 # emit the finished group
                yield current_key, group              # (key, items)
            current_key, group = k, []                # reset for the new group
        group.append(item)                            # Step 4: add item to current group
    if group:                                         # Step 5: emit the last group
        yield current_key, group                      # (key, items)

# ============================================
# TEST CASES
# ============================================
print([(k, g) for k, g in groupby("AAABBA")])
# Expected: [('A', ['A', 'A', 'A']), ('B', ['B', 'B']), ('A', ['A'])]
print([(k, len(g)) for k, g in groupby([1, 1, 2, 3, 3, 3])])     # Expected: [(1, 2), (2, 1), (3, 3)]
print([(k, g) for k, g in groupby(["apple", "avocado", "banana", "blueberry", "cherry"], key=lambda w: w[0])])
# Expected: [('a', ['apple', 'avocado']), ('b', ['banana', 'blueberry']), ('c', ['cherry'])]
print(list(groupby([])))                                         # Expected: []
import itertools                                                 # compare with the real one
data = [1, 1, 2, 3, 3, 3]
print([(k, list(g)) for k, g in itertools.groupby(data)] == list(groupby(data)))  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
We only compare each item's key with the previous one, so it is O(n) with one pass. A sentinel (not `None`) marks "no group yet", because `None` can be a valid key.
हिंदी: हर item की key पिछली से compare होती है; बदलते ही नया group शुरू होता है।

---

## ⚡ Alternative Solution
```python
# Real itertools.groupby — groups are LAZY iterators tied to the underlying iteration
from itertools import groupby as ig                              # built-in version
print({k: "".join(g) for k, g in ig("aabccc")})                  # Output: {'a': 'aa', 'b': 'b', 'c': 'ccc'}
print([(k, len(list(g))) for k, g in ig("aabccc")])              # Output: [('a', 2), ('b', 1), ('c', 3)]  (run-length encoding)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to sort first -> same key appears in several groups
words = ["bob", "alice", "bill", "anna"]
print([(k, list(g)) for k, g in ig(words, key=lambda w: w[0])])
# Output: [('b', ['bob']), ('a', ['alice']), ('b', ['bill']), ('a', ['anna'])]

# ✅ Correct: sort by the same key first
print([(k, list(g)) for k, g in ig(sorted(words), key=lambda w: w[0])])
# Output: [('a', ['alice', 'anna']), ('b', ['bill', 'bob'])]

# ❌ Also wrong: real groupby groups are consumed when you advance — materialise them first
gs = list(ig("aabb"))                                            # advances past every group
print([(k, list(g)) for k, g in gs])                             # Output: [('a', []), ('b', [])]
```

---

## 🎯 Interview Tip (1 line)
Say: "groupby only groups consecutive items, so sort by the same key first — otherwise use a dict/defaultdict to group; and consume each group before advancing."

---

## 🔗 Related Questions
→ Q064 (group list by key) | Q114 (itertools.chain) | Q066 (count occurrences) | Q250 (itertools examples)
