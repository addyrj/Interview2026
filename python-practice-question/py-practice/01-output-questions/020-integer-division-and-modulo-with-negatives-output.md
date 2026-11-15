---

# Q020. Integer division and modulo with negatives output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
print(7 // 2, -7 // 2, 7 // -2, -7 // -2)    # (a)
print(7 % 3, -7 % 3, 7 % -3, -7 % -3)        # (b)
print(divmod(-7, 2), int(-7 / 2))            # (c)
print(-7.5 // 2, -7.5 % 2)                   # (d)
```

---

## 💡 Quick Concept (2 lines only)
`//` FLOORS toward negative infinity (not toward zero), and `%` always takes the sign of the divisor, so that `a == (a // b) * b + a % b`.
हिंदी: `//` हमेशा नीचे (−∞ की तरफ) round करता है, और `%` का sign divisor जैसा होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
print(7 // 2, -7 // 2, 7 // -2, -7 // -2)   # (a) 3 -4 -4 3  (-3.5 floors to -4)
print(7 % 3, -7 % 3, 7 % -3, -7 % -3)       # (b) 1 2 -2 -1  (sign follows the divisor)
print(divmod(-7, 2), int(-7 / 2))           # (c) (-4, 1) -3  (int() truncates toward zero)
print(-7.5 // 2, -7.5 % 2)                  # (d) -4.0 0.5   (floats follow the same rule)

# Identity check for every case: a == (a // b) * b + a % b
a, b = -7, 3                                # Sample numbers
print((a // b) * b + a % b == a)            # True

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# 3 -4 -4 3
# 1 2 -2 -1
# (-4, 1) -3
# -4.0 0.5
# True
```

---

## 🔍 Why This Works (3 lines max)
Python defines `//` as floor division and `%` as the remainder that keeps `a == (a // b) * b + a % b`. So `-7 // 2 = -4` and `-7 % 2 = 1`. C/Java truncate toward zero, which gives `-3` and `-1`.
हिंदी: C/Java में `-7 % 3 = -1` होता है, Python में `2` — यही अंतर interview में पूछा जाता है।

---

## ⚡ Alternative Solution
```python
import math                                   # floor, trunc, fmod

print(math.floor(-3.5), math.trunc(-3.5), int(-3.5))   # -4 -3 -3
print(math.fmod(-7, 3))                       # -1.0 (C-style remainder, sign of dividend)
print(-1 % 5, 1 % -5, 0 % -5)                 # 4 -4 0

try:
    5 // 0                                    # Division by zero
except ZeroDivisionError as e:                # Catch it
    print(e)                                  # integer division or modulo by zero
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using int(a / b) as "integer division" for negatives
print(int(-7 / 2))        # -3  <- truncates, differs from //

# ✅ Correct: use // for floor semantics (also safe from float error on big ints)
print(-7 // 2)            # -4

# Handy use: circular index wraps correctly even when negative
print((-1) % 5)           # 4  (previous element in a ring of 5)
```

---

## 🎯 Interview Tip (1 line)
Say: "Python floors: `//` rounds toward −∞ and `%` follows the divisor's sign; use `math.fmod`/`int(a/b)` for C-style truncation."

---

## 🔗 Related Questions
→ Q021 (banker's rounding) | Q019 (float precision) | Q014 (bool is int)
