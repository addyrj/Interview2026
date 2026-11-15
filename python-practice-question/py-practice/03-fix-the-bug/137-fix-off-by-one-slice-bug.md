---

# Q137. Fix Off-by-One Slice Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
`last_n([1, 2, 3, 4, 5], 2)` should return `[4, 5]` but returns three items. Find and fix the bug.

```python
# BUGGY CODE:
def last_n_buggy(items: list[int], n: int) -> list[int]:
    return items[len(items) - n - 1:]   # ❌ start index is one too early
```

---

## 💡 Quick Concept (2 lines only)
Slices are half-open: `a[start:stop]` includes `start` and EXCLUDES `stop`. For the last n items, start at `len - n` (or use `-n`). Beware: `a[-0:]` is the whole list.
हिंदी: slice में start शामिल, stop शामिल नहीं; last n के लिए `items[-n:]` (n=0 पर सावधान)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def last_n_buggy(items: list[int], n: int) -> list[int]:
    return items[len(items) - n - 1:]        # starts at index len-n-1 -> one extra item

def last_n(items: list[int], n: int) -> list[int]:
    return items[-n:] if n > 0 else []       # Step 1: negative start counts from the end; guard n == 0

data = [1, 2, 3, 4, 5]                       # sample data

# ============================================
# TEST CASES
# ============================================
print(last_n_buggy(data, 2))                 # Expected: [3, 4, 5]  (wrong, has 3 items)
print(last_n(data, 2))                       # Expected: [4, 5]
print(last_n(data, 0))                       # Expected: []
print(last_n(data, 10))                      # Expected: [1, 2, 3, 4, 5]  (n larger than list is fine)
print(last_n([], 3))                         # Expected: []
print(data[0:3], data[:3], data[3:])         # Expected: [1, 2, 3] [1, 2, 3] [4, 5]
print(data[1:-1])                            # Expected: [2, 3, 4]
```

---

## 🔍 Why This Works (3 lines max)
`items[-2:]` starts 2 from the end and runs to the end, so it yields exactly 2 items. Slices never raise `IndexError` — out-of-range bounds are clamped. `-0` equals `0`, so `items[-0:]` returns everything; that is why `n == 0` needs a guard.
हिंदी: slice कभी IndexError नहीं देता; `-0` का मतलब `0` है, इसलिए n=0 अलग से handle करो।

---

## ⚡ Alternative Solution
```python
data = [1, 2, 3, 4, 5]                           # sample data

# Alternative 1: explicit start with max() to stay safe for large n
def last_n2(items: list[int], n: int) -> list[int]:
    return items[max(len(items) - n, 0):]        # len - n, never below 0

print(last_n2(data, 2), last_n2(data, 0), last_n2(data, 10))   # Output: [4, 5] [] [1, 2, 3, 4, 5]

# Alternative 2: collections.deque keeps only the last n items of a stream
from collections import deque                    # bounded queue
print(list(deque(data, maxlen=2)))               # Output: [4, 5]

# Other slice forms
print(data[::-1], data[::2])                     # Output: [5, 4, 3, 2, 1] [1, 3, 5]
print("hello"[1:-1])                             # Output: ell
```

---

## ⚠️ Common Mistake
```python
data = [1, 2, 3, 4, 5]          # sample data

# ❌ Wrong: thinking the end index is inclusive
print(data[1:3])                # Output: [2, 3]   (index 3 is NOT included)

# ❌ Wrong: items[-n:] with n = 0 returns EVERYTHING
print(data[-0:])                # Output: [1, 2, 3, 4, 5]

# ✅ Correct: remember [start, stop) and guard the n == 0 case
print(data[1:3 + 1])            # Output: [2, 3, 4]  (to include index 3, use stop = 4)
```

---

## 🎯 Interview Tip (1 line)
Say: "Slices are half-open `[start, stop)` and clamp out-of-range bounds; `items[-n:]` gets the last n, but `n == 0` needs a guard because `-0 == 0`."

---

## 🔗 Related Questions
→ Q022 (string multiplication and slicing) | Q023 (slicing out of range) | Q060 (chunk list into groups) | Q070 (list rotation)
