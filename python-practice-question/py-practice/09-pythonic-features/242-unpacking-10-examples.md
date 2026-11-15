---

# Q242. Unpacking — 10 Examples
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 10 unpacking patterns: tuple, swap, star-rest, middle, nested, in function calls, dict merge, in loops, ignoring values and star in literals.

---

## 💡 Quick Concept (2 lines only)
Unpacking assigns items of an iterable to names in one line; `*name` collects the rest into a list; `**` unpacks dicts. Works on ANY iterable, not only tuples.
हिंदी: Unpacking = iterable के items को सीधे variables में बाँटना — `*` बाकी सब list में ले लेता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
a, b = (1, 2)                                   # 1. basic tuple unpacking
print(a, b)                                     # Expected: 1 2

a, b = b, a                                     # 2. swap without temp variable
print(a, b)                                     # Expected: 2 1

first, *rest = [1, 2, 3, 4]                     # 3. star collects the rest
print(first, rest)                              # Expected: 1 [2, 3, 4]

head, *mid, tail = "abcde"                      # 4. star in the middle (works on strings)
print(head, mid, tail)                          # Expected: a ['b', 'c', 'd'] e

(x, y), z = (1, 2), 3                           # 5. nested unpacking
print(x, y, z)                                  # Expected: 1 2 3

def add(p: int, q: int, r: int) -> int:         # 6. function taking 3 args
    return p + q + r                            # return the sum
print(add(*[1, 2, 3]))                          # Expected: 6  (* spreads a list into args)
print(add(**{"p": 1, "q": 2, "r": 3}))          # Expected: 6  (** spreads a dict into kwargs)

d = {**{"a": 1, "b": 2}, **{"b": 9, "c": 3}}    # 7. merge dicts (later wins)
print(d)                                        # Expected: {'a': 1, 'b': 9, 'c': 3}

for i, (name, age) in enumerate([("A", 20), ("B", 30)]):  # 8. unpack inside a for loop
    print(i, name, age)                         # Expected: 0 A 20  then  1 B 30

_, keep, *_ = [10, 20, 30, 40]                  # 9. `_` means "ignore this"
print(keep)                                     # Expected: 20

print([*range(3), *"ab"])                       # 10. star inside a literal -> Expected: [0, 1, 2, 'a', 'b']

# ============================================
# TEST CASES
# ============================================
*init, last = (1, 2, 3)                         # star always produces a LIST
print(init, last)                               # Expected: [1, 2] 3
only, *empty = [7]                              # star can capture nothing
print(only, empty)                              # Expected: 7 []
```

---

## 🔍 Why This Works (3 lines max)
Python iterates the right side and matches items to targets by position; one starred target absorbs the leftover items as a list. The number of non-starred targets must fit, otherwise `ValueError`.
हिंदी: Right side को iterate करके position से match होता है — star बचे हुए items को list बना देता है।

---

## ⚡ Alternative Solution
```python
# Python 3.9+: dict merge with | ; unpacking in return and in f(*args, **kwargs)
d1 = {"a": 1, "b": 2}                           # first dict
d2 = {"b": 9, "c": 3}                           # second dict
print(d1 | d2)                                  # Expected: {'a': 1, 'b': 9, 'c': 3}

def min_max(items: list[int]) -> tuple[int, int]:   # returns a tuple
    return min(items), max(items)               # packing into a tuple
lo, hi = min_max([4, 1, 9])                     # unpack the returned tuple
print(lo, hi)                                   # Expected: 1 9
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: wrong number of targets -> ValueError
try:                                            # catch the error to show it
    a, b = [1, 2, 3]                            # 3 values, 2 names
except ValueError as e:                         # raised by unpacking
    print(e)                                    # Expected: too many values to unpack (expected 2, got 3)

# ✅ Correct: use a starred target to absorb extras
a, b, *_ = [1, 2, 3]                            # extras go into _
print(a, b)                                     # Expected: 1 2
```

---

## 🎯 Interview Tip (1 line)
Say: "`a, b = b, a` swaps via tuple packing/unpacking, and `first, *rest = seq` is the Pythonic head/tail split — the star target is always a list."

---

## 🔗 Related Questions
→ Q046 (*args/**kwargs unpacking) | Q072 (deep merge dicts) | Q259 (*args/**kwargs tricks) | Q256 (zip/dict tricks)
