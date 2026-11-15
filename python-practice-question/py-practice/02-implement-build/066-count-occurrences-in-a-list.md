---

# Q066. Count Occurrences in a List
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `count_items(items)` that returns a dict of `{item: how_many_times}` without using `Counter`.

```python
count_items("banana")  # {'b': 1, 'a': 3, 'n': 2}
```

---

## 💡 Quick Concept (2 lines only)
Walk the items and do `counts[item] = counts.get(item, 0) + 1`. `.get(..., 0)` gives a default so missing keys do not raise `KeyError`.
हिंदी: `.get(item, 0) + 1` से हर item की गिनती बढ़ाओ — नया item हो तो 0 से शुरू होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Hashable, Iterable  # items must be hashable (dict keys)

def count_items(items: Iterable[Hashable]) -> dict:
    counts: dict = {}                           # Step 1: item -> count
    for it in items:                            # Step 2: visit every item
        counts[it] = counts.get(it, 0) + 1      # Step 3: current count (default 0) + 1
    return counts                               # Step 4: return the tally

# ============================================
# TEST CASES
# ============================================

print(count_items("banana"))     # Expected: {'b': 1, 'a': 3, 'n': 2}  (first-seen order)
print(count_items([]))           # Expected: {}
print(count_items([1, 1.0, True]))   # Expected: {1: 3}  (1 == 1.0 == True and same hash -> one key!)
```

---

## 🔍 Why This Works (3 lines max)
Each item maps to its running total; `get` supplies 0 the first time. One pass, O(n). Items are keyed by hash/equality, so `1`, `1.0`, `True` merge.
हिंदी: एक ही pass में गिनती हो जाती है; `1`, `1.0`, `True` एक ही key माने जाते हैं।

---

## ⚡ Alternative Solution
```python
from collections import Counter, defaultdict    # stdlib helpers

c = Counter("banana")                           # one-liner tally
print(c)                                        # Expected: Counter({'a': 3, 'n': 2, 'b': 1})
print(c.most_common(2))                         # Expected: [('a', 3), ('n', 2)]
print(c["z"])                                   # Expected: 0  (missing key -> 0, NOT KeyError, and does not insert)

dd = defaultdict(int)                           # int() == 0 as default
for ch in "aab":                                # loop over characters
    dd[ch] += 1                                 # no .get needed
print(dict(dd))                                 # Expected: {'a': 2, 'b': 1}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: incrementing a missing key on a plain dict
d = {}
# d["a"] += 1        # KeyError: 'a' (verified)

# ❌ Wrong: items.count(x) inside a loop -> O(n^2)
# [(x, items.count(x)) for x in set(items)]
# ✅ Correct: single pass with .get / defaultdict(int) / Counter
```

---

## 🎯 Interview Tip (1 line)
Show the manual `.get` loop first, then say "in production I'd use `Counter` and `most_common`."

---

## 🔗 Related Questions
→ Q067 (find duplicates) | Q079 (count key occurrences in nested dicts) | Q252 (collections) | Q054 (count vowels)
