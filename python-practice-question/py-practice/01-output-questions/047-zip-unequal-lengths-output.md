---

# Q047. zip with Unequal Lengths Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
a = [1, 2, 3]
b = ["x", "y"]

print(list(zip(a, b)))

it = iter(a)
print(list(zip(it, b)))
print(list(it))

it = iter(a)
print(list(zip(b, it)))
print(list(it))

try:
    print(list(zip(a, b, strict=True)))
except ValueError as e:
    print("ValueError:", e)
```

---

## 💡 Quick Concept (2 lines only)
`zip` stops at the shortest iterable, silently dropping the rest. It pulls items from its arguments left to right, so with iterators the order of arguments decides which item gets "lost".
हिंदी: `zip` सबसे छोटे iterable पर रुक जाता है; iterator हो तो बायीं तरफ वाले का एक item खो सकता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from itertools import zip_longest             # pads the shorter input

a = [1, 2, 3]                                 # 3 items
b = ["x", "y"]                                # 2 items

print(list(zip(a, b)))                        # Step 1: stops at 2 pairs, 3 is dropped

it = iter(a)                                  # one-shot iterator over a
print(list(zip(it, b)))                       # Step 2: zip pulls 3 from `it` BEFORE finding b exhausted
print(list(it))                               # 3 was consumed and lost -> empty

it = iter(a)                                  # fresh iterator
print(list(zip(b, it)))                       # Step 3: b is exhausted first, so `it` is not touched again
print(list(it))                               # 3 is still available

try:
    print(list(zip(a, b, strict=True)))       # Step 4: 3.10+ strict=True raises on length mismatch
except ValueError as e:
    print("ValueError:", e)                   # message names the shorter argument

print(list(zip_longest(a, b, fillvalue="-"))) # Step 5: pad instead of truncate

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# [(1, 'x'), (2, 'y')]
# [(1, 'x'), (2, 'y')]
# []
# [('x', 1), ('y', 2)]
# [3]
# ValueError: zip() argument 2 is shorter than argument 1
# [(1, 'x'), (2, 'y'), (3, '-')]
```

---

## 🔍 Why This Works (3 lines max)
Each `zip` step calls `next()` on every input in order and stops at the first `StopIteration`. In `zip(it, b)` the iterator `it` yields 3 first, then `b` is exhausted, so 3 is gone. Put the shorter/known-length iterable first, or use `strict=True`.
हिंदी: `zip` हर step पर क्रम से `next()` बुलाता है — इसलिए `zip(it, b)` में 3 खो जाता है।

---

## ⚡ Alternative Solution
```python
print(list(zip()))                            # no inputs -> Output: []
print(list(zip(a)))                           # one input -> Output: [(1,), (2,), (3,)]
print(dict(zip("abc", range(10))))            # build a dict -> Output: {'a': 0, 'b': 1, 'c': 2}
print(list(zip(*[(1, "a"), (2, "b")])))       # "unzip" with * -> Output: [(1, 2), ('a', 'b')]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: silently losing data when lists should match
names = ["a", "b", "c"]
ages = [1, 2]
pairs = list(zip(names, ages))               # [('a', 1), ('b', 2)] -> "c" vanished, no error

# ✅ Correct: make the mismatch loud
# list(zip(names, ages, strict=True))        # raises ValueError (not run here)
pairs = list(zip(names, ages, strict=False)) # explicit: "I know it truncates"
```

---

## 🎯 Interview Tip (1 line)
Say: "zip truncates to the shortest; use `strict=True` (3.10+) to catch mismatches, `zip_longest` to pad."

---

## 🔗 Related Questions
→ Q048 (enumerate and reversed) | Q061 (zip manually) | Q110 (implement zip) | Q256 (zip/dict tricks)
