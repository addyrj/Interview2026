---

# Q135. Fix Integer Division Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
A developer coming from Python 2 / C wrote these helpers. `average(3, 4)` should be `3.5` and 3 of 4 tasks done should be `75.0`%. Both are wrong. Find and fix the bug.

```python
# BUGGY CODE:
def average_buggy(a: int, b: int) -> int:
    return (a + b) // 2          # ❌ floor division drops the fraction

def percent_buggy(done: int, total: int) -> int:
    return done // total * 100   # ❌ 3 // 4 == 0, so the result is always 0 (until done == total)
```

---

## 💡 Quick Concept (2 lines only)
In Python 3, `/` is true division (always `float`) and `//` is floor division (rounds toward negative infinity). Use `/` when you need the fraction; multiply before dividing only with floats or `/`.
हिंदी: `/` दशमलव देता है, `//` नीचे की ओर round करता है (negative में -3.5 -> -4)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def average_buggy(a: int, b: int) -> int:
    return (a + b) // 2                  # floor division

def percent_buggy(done: int, total: int) -> int:
    return done // total * 100           # 3 // 4 -> 0, then * 100 -> 0

print(average_buggy(3, 4))               # Expected: 3     (should be 3.5)
print(percent_buggy(3, 4))               # Expected: 0     (should be 75.0)

def average(a: int, b: int) -> float:
    return (a + b) / 2                   # Step 1: true division -> float

def percent(done: int, total: int) -> float:
    return done / total * 100            # Step 2: divide with / first, then scale

# ============================================
# TEST CASES
# ============================================
print(average(3, 4))                     # Expected: 3.5
print(percent(3, 4))                     # Expected: 75.0
print(f"{percent(1, 3):.1f}")            # Expected: 33.3
print(round(percent(1, 3), 2))           # Expected: 33.33
print(type(4 / 2), type(4 // 2))         # Expected: <class 'float'> <class 'int'>
try:
    percent(1, 0)                        # division by zero
except ZeroDivisionError as e:           # catch it
    print("ZeroDivisionError:", e)       # Expected: ZeroDivisionError: division by zero
```

---

## 🔍 Why This Works (3 lines max)
`/` always returns a `float`; `//` returns the floor of the quotient (an `int` for int operands). Floor division of negatives rounds DOWN: `-7 // 2 == -4`, not `-3`. Python 2's `/` was integer division for ints — that habit causes this bug.
हिंदी: Python 3 में `/` हमेशा float है; `//` floor करता है, truncate नहीं।

---

## ⚡ Alternative Solution
```python
import math                                   # for trunc / ceil
from fractions import Fraction                # exact rational numbers

print(-7 // 2, int(-7 / 2), -7 % 2)           # Output: -4 -3 1   (floor vs truncate)
print(math.trunc(-7 / 2))                     # Output: -3        (truncate toward zero)
print(divmod(7, 2), divmod(-7, 2))            # Output: (3, 1) (-4, 1)  (quotient and remainder)
print(7 // 2.0, 7 / 2)                        # Output: 3.0 3.5   (// with a float returns a float)
print(Fraction(3, 4) * 100)                   # Output: 75        (exact, no float error)

# Ceiling division without floats
print(-(-9 // 2), math.ceil(9 / 2))           # Output: 5 5       (pages needed for 9 items, 2 per page)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using int(a / b) to "floor" negative numbers
print(int(-7 / 2))        # Output: -3   (truncates toward zero)

# ✅ Correct: use // for floor, math.trunc() for truncation — pick on purpose
print(-7 // 2)            # Output: -4   (floor)
```

---

## 🎯 Interview Tip (1 line)
Say: "In Python 3 `/` is true division and `//` floors toward negative infinity — for money or exact ratios I use `Decimal` or `Fraction`."

---

## 🔗 Related Questions
→ Q019 (float precision) | Q020 (integer division and modulo with negatives) | Q021 (round banker's rounding) | Q136 (float equality bug) | Q309 (Python 2 vs 3)
