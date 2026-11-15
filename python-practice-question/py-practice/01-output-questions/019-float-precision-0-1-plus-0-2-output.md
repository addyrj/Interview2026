---

# Q019. Float precision (0.1 + 0.2) output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
print(0.1 + 0.2)               # (a)
print(0.1 + 0.2 == 0.3)        # (b)
print(sum([0.1] * 10) == 1.0)  # (c)
print(1.1 + 2.2)               # (d)
print(round(2.675, 2))         # (e)
```

---

## 💡 Quick Concept (2 lines only)
Floats are binary (IEEE 754 double); 0.1 and 0.2 cannot be stored exactly, so tiny errors appear. Compare with `math.isclose`, or use `Decimal` for money.
हिंदी: Float binary में है, इसलिए 0.1 सटीक store नहीं होता — `==` से compare मत करें।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
print(0.1 + 0.2)               # (a) 0.30000000000000004 (representation error)
print(0.1 + 0.2 == 0.3)        # (b) False
print(sum([0.1] * 10) == 1.0)  # (c) True here (errors happened to cancel; do not rely on it)
print(1.1 + 2.2)               # (d) 3.3000000000000003
print(round(2.675, 2))         # (e) 2.67 (2.675 is stored as 2.67499999...)

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# 0.30000000000000004
# False
# True
# 3.3000000000000003
# 2.67
```

---

## 🔍 Why This Works (3 lines max)
`0.1 = 0x1.999999999999ap-4` is rounded to the nearest double, so the sum lands one bit above 0.3's double. Correct printing shows the shortest string that round-trips, exposing the error.
हिंदी: Error Python का bug नहीं, हर language के float में यही होता है।

---

## ⚡ Alternative Solution
```python
import math                                         # isclose, fsum
from decimal import Decimal                         # Exact decimal arithmetic
from fractions import Fraction                      # Exact rational arithmetic

print(math.isclose(0.1 + 0.2, 0.3))                 # True (relative tolerance 1e-09)
print(abs((0.1 + 0.2) - 0.3) < 1e-9)                # True (manual epsilon)
print(Decimal("0.1") + Decimal("0.2"))              # 0.3 (build from STRINGS)
print(Decimal(0.1))                                 # 0.1000000000000000055511151231257827021181583404541015625
print(Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10))  # True
print(f"{0.1 + 0.2:.2f}")                           # 0.30 (format only for display)
print(math.fsum([0.1] * 10))                        # 1.0 (accurate summation)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: money with floats and ==
total = 0.1 + 0.2                  # Float math
print(total == 0.3)                # False

# ❌ Wrong: Decimal from a float keeps the error
from decimal import Decimal        # Import
print(Decimal(0.1) == Decimal("0.1"))   # False

# ✅ Correct: Decimal from str, or integer cents
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))   # True
```

---

## 🎯 Interview Tip (1 line)
Say: "Floats are binary approximations; use `math.isclose` for comparisons and `Decimal('0.1')` (from strings) or integer cents for money."

---

## 🔗 Related Questions
→ Q018 (NaN comparison) | Q021 (banker's rounding) | Q020 (integer division)
