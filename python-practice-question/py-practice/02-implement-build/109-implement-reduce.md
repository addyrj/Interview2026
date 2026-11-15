---

# Q109. Implement reduce()
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `my_reduce(fn, iterable, initial=<missing>)` like `functools.reduce`. With no initial value, the first item seeds the accumulator; an empty iterable with no initial raises `TypeError`. An initial value of `0`/`None` must still be respected.

```python
my_reduce(lambda a, b: a + b, [1, 2, 3, 4])      # 10
my_reduce(lambda a, b: a + b, [1, 2, 3, 4], 10)  # 20
```

---

## 💡 Quick Concept (2 lines only)
`reduce` folds a sequence into one value: `acc = fn(acc, item)` for every item. Use a private sentinel to tell "no initial" apart from `initial=None` or `0`.
हिंदी: reduce पूरी list को एक value में बदलता है — "initial नहीं दिया" पहचानने के लिए sentinel object चाहिए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
_MISSING = object()  # Step 1: unique sentinel (cannot clash with any real value)

def my_reduce(fn, iterable, initial=_MISSING):  # fold iterable into one value
    it = iter(iterable)  # Step 2: iterator so we can pull the first item manually
    if initial is _MISSING:  # no initial value supplied
        try:
            acc = next(it)  # first item becomes the accumulator
        except StopIteration:  # empty iterable and no initial
            raise TypeError("reduce() of empty iterable with no initial value") from None  # same error as stdlib
    else:
        acc = initial  # use the given initial (even if it is 0 or None)
    for item in it:  # Step 3: fold the remaining items
        acc = fn(acc, item)  # combine accumulator with next item
    return acc  # final folded value

# ============================================
# TEST CASES
# ============================================
print(my_reduce(lambda a, b: a + b, [1, 2, 3, 4]))  # Expected: 10
print(my_reduce(lambda a, b: a + b, [1, 2, 3, 4], 10))  # Expected: 20
print(my_reduce(lambda a, b: a * b, range(1, 6)))  # Expected: 120
print(my_reduce(max, [3, 9, 2]))  # Expected: 9
print(my_reduce(lambda a, b: a + b, [], 0))  # Expected: 0
print(my_reduce(lambda a, b: a + b, [7]))  # Expected: 7  (single item, fn never called)
try:  # empty and no initial
    my_reduce(lambda a, b: a + b, [])  # should raise
except TypeError as e:
    print(e)  # Expected: reduce() of empty iterable with no initial value
print(my_reduce(lambda acc, w: {**acc, w: acc.get(w, 0) + 1}, "abca", {}))  # Expected: {'a': 2, 'b': 1, 'c': 1}
```

---

## 🔍 Why This Works (3 lines max)
The accumulator starts from the initial value or the first item, then each item is folded in. `is _MISSING` (not truthiness) correctly accepts `0`, `None` and `[]` as real initial values.
हिंदी: sentinel से पता चलता है कि user ने initial दिया या नहीं — 0 और None भी valid initial हैं।

---

## ⚡ Alternative Solution
```python
# Standard library
from functools import reduce  # reduce lives in functools in Python 3

print(reduce(lambda a, b: a + b, [1, 2, 3, 4], 10))  # Expected: 20
# For sums/products prefer sum(), math.prod(), any(), all() — clearer than reduce
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `if initial` treats 0 / "" / [] as "not provided"
def bad(fn, it, initial=None):
    it = iter(it)
    acc = initial if initial else next(it)  # ❌ initial=0 is ignored
    for x in it: acc = fn(acc, x)
    return acc
print(bad(lambda a, b: a - b, [1, 2, 3], 0))  # Output: -4  (WRONG: 1-2-3)

# ✅ Correct: sentinel check
print(my_reduce(lambda a, b: a - b, [1, 2, 3], 0))  # Output: -6  (0-1-2-3)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use a sentinel object instead of None/falsy checks for the optional initial value, and I'd normally prefer sum/prod/comprehensions over reduce."

---

## 🔗 Related Questions
→ Q107 (map) | Q108 (filter) | Q085 (compose) | Q209 (async reduce) | Q251 (functools)
