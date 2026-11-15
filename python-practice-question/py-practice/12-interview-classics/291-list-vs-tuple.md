---

# Q291. list vs tuple
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
What are the differences between a `list` and a `tuple`? When do you choose each?

---

## 💡 Quick Concept (2 lines only)
A list is mutable (can change after creation); a tuple is immutable, hashable (if its items are) and slightly smaller/faster.
हिंदी: List बदल सकती है, tuple नहीं बदलता — इसलिए tuple dict key बन सकता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys  # for getsizeof

lst = [1, 2, 3]  # Step 1: mutable list
tup = (1, 2, 3)  # Step 2: immutable tuple

lst.append(4)  # lists can grow
lst[0] = 99  # and items can change

# ============================================
# TEST CASES
# ============================================
print(lst)  # Expected: [99, 2, 3, 4]
try:
    tup[0] = 99  # try to modify the tuple
except TypeError as e:  # tuples reject item assignment
    print(e)  # Expected: 'tuple' object does not support item assignment

print(sys.getsizeof([1, 2, 3]), sys.getsizeof((1, 2, 3)))  # Expected: 88 64 (tuple smaller; exact sizes vary by build)

grid = {(0, 0): "origin", (1, 2): "point"}  # tuple as dict key
print(grid[(1, 2)])  # Expected: point
try:
    {[1, 2]: "x"}  # list as dict key
except TypeError as e:  # lists are unhashable
    print(e)  # Expected: unhashable type: 'list'

print(hash((1, 2)) == hash((1, 2)))  # Expected: True (hashable)
```

---

## 🔍 Why This Works (3 lines max)
Immutability lets a tuple compute a stable hash, so it works as a dict key or set member; a list can change, so it can't. Tuples also signal "fixed record" (e.g. coordinates), lists signal "collection that grows".
हिंदी: Immutable = hashable; इसलिए fixed data के लिए tuple, बदलने वाले data के लिए list।

---

## ⚡ Alternative Solution
```python
from typing import NamedTuple  # tuple with field names


class Point(NamedTuple):  # immutable record
    x: int  # field x
    y: int  # field y


p = Point(1, 2)  # create
print(p.x, p[1], p)  # Expected: 1 2 Point(x=1, y=2)

t = ([1], 2)  # tuple containing a mutable list
t[0].append(5)  # allowed: the tuple holds the same list object
print(t)  # Expected: ([1, 5], 2)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: thinking a one-item tuple is (1)
not_tuple = (1)  # this is just int 1
print(type(not_tuple))  # <class 'int'>

# ✅ Correct: trailing comma
one = (1,)  # real tuple
print(type(one))  # Expected: <class 'tuple'>
```

---

## 🎯 Interview Tip (1 line)
Say: "Tuple = immutable and hashable, so usable as a dict key; but a tuple holding a list is only shallowly immutable."

---

## 🔗 Related Questions
→ Q008 (tuple with mutable element) | Q292 (mutable vs immutable) | Q175 (mutability and hashability) | Q242 (unpacking)
