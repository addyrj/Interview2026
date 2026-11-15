---

# D086. Find First and Last Position
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #34

---

## ❓ Problem
Given a sorted list `nums` (may contain duplicates) and a `target`, return `[first_index, last_index]` of the target, or `[-1, -1]` if absent. Must run in O(log n).

```
Input:  nums = [5, 7, 7, 8, 8, 10], target = 8
Output: [3, 4]
```

---

## 💡 Quick Concept (2 lines only)
Run binary search twice: once for the leftmost index where `nums[i] >= target`, once for the leftmost index where `nums[i] > target` (minus 1 gives the last position).
हिंदी: दो बार binary search चलाओ, एक बार left boundary के लिए और एक बार right boundary के लिए।

---

## ✅ Solution

```python
from bisect import bisect_left, bisect_right  # stdlib boundary searches

# ============================================
# APPROACH 1: Brute force linear scan — O(n) time, O(1) space
# ============================================
def search_range_brute(nums: list[int], target: int) -> list[int]:
    first = last = -1                    # default when not found
    for i, v in enumerate(nums):         # scan every element
        if v == target:                  # match
            if first == -1:              # first time we see it
                first = i                # remember the first index
            last = i                     # keep updating the last index
    return [first, last]                 # result pair

# ============================================
# APPROACH 2: Two boundary binary searches — O(log n) time, O(1) space ✅ PREFERRED
# ============================================
def search_range(nums: list[int], target: int) -> list[int]:
    def lower_bound(x: int) -> int:      # first index with nums[i] >= x
        lo, hi = 0, len(nums)            # half-open window [lo, hi)
        while lo < hi:                   # until window collapses
            mid = (lo + hi) // 2         # middle index
            if nums[mid] < x:            # mid is too small
                lo = mid + 1             # answer is to the right
            else:                        # mid could be the answer
                hi = mid                 # keep mid in window
        return lo                        # insertion point

    left = lower_bound(target)           # first position of target (or where it would go)
    if left == len(nums) or nums[left] != target:  # target not present
        return [-1, -1]                  # not found
    right = lower_bound(target + 1) - 1  # first index > target, minus one (ints only)
    return [left, right]                 # both boundaries

# ============================================
# ALTERNATIVE: Pythonic — bisect_left and bisect_right
# ============================================
def search_range_bisect(nums: list[int], target: int) -> list[int]:
    lo = bisect_left(nums, target)       # first index of target
    hi = bisect_right(nums, target)      # one past the last index of target
    return [lo, hi - 1] if lo < hi else [-1, -1]  # empty slice means absent

# ============================================
# TEST CASES
# ============================================
print(search_range_brute([5, 7, 7, 8, 8, 10], 8))   # [3, 4]
print(search_range([5, 7, 7, 8, 8, 10], 8))         # [3, 4]
print(search_range_bisect([5, 7, 7, 8, 8, 10], 8))  # [3, 4]
print(search_range([5, 7, 7, 8, 8, 10], 6))         # [-1, -1]
print(search_range([], 0))                          # [-1, -1]
print(search_range([1], 1))                         # [0, 0]
print(search_range([2, 2, 2, 2], 2))                # [0, 3]
print(search_range([1, 2, 3], 4))                   # [-1, -1]
```

---

## 🔍 Why It Works
```
nums = [5,7,7,8,8,10], target = 8
lower_bound(8) = 3   (first index with value >= 8)
lower_bound(9) = 5   (first index with value >= 9)  -> last = 5 - 1 = 4
Result: [3, 4]
```
हिंदी: lower_bound(target) पहला index देता है और lower_bound(target+1) - 1 आखिरी index।

---

## 📊 Complexity
```
Brute force: Time O(n)     | Space O(1)
Two BS:      Time O(log n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Count occurrences of target — right - left + 1 (or bisect_right - bisect_left)
# VARIANT 2: Search insert position (LC 35) — return lower_bound(target)
# VARIANT 3: Floor / ceiling of a value in a sorted list — use lower_bound with an index check
```

---

## ⚠️ Common Mistake
```python
# (not run) intentionally broken snippets
# ❌ Wrong: plain binary search, then expand left/right linearly
i = search(nums, target)          # finds some occurrence
while i > 0 and nums[i - 1] == target:  # linear walk — O(n) when all elements are equal
    i -= 1

# ✅ Correct: two boundary binary searches, each O(log n) even with all duplicates
```

---

## 🎯 Interview Tip
Say: "Finding any match then expanding is O(n) worst case. I'll implement lower_bound once and reuse it for target and target+1." Mention `bisect_left` / `bisect_right` as the library equivalents.

---

## 🔗 Related Problems
→ D084 (Binary Search) | D085 (Search in Rotated Sorted Array) | D087 (Kth Largest Element)
