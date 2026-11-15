---

# Q256. zip / dict Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 6 handy `zip` and `dict` tricks: build a dict from two lists, transpose a matrix, `strict=True`, `dict.get`/`setdefault`/`defaultdict`, merge with `|`, and invert a dict.

```python
keys = ["a", "b", "c"]
vals = [1, 2, 3]
# -> {'a': 1, 'b': 2, 'c': 3}
```

---

## 💡 Quick Concept (2 lines only)
`zip` pairs up iterables lazily and stops at the shortest (use `strict=True` in 3.10+ to catch length bugs). `dict(zip(k, v))` builds dicts; `|` (3.9+) merges them, right side wins.
हिंदी: `zip` दो lists को जोड़ता है, `dict(zip(k, v))` से dict बनता है, और `|` दो dicts merge करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import defaultdict              # auto-creating dict

keys = ["a", "b", "c"]                           # sample keys
vals = [1, 2, 3]                                 # sample values

d = dict(zip(keys, vals))                        # 1. two lists -> dict
print(d)

matrix = [[1, 2, 3], [4, 5, 6]]                  # 2x3 matrix
print(list(zip(*matrix)))                        # 2. transpose: * unpacks rows into zip

try:
    list(zip([1, 2, 3], [1, 2], strict=True))    # 3. strict=True raises on length mismatch
except ValueError as e:
    print(e)                                     # error message

print(d.get("z", 0))                             # 4a. get with default, no KeyError

groups: dict[str, list[int]] = defaultdict(list) # 4b. missing key -> empty list
for word, n in [("x", 1), ("y", 2), ("x", 3)]:   # group numbers by letter
    groups[word].append(n)                       # no "if key not in" needed
print(dict(groups))

print({"a": 1, "b": 2} | {"b": 20, "c": 3})      # 5. merge: right side wins on conflict

print({v: k for k, v in d.items()})              # 6. invert (values must be unique/hashable)

# Output:
# {'a': 1, 'b': 2, 'c': 3}
# [(1, 4), (2, 5), (3, 6)]
# zip() argument 2 is shorter than argument 1
# 0
# {'x': [1, 3], 'y': [2]}
# {'a': 1, 'b': 20, 'c': 3}
# {1: 'a', 2: 'b', 3: 'c'}
```

---

## 🔍 Why This Works (3 lines max)
`zip(*matrix)` unpacks each row as a separate argument, so `zip` takes column tuples. `defaultdict(list)` calls `list()` for any missing key, avoiding `setdefault` boilerplate. `a | b` creates a new dict where later keys overwrite earlier ones.
हिंदी: `zip(*matrix)` rows को अलग-अलग arguments बना देता है, इसलिए columns मिलते हैं (transpose)।

---

## ⚡ Alternative Solution
```python
# zip_longest, unzip, and dict.setdefault / update
from itertools import zip_longest                # pad the shorter iterable

print(list(zip_longest([1, 2, 3], ["a"], fillvalue="-")))  # no data lost

pairs = [(1, "a"), (2, "b")]                     # list of pairs
nums, letters = zip(*pairs)                      # "unzip" back into two tuples
print(nums, letters)

d: dict[str, list[int]] = {}                     # plain dict
d.setdefault("k", []).append(1)                  # create-if-missing, then append
d.setdefault("k", []).append(2)                  # reuses the existing list
print(d)

# Output:
# [(1, 'a'), (2, '-'), (3, '-')]
# (1, 2) ('a', 'b')
# {'k': [1, 2]}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain zip silently drops data when lengths differ
print(list(zip([1, 2, 3], ["a", "b"])))          # [(1, 'a'), (2, 'b')] -> 3 vanished!

# ✅ Correct: strict=True (3.10+) or zip_longest when lengths must match
print(list(zip([1, 2, 3], ["a", "b", "c"], strict=True)))

# Output:
# [(1, 'a'), (2, 'b')]
# [(1, 'a'), (2, 'b'), (3, 'c')]
```

---

## 🎯 Interview Tip (1 line)
Say: "zip stops at the shortest; I use `strict=True` to fail loudly, and `zip(*x)` to transpose."

---

## 🔗 Related Questions
→ Q047 (zip with unequal lengths) | Q061 (zip manually) | Q110 (implement zip) | Q250 (itertools) | Q252 (collections)
