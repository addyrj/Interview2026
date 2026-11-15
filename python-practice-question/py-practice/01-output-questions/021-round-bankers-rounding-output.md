---

# Q021. round() banker's rounding output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
print(round(0.5), round(1.5), round(2.5), round(3.5))   # (a)
print(round(-0.5), round(-2.5))                         # (b)
print(round(2.675, 2), round(0.125, 2))                 # (c)
print(round(1250, -2), round(1350, -2))                 # (d)
print(type(round(2.5)), type(round(2.5, 0)))            # (e)
```

---

## 💡 Quick Concept (2 lines only)
`round()` uses banker's rounding: exact halves go to the nearest EVEN number. Decimal fractions like 2.675 are also affected by float error.
हिंदी: ठीक .5 पर Python सबसे पास की even संख्या चुनता है — 2.5 → 2, 3.5 → 4।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
print(round(0.5), round(1.5), round(2.5), round(3.5))   # (a) 0 2 2 4 (ties go to even)
print(round(-0.5), round(-2.5))                         # (b) 0 -2 (also even; -0.5 gives 0)
print(round(2.675, 2), round(0.125, 2))                 # (c) 2.67 0.12
                                                        #     2.675 is really 2.67499..., 0.125 is an exact tie -> even
print(round(1250, -2), round(1350, -2))                 # (d) 1200 1400 (ties to even hundred)
print(type(round(2.5)), type(round(2.5, 0)))            # (e) int float (ndigits given -> same type)

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# 0 2 2 4
# 0 -2
# 2.67 0.12
# 1200 1400
# <class 'int'> <class 'float'>
```

---

## 🔍 Why This Works (3 lines max)
Python 3 follows IEEE round-half-to-even to avoid statistical bias when rounding many values. `round(x)` returns an int, while `round(x, n)` keeps x's type. Floats such as 2.675 are not exact ties, so the stored value decides.
हिंदी: Python 2 में 2.5 → 3 था; Python 3 में 2 — यह बदलाव मशहूर interview सवाल है।

---

## ⚡ Alternative Solution
```python
from decimal import Decimal, ROUND_HALF_UP        # Exact decimals, chosen rounding mode
import math                                       # floor

print(Decimal("2.5").quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # 3 (school rounding)
print(Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))  # 2.68
print(math.floor(2.5 + 0.5), int(2.5 + 0.5))      # 3 3 (works for positives only)
print(f"{0.5:.0f}", f"{1.5:.0f}", f"{2.5:.0f}")   # 0 2 2 (format() also rounds half-even)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting school rounding (half up) from round()
print(round(2.5))                 # 2  (not 3)

# ✅ Correct: when you need half-up (e.g. invoices), use Decimal explicitly
from decimal import Decimal, ROUND_HALF_UP     # Import
print(Decimal("2.5").quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # 3
```

---

## 🎯 Interview Tip (1 line)
Say: "round() is half-to-even and float-representation dependent; use Decimal with ROUND_HALF_UP when business rules need school rounding."

---

## 🔗 Related Questions
→ Q019 (float precision) | Q020 (integer division) | Q014 (bool is int)
