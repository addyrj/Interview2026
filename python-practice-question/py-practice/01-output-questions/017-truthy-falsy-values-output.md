---

# Q017. Truthy/falsy values output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
print([bool(v) for v in [0, 0.0, "", [], {}, set(), (), None, False, 0j]])   # (a)
print([bool(v) for v in ["0", " ", [0], [[]], "False", -1, float("nan")]])    # (b)

class E:
    def __len__(self): return 0                     # only __len__

class B:
    def __bool__(self): return False                # __bool__ AND __len__
    def __len__(self): return 5

print(bool(E()), bool(B()), bool(range(0)), bool(range(1)))                  # (c)
```

---

## 💡 Quick Concept (2 lines only)
Falsy = None, False, zero of any numeric type, and empty containers/strings/ranges; everything else is truthy. Python checks `__bool__` first, then `__len__`.
हिंदी: खाली या zero = falsy; बाकी सब truthy — `"0"` और `[0]` भी truthy हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
falsy = [0, 0.0, "", [], {}, set(), (), None, False, 0j]          # Step 1: all the falsy kinds
print([bool(v) for v in falsy])                                    # (a) ten False values

tricky = ["0", " ", [0], [[]], "False", -1, float("nan")]         # Step 2: look falsy, but are not
print([bool(v) for v in tricky])                                   # (b) seven True values

class E:                                                           # Step 3: only __len__ defined
    def __len__(self) -> int:                                      # len 0 -> falsy
        return 0                                                   # Empty

class B:                                                           # Step 4: __bool__ wins over __len__
    def __bool__(self) -> bool:                                    # Checked first
        return False                                               # Falsy even though len is 5
    def __len__(self) -> int:                                      # Ignored for truthiness
        return 5                                                   # Non-empty

print(bool(E()), bool(B()), bool(range(0)), bool(range(1)))       # (c)

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# [False, False, False, False, False, False, False, False, False, False]
# [True, True, True, True, True, True, True]
# False False False True
```

---

## 🔍 Why This Works (3 lines max)
`bool(x)` calls `x.__bool__()` if present, otherwise `len(x) != 0`, otherwise True. Non-empty strings (even `"0"`), lists containing falsy items, and NaN are all truthy.
हिंदी: Truthiness container के अंदर की value से नहीं, उसके खाली होने से तय होती है।

---

## ⚡ Alternative Solution
```python
from decimal import Decimal                  # Decimal also follows the zero rule

print(bool(Decimal("0.0")))                  # False (zero)
print(bool(Decimal("0.1")))                  # True

# Idiomatic emptiness check: rely on truthiness, don't use len()
items: list[int] = []                        # Empty list
if not items:                                # Pythonic (instead of len(items) == 0)
    print("empty")                           # empty
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `if value:` when 0 / "" / [] are legal values
def set_timeout(seconds: int | None = None) -> int:
    if not seconds:               # 0 is treated as "missing"!
        return 30                 # Wrong default applied to 0
    return seconds                # Never returns 0

print(set_timeout(0))             # 30  <- bug, user asked for 0

# ✅ Correct: compare with None explicitly
def set_timeout_ok(seconds: int | None = None) -> int:
    return 30 if seconds is None else seconds   # Only None means "missing"
print(set_timeout_ok(0))          # 0
```

---

## 🎯 Interview Tip (1 line)
Say: "Falsy = None/False/zero/empty; `__bool__` then `__len__` decide for custom classes; use `is None` when 0 or '' are valid."

---

## 🔗 Related Questions
→ Q016 (short-circuit and/or) | Q049 (any/all empty) | Q014 (bool is int)
