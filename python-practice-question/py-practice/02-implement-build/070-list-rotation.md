---

# Q070. List Rotation
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `rotate(items, k)` that rotates a list right by `k` steps (negative `k` rotates left). `k` can exceed the length.

```python
rotate([1, 2, 3, 4, 5], 2)   # [4, 5, 1, 2, 3]
rotate([1, 2, 3, 4, 5], -1)  # [2, 3, 4, 5, 1]
```

---

## 💡 Quick Concept (2 lines only)
Reduce `k` with `k %= len(items)` (Python's `%` is always non-negative for a positive divisor), then result = `items[-k:] + items[:-k]`.
हिंदी: पहले `k %= len` करो, फिर आखिरी k items को आगे लगा दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def rotate(items: list, k: int) -> list:
    if not items:                                   # Step 1: empty list -> nothing to rotate (avoid % 0)
        return []                                   # return an empty list
    k %= len(items)                                 # Step 2: normalise k (7 -> 1 for len 3; -1 -> len-1)
    return items[-k:] + items[:-k] if k else items[:]  # Step 3: tail + head; k == 0 needs a special case

# ============================================
# TEST CASES
# ============================================

print(rotate([1, 2, 3, 4, 5], 2))    # Expected: [4, 5, 1, 2, 3]
print(rotate([1, 2, 3, 4, 5], -1))   # Expected: [2, 3, 4, 5, 1]
print(rotate([1, 2, 3], 0))          # Expected: [1, 2, 3]
print(rotate([1, 2, 3], 7))          # Expected: [3, 1, 2]   (7 % 3 == 1)
print(rotate([], 3))                 # Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Rotating right by k moves the last k items to the front. Modulo makes huge or negative `k` equivalent to a value in `[0, len)`. The `k == 0` branch is needed because `items[-0:]` is the WHOLE list.
हिंदी: Rotate right का मतलब आखिरी k items आगे आते हैं; `k == 0` अलग से संभालना ज़रूरी है।

---

## ⚡ Alternative Solution
```python
from collections import deque            # deque has a built-in O(k) rotate

d = deque([1, 2, 3, 4, 5])               # sample data
d.rotate(2)                              # positive = right rotation (in place)
print(list(d))                           # Expected: [4, 5, 1, 2, 3]
d = deque([1, 2, 3, 4, 5])               # fresh deque
d.rotate(-1)                             # negative = left rotation
print(list(d))                           # Expected: [2, 3, 4, 5, 1]

def rev(a, i, j):                        # reverse a[i..j] in place
    while i < j:                         # until pointers meet
        a[i], a[j] = a[j], a[i]          # swap ends
        i += 1; j -= 1                   # move inwards

def rotate_inplace(a, k):                # O(n) time, O(1) extra space (three reversals)
    n = len(a)                           # length
    if not n:                            # empty guard
        return
    k %= n                               # normalise k
    rev(a, 0, n - 1); rev(a, 0, k - 1); rev(a, k, n - 1)  # reverse all, then each part

a = [1, 2, 3, 4, 5]; rotate_inplace(a, 2); print(a)       # Expected: [4, 5, 1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no modulo and no empty-list guard
def bad(a, k):
    return a[-k:] + a[:-k]
print(bad([1, 2, 3], 7))    # [1, 2, 3] <- k=7 slices past the ends, so nothing rotates (verified: [1, 2, 3])
# bad([], 3) is fine, but `k %= len(a)` on an empty list would raise ZeroDivisionError

# ❌ Wrong: k == 0 -> a[-0:] is the WHOLE list and a[:-0] is EMPTY; here it only works by luck
print([1, 2, 3][-0:] + [1, 2, 3][:-0])   # [1, 2, 3] (verified) - fragile, so special-case k == 0

# ✅ Correct: guard empty list, k %= len(a), special-case k == 0
```

---

## 🎯 Interview Tip (1 line)
Mention modulo normalisation, `deque.rotate`, and the three-reversal in-place trick (O(1) space).

---

## 🔗 Related Questions
→ Q060 (chunk) | Q101 (implement queue) | Q103 (binary search) | Q023 (slicing out of range output)
