---

# Q064. Group List by Key
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `group_by(items, key)` that returns a dict mapping `key(item)` to the list of items having that key.

```python
group_by(["apple", "bob", "cat", "dodo", "egg"], len)
# {5: ['apple'], 3: ['bob', 'cat', 'egg'], 4: ['dodo']}
```

---

## 💡 Quick Concept (2 lines only)
For each item compute its key, then append the item to `groups[key]`, creating the list on first use (`setdefault` or `defaultdict(list)`).
हिंदी: हर item की key निकालो और उसी key वाली list में जोड़ दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Callable, Iterable  # type hints
from operator import itemgetter        # fast key function for dicts

def group_by(items: Iterable, key: Callable) -> dict:
    groups: dict = {}                              # Step 1: key -> list of items
    for it in items:                               # Step 2: visit every item
        groups.setdefault(key(it), []).append(it)  # Step 3: create list if missing, then append
    return groups                                  # Step 4: return the groups

# ============================================
# TEST CASES
# ============================================

print(group_by(["apple", "bob", "cat", "dodo", "egg"], len))
# Expected: {5: ['apple'], 3: ['bob', 'cat', 'egg'], 4: ['dodo']}
people = [{"n": "A", "city": "X"}, {"n": "B", "city": "Y"}, {"n": "C", "city": "X"}]
print(group_by(people, itemgetter("city")))
# Expected: {'X': [{'n': 'A', 'city': 'X'}, {'n': 'C', 'city': 'X'}], 'Y': [{'n': 'B', 'city': 'Y'}]}
print(group_by([1, 2, 3, 4], lambda n: n % 2 == 0))   # Expected: {False: [1, 3], True: [2, 4]}
```

---

## 🔍 Why This Works (3 lines max)
`setdefault(k, [])` returns the existing list or inserts a new one, so we can always `.append`. Dict keeps first-seen key order and items keep their input order. One pass: O(n).
हिंदी: `setdefault` list देता है (या बनाता है), इसलिए हर बार सीधे append कर सकते हैं।

---

## ⚡ Alternative Solution
```python
from collections import defaultdict            # auto-creates missing lists
from itertools import groupby                  # groups only ADJACENT equal keys

people = [{"n": "A", "city": "X"}, {"n": "B", "city": "Y"}, {"n": "C", "city": "X"}]
dd = defaultdict(list)                         # missing key -> []
for p in people:                               # one pass
    dd[p["city"]].append(p["n"])               # append the name under its city
print(dict(dd))                                # Expected: {'X': ['A', 'C'], 'Y': ['B']}

words = ["apple", "cat", "bob", "dog", "egg"]  # sample words
print({k: list(g) for k, g in groupby(words, key=len)})
# Expected: {5: ['apple'], 3: ['cat', 'bob', 'dog', 'egg']}  <- only adjacent items grouped
print({k: list(g) for k, g in groupby(sorted(words, key=len), key=len)})
# Expected: {3: ['cat', 'bob', 'dog', 'egg'], 5: ['apple']}  <- sort by the same key first
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: groupby on UNSORTED data - splits equal keys into many groups
# groupby(["a1","b","a2"], key=lambda s: s[0]) -> groups: a, b, a  (two separate 'a' groups)
# In a dict comprehension the later 'a' group OVERWRITES the earlier one -> data loss!

# ❌ Wrong: reading a defaultdict creates keys
d = defaultdict(list)
d["x"]                              # just reading adds the key
print(dict(d))                      # {'x': []} (verified)
# ✅ Correct: sort before groupby, or use setdefault/defaultdict when appending
```

---

## 🎯 Interview Tip (1 line)
Say: "`defaultdict(list)` for unsorted data; `itertools.groupby` only groups consecutive runs, so sort first."

---

## 🔗 Related Questions
→ Q115 (implement itertools.groupby) | Q066 (count occurrences) | Q065 (sort dicts) | Q252 (collections)
