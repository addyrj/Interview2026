---

# Q136. Fix Float Equality Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
A checkout validator rejects a cart whose prices are `[0.1, 0.2]` when the expected total is `0.3`. Find and fix the bug.

```python
# BUGGY CODE:
def total_ok_buggy(prices: list[float], expected: float) -> bool:
    return sum(prices) == expected   # ❌ exact equality on floats
```

---

## 💡 Quick Concept (2 lines only)
Floats are binary approximations — `0.1 + 0.2` is `0.30000000000000004`. Never compare floats with `==`; use `math.isclose()` with a tolerance, or use `Decimal`/integer cents for money.
हिंदी: float में `0.1+0.2 != 0.3` — `math.isclose()` use करो, पैसे के लिए `Decimal`।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import math                                        # isclose lives here

print(0.1 + 0.2 == 0.3)                            # Expected: False
print(0.1 + 0.2)                                   # Expected: 0.30000000000000004

def total_ok_buggy(prices: list[float], expected: float) -> bool:
    return sum(prices) == expected                 # exact comparison -> fragile

print(total_ok_buggy([0.1, 0.2], 0.3))             # Expected: False  (wrong!)

def total_ok(prices: list[float], expected: float) -> bool:
    # Step 1: compare with a tolerance instead of exact equality
    return math.isclose(sum(prices), expected, rel_tol=1e-9, abs_tol=1e-12)

# ============================================
# TEST CASES
# ============================================
print(total_ok([0.1, 0.2], 0.3))                   # Expected: True
print(total_ok([0.1, 0.2], 0.31))                  # Expected: False  (truly different)
print(math.isclose(0, 1e-12))                      # Expected: False (rel_tol alone fails near 0)
print(math.isclose(0, 1e-12, abs_tol=1e-9))        # Expected: True  (abs_tol fixes comparison to 0)
```

---

## 🔍 Why This Works (3 lines max)
`0.1` can't be stored exactly in binary, so tiny rounding errors accumulate. `math.isclose(a, b, rel_tol, abs_tol)` checks the difference against a relative (and optional absolute) tolerance. Comparing with 0 needs `abs_tol`, since relative tolerance of 0 is 0.
हिंदी: tolerance के साथ compare करो; 0 से compare करते समय `abs_tol` जरूर दो।

---

## ⚡ Alternative Solution
```python
from decimal import Decimal              # exact decimal arithmetic (money)
from fractions import Fraction           # exact rational arithmetic

# Decimal built from STRINGS is exact
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))   # Output: True
print(Decimal("0.1") + Decimal("0.2"))                     # Output: 0.3

# ❌ Decimal built from a float copies the float's error
print(Decimal(0.1) + Decimal(0.2) == Decimal("0.3"))       # Output: False

# Fraction is exact too
print(Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10))  # Output: True

# Integer cents — simplest for money
cents = 10 + 20                          # 10 cents + 20 cents
print(cents == 30)                       # Output: True

# Manual epsilon check
print(abs((0.1 + 0.2) - 0.3) < 1e-9)     # Output: True
```

---

## ⚠️ Common Mistake
```python
import math                                  # for isnan

# ❌ Wrong: checking NaN with == (NaN is never equal to anything, even itself)
nan = float("nan")                           # a NaN value
print(nan == nan)                            # Output: False

# ✅ Correct: math.isnan()
print(math.isnan(nan))                       # Output: True
```

---

## 🎯 Interview Tip (1 line)
Say: "Floats are binary approximations, so I use `math.isclose` for comparisons and `Decimal` or integer cents for money — never `==`."

---

## 🔗 Related Questions
→ Q018 (NaN comparison) | Q019 (float precision 0.1 + 0.2) | Q021 (round banker's rounding) | Q135 (integer division bug)
