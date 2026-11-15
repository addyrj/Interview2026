---

# Q018. NaN comparison output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```python
import math

nan = float("nan")
print(nan == nan, nan != nan)                  # (a)
print(nan in [nan])                            # (b)
print([nan] == [float("nan")])                 # (c)
print(max(1, nan), max(nan, 1))                # (d)
print(len({float("nan"), float("nan")}))       # (e)
print(math.isnan(nan))                         # (f)
```

---

## 💡 Quick Concept (2 lines only)
NaN is never equal to anything, including itself (IEEE 754). But containers check identity (`is`) before `==`, so the same NaN object can be "found".
हिंदी: NaN अपने आप के बराबर भी नहीं होता; list/dict पहले identity देखते हैं, इसलिए same object मिल जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import math                                        # For isnan

nan = float("nan")                                 # Step 1: one NaN object
print(nan == nan, nan != nan)                      # (a) False True (IEEE rule)
print(nan in [nan])                                # (b) True: `in` checks identity first
print([nan] == [float("nan")])                     # (c) False: different objects, == is False
print(max(1, nan), max(nan, 1))                    # (d) 1 nan: comparisons with nan are all False
print(len({float("nan"), float("nan")}))           # (e) 2: two distinct NaN objects, never equal
print(math.isnan(nan))                             # (f) True: the correct check

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# False True
# True
# False
# 1 nan
# 2
# True
```

---

## 🔍 Why This Works (3 lines max)
`==` on NaN is always False, `<`/`>` too. `in`, `list ==` and dict lookup use `x is y or x == y`, so only the identical object matches. `max` keeps the first value unless a later one is strictly greater, so the order of arguments changes the answer.
हिंदी: NaN check के लिए हमेशा `math.isnan()` use करें, `==` नहीं।

---

## ⚡ Alternative Solution
```python
import math                                          # isnan / isclose

values = [3.0, float("nan"), 1.0]                    # Data with a NaN
clean = [v for v in values if not math.isnan(v)]     # Filter NaN out
print(sorted(clean))                                 # [1.0, 3.0]

nan = float("nan")                                   # Same object
print({nan: 1}.get(nan), {nan: 1}.get(float("nan"))) # 1 None (identity vs new object)
print(sorted([3, nan, 1, 2]))                        # [3, nan, 1, 2] -> sort silently breaks
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: detecting NaN with ==
x = float("nan")                 # NaN value
print(x == float("nan"))         # False -> check always fails

# ✅ Correct
import math                      # Standard check
print(math.isnan(x))             # True
print(x != x)                    # True (works too, but cryptic)
```

---

## 🎯 Interview Tip (1 line)
Say: "NaN != NaN by IEEE 754; use math.isnan(), and remember sorting or max/min with NaN gives order-dependent garbage."

---

## 🔗 Related Questions
→ Q019 (float precision) | Q003 (is vs ==) | Q012 (dict key collision)
