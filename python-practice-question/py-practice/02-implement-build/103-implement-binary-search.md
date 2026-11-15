---

# Q103. Implement Binary Search
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `binary_search(arr, target)` for a **sorted** list. Return the index of `target`, or `-1` if absent. Time must be O(log n).

```python
binary_search([1, 3, 5, 7, 9, 11], 7)   # 3
binary_search([1, 3, 5, 7, 9, 11], 4)   # -1
```

---

## 💡 Quick Concept (2 lines only)
Compare with the middle element and discard half the range each step. Needs sorted input; runs in O(log n).
हिंदी: हर बार बीच का element देखो और आधा हिस्सा फेंक दो — sorted list चाहिए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def binary_search(arr: list[int], target: int) -> int:  # iterative version
    lo, hi = 0, len(arr) - 1  # Step 1: inclusive search bounds
    while lo <= hi:  # Step 2: loop while range is non-empty (<= matters!)
        mid = lo + (hi - lo) // 2  # middle index (overflow-safe habit)
        if arr[mid] == target:  # found it
            return mid  # return the index
        if arr[mid] < target:  # target is in the right half
            lo = mid + 1  # drop left half including mid
        else:  # target is in the left half
            hi = mid - 1  # drop right half including mid
    return -1  # Step 3: range empty -> not found

# ============================================
# TEST CASES
# ============================================
print(binary_search([1, 3, 5, 7, 9, 11], 7))  # Expected: 3
print(binary_search([1, 3, 5, 7, 9, 11], 1))  # Expected: 0
print(binary_search([1, 3, 5, 7, 9, 11], 11))  # Expected: 5
print(binary_search([1, 3, 5, 7, 9, 11], 4))  # Expected: -1
print(binary_search([], 4))  # Expected: -1
print(binary_search([5], 5))  # Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Each iteration halves `[lo, hi]`, so at most log2(n) steps. `mid +/- 1` guarantees progress because `mid` was already checked.
हिंदी: हर step में range आधी होती है, और mid +/- 1 से loop कभी अटकता नहीं।

---

## ⚡ Alternative Solution
```python
# Pythonic: use the bisect module (leftmost insertion point)
from bisect import bisect_left  # standard-library binary search

def bs_bisect(arr: list[int], target: int) -> int:
    i = bisect_left(arr, target)  # index where target would be inserted
    return i if i < len(arr) and arr[i] == target else -1  # verify it is really there

print(bs_bisect([1, 3, 5, 7, 9, 11], 7))  # Expected: 3
print(bs_bisect([1, 3, 5], 4))  # Expected: -1

# Recursive version
def rec(arr, t, lo=0, hi=None):
    hi = len(arr) - 1 if hi is None else hi  # default upper bound
    if lo > hi: return -1  # empty range
    mid = (lo + hi) // 2  # middle
    if arr[mid] == t: return mid  # found
    return rec(arr, t, mid + 1, hi) if arr[mid] < t else rec(arr, t, lo, mid - 1)  # recurse
print(rec([1, 3, 5, 7], 5))  # Expected: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `while lo < hi` skips the last remaining candidate
def bad(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:  # ❌ should be <=
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        if arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
print(bad([5], 5))  # Output: -1  (WRONG, 5 is there)
print(bad([1, 3], 3))  # Output: -1  (WRONG)

# ✅ Correct: while lo <= hi
```

---

## 🎯 Interview Tip (1 line)
Say: "Sorted input required, O(log n) time O(1) space; I'm careful with `lo <= hi` and `mid +/- 1`, and in real code I'd use bisect."

---

## 🔗 Related Questions
→ Q113 (sorted with key) | Q151 (complete binary search) | Q104 (bubble sort) | Q106 (merge sort)
