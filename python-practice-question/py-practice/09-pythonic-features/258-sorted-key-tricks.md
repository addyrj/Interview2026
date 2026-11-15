---

# Q258. sorted() key Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 6 `sorted()` / `key=` tricks: sort by length, case-insensitive, multi-key with tuples, descending on one field and ascending on another, `itemgetter/attrgetter`, and `cmp_to_key`.

```python
people = [("Ana", 30), ("Bob", 25), ("Cid", 30)]
# Sort by age DESC, then name ASC -> ?
```

---

## 💡 Quick Concept (2 lines only)
`key=` is called ONCE per element and the results are compared; Python's sort is stable (equal keys keep original order). Tuples as keys give multi-level sorting.
हिंदी: `key` function हर element पर एक बार चलता है; sort stable है — बराबर keys का original order बना रहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from operator import itemgetter, attrgetter      # fast key helpers
from functools import cmp_to_key                 # adapt old-style comparators
from dataclasses import dataclass                # simple object for attrgetter

words = ["banana", "Apple", "cherry", "fig"]     # sample words
print(sorted(words, key=len))                    # 1. by length
print(sorted(words, key=str.lower))              # 2. case-insensitive (str.lower as key)

people = [("Ana", 30), ("Bob", 25), ("Cid", 30)] # (name, age)
print(sorted(people, key=lambda p: (-p[1], p[0])))  # 3. age DESC (negate), name ASC

print(sorted(people, key=itemgetter(1)))         # 4. itemgetter: sort by index 1 (stable)

@dataclass
class User:
    name: str                                    # name field
    score: int                                   # score field

users = [User("x", 5), User("y", 9), User("z", 1)]  # sample users
print([u.name for u in sorted(users, key=attrgetter("score"), reverse=True)])  # 5. attrgetter + reverse

def compare(a: str, b: str) -> int:
    return (a + b > b + a) - (a + b < b + a)     # a before b if a+b is "bigger" (descending below)

nums = ["3", "30", "34", "5", "9"]               # largest-number problem
print("".join(sorted(nums, key=cmp_to_key(compare), reverse=True)))  # 6. custom comparator

# Output:
# ['fig', 'Apple', 'banana', 'cherry']
# ['Apple', 'banana', 'cherry', 'fig']
# [('Ana', 30), ('Cid', 30), ('Bob', 25)]
# [('Bob', 25), ('Ana', 30), ('Cid', 30)]
# ['y', 'x', 'z']
# 9534330
```

---

## 🔍 Why This Works (3 lines max)
Negating a number flips its order inside a tuple key, so you can mix ASC and DESC. `itemgetter`/`attrgetter` are C-level and faster than lambdas. `cmp_to_key` wraps a two-argument comparator into a key for the rare cases a key can't express.
हिंदी: Number पर minus लगाने से उसका order उल्टा हो जाता है — tuple key में ASC + DESC mix करने की यही trick है।

---

## ⚡ Alternative Solution
```python
# Two-pass stable sort (works even for non-numeric DESC fields)
people = [("Ana", 30), ("Bob", 25), ("Cid", 30)]  # (name, age)

step1 = sorted(people, key=lambda p: p[0], reverse=True)   # secondary key first: name DESC
step2 = sorted(step1, key=lambda p: p[1])                  # primary key last: age ASC (stable keeps name order)
print(step2)

# Output:
# [('Bob', 25), ('Cid', 30), ('Ana', 30)]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting sort() to return the list
nums = [3, 1, 2]
result = nums.sort()                             # sorts IN PLACE, returns None
print(result)                                    # None

# ✅ Correct: sorted() returns a new list; list.sort() mutates and returns None
print(sorted([3, 1, 2]))

# Output:
# None
# [1, 2, 3]
```

---

## 🎯 Interview Tip (1 line)
Say: "Sort is stable (Timsort, O(n log n)); I use tuple keys for multi-level sorting and `-x` or two-pass sorting for mixed directions."

---

## 🔗 Related Questions
→ Q010 (sorted vs list.sort) | Q065 (sort list of dicts by multiple keys) | Q113 (sorted with key) | Q255 (decorator tricks)
