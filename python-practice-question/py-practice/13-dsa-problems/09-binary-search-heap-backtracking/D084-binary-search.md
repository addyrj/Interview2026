---

# D084. Binary Search
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐ Easy | LeetCode #704

---

## ❓ Problem
Given a sorted (ascending) list of distinct integers `nums` and an integer `target`, return the index of `target`, or `-1` if it is not present. Must run in O(log n).

```
Input:  nums = [-1, 0, 3, 5, 9, 12], target = 9
Output: 4
```

---

## 💡 Quick Concept (2 lines only)
Keep a search window `[lo, hi]`. Look at the middle: if it equals target, done; if target is bigger, discard the left half; else discard the right half.
हिंदी: हर बार बीच का element देखो और आधा हिस्सा फेंक दो, इसलिए O(log n) लगता है।

---

## ✅ Solution

```python
from bisect import bisect_left  # stdlib binary search for the alternative

# ============================================
# APPROACH 1: Brute force linear scan — O(n) time, O(1) space
# ============================================
def search_linear(nums: list[int], target: int) -> int:
    for i, v in enumerate(nums):     # look at every element
        if v == target:              # found it
            return i                 # return its index
    return -1                        # never found

# ============================================
# APPROACH 2: Iterative binary search — O(log n) time, O(1) space ✅ PREFERRED
# ============================================
def search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1        # inclusive search window
    while lo <= hi:                  # window still has elements
        mid = lo + (hi - lo) // 2    # middle index (overflow-safe habit)
        if nums[mid] == target:      # hit
            return mid               # return index
        if nums[mid] < target:       # target is in the right half
            lo = mid + 1             # drop mid and everything left
        else:                        # target is in the left half
            hi = mid - 1             # drop mid and everything right
    return -1                        # window empty -> not present

# ============================================
# APPROACH 3: Recursive — O(log n) time, O(log n) stack
# ============================================
def search_rec(nums: list[int], target: int, lo: int = 0, hi: int | None = None) -> int:
    if hi is None:                   # first call: default hi to last index
        hi = len(nums) - 1           # set the upper bound
    if lo > hi:                      # empty window
        return -1                    # not found
    mid = (lo + hi) // 2             # middle index
    if nums[mid] == target:          # hit
        return mid                   # done
    if nums[mid] < target:           # go right
        return search_rec(nums, target, mid + 1, hi)  # recurse on right half
    return search_rec(nums, target, lo, mid - 1)      # recurse on left half

# ============================================
# ALTERNATIVE: Pythonic — bisect_left from the standard library
# ============================================
def search_bisect(nums: list[int], target: int) -> int:
    i = bisect_left(nums, target)    # leftmost insertion point for target
    return i if i < len(nums) and nums[i] == target else -1  # confirm it is really there

# ============================================
# TEST CASES
# ============================================
print(search_linear([-1, 0, 3, 5, 9, 12], 9))   # 4
print(search([-1, 0, 3, 5, 9, 12], 9))          # 4
print(search_rec([-1, 0, 3, 5, 9, 12], 9))      # 4
print(search_bisect([-1, 0, 3, 5, 9, 12], 9))   # 4
print(search([-1, 0, 3, 5, 9, 12], 2))          # -1
print(search([5], 5))                           # 0
print(search([], 1))                            # -1
print(search([1, 2], 2))                        # 1
```

---

## 🔍 Why It Works
```
nums = [-1, 0, 3, 5, 9, 12], target = 9
lo=0 hi=5 mid=2 (3)  < 9 -> lo=3
lo=3 hi=5 mid=4 (9) == 9 -> return 4
```
हिंदी: हर step में window आधी होती है, 6 elements में सिर्फ 2-3 steps लगे।

---

## 📊 Complexity
```
Linear:    Time O(n)     | Space O(1)
Iterative: Time O(log n) | Space O(1) ← preferred
Recursive: Time O(log n) | Space O(log n) — call stack
```

---

## ⚡ Variations

```python
# VARIANT 1: First/last occurrence with duplicates — see D086
# VARIANT 2: Search insert position — return lo at the end instead of -1 (LC 35)
# VARIANT 3: Binary search on the answer (e.g. integer sqrt, Koko eating bananas) — search a value range, not an array
```

---

## ⚠️ Common Mistake
```python
# (not run) intentionally broken snippets
# ❌ Wrong: while lo < hi with hi = len(nums) - 1 -> misses the last remaining element
while lo < hi:                   # a one-element window [lo == hi] is never checked
    ...

# ❌ Wrong: lo = mid / hi = mid (no +1 / -1) -> infinite loop when window has 2 elements

# ✅ Correct: inclusive window `lo <= hi` with `mid + 1` / `mid - 1`
```

---

## 🎯 Interview Tip
Say: "I'll use an inclusive window with lo <= hi and always move past mid, so the loop must terminate. In production I'd just use bisect." Mention checking the empty list and one-element cases out loud.

---

## 🔗 Related Problems
→ D085 (Search in Rotated Sorted Array) | D086 (Find First and Last Position) | D087 (Kth Largest Element)
