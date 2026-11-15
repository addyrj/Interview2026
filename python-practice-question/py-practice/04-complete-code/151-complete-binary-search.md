---

# Q151. Complete Binary Search
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so `binary_search(nums, target)` returns the index of `target` in a sorted list, or `-1`.

```python
def binary_search(nums: list[int], target: int) -> int:
    lo, hi = 0, ____                               # BLANK 1: last valid index
    while lo ____ hi:                              # BLANK 2: loop condition
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = ____                              # BLANK 3: discard the left half
        else:
            hi = ____                              # BLANK 4: discard the right half
    return -1
```

---

## 💡 Quick Concept (2 lines only)
Look at the middle of a sorted range and throw away the half that cannot contain the target — O(log n) instead of O(n).
हिंदी: Sorted list के बीच का element देखो और जिस आधे में target नहीं हो सकता उसे हटा दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def binary_search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1                      # BLANK 1: inclusive range [lo, hi]
    while lo <= hi:                                # BLANK 2: <= so a 1-element range is checked
        mid = (lo + hi) // 2                       # Step 1: middle index (no overflow in Python)
        if nums[mid] == target:                    # Step 2: found
            return mid                             # return its index
        if nums[mid] < target:                     # target is on the right
            lo = mid + 1                           # BLANK 3: skip mid and everything left
        else:                                      # target is on the left
            hi = mid - 1                           # BLANK 4: skip mid and everything right
    return -1                                      # Step 3: range empty -> not present


# ============================================
# TEST CASES
# ============================================
nums = [1, 3, 5, 7, 9, 11]                         # must be sorted
print(binary_search(nums, 7))                      # Expected: 3
print(binary_search(nums, 1))                      # Expected: 0
print(binary_search(nums, 11))                     # Expected: 5
print(binary_search(nums, 4))                      # Expected: -1
print(binary_search([], 1))                        # Expected: -1
print(binary_search([5], 5))                       # Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
The search range `[lo, hi]` always contains the target if it exists. Each step halves it (`mid +/- 1` guarantees progress), so at most ~log2(n) iterations. `<=` ensures the last single element is tested.
हिंदी: हर step में range आधी होती है; `mid ± 1` से progress पक्का होता है और `<=` आख़िरी element भी जाँचता है।

---

## ⚡ Alternative Solution
```python
# Standard library: bisect (returns the insertion point, so verify the hit)
from bisect import bisect_left


def binary_search(nums: list[int], target: int) -> int:
    i = bisect_left(nums, target)                  # leftmost position where target could go
    return i if i < len(nums) and nums[i] == target else -1  # check it is really there

print(binary_search([1, 3, 5, 7, 9, 11], 9))       # Expected: 4
print(binary_search([1, 3, 5, 7, 9, 11], 4))       # Expected: -1
print(bisect_left([1, 2, 2, 2, 3], 2))             # Expected: 1  (first of the duplicates)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: while lo < hi with hi = len(nums) - 1  -> skips the last candidate (e.g. [5], target 5 -> -1)
# ❌ Wrong: lo = mid / hi = mid (no +1/-1) -> infinite loop when lo + 1 == hi
# ❌ Wrong: running it on an unsorted list -> silently wrong answers
# ✅ Correct: inclusive range, lo <= hi, mid + 1 / mid - 1
```

---

## 🎯 Interview Tip (1 line)
Say: "State the invariant (target in [lo, hi]), explain why the loop terminates, and mention `bisect` for the library version."

---

## 🔗 Related Questions
→ Q103 (implement binary search) | Q137 (off-by-one) | D084 (binary search DSA) | D086 (first and last position)
