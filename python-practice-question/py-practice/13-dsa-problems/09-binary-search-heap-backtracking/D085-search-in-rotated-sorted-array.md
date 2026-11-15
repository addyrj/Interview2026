---

# D085. Search in Rotated Sorted Array
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #33

---

## ❓ Problem
A sorted list of distinct integers was rotated at an unknown pivot (e.g. `[0,1,2,4,5,6,7]` became `[4,5,6,7,0,1,2]`). Given the rotated list and a `target`, return its index or `-1`. Must run in O(log n).

```
Input:  nums = [4, 5, 6, 7, 0, 1, 2], target = 0
Output: 4
```

---

## 💡 Quick Concept (2 lines only)
At any `mid`, at least one half is sorted. Find which half is sorted, check whether target lies inside that sorted range, and keep or discard that half accordingly.
हिंदी: हर बार देखो कौन सा आधा हिस्सा sorted है, target उसकी range में है तो वहीं जाओ, वरना दूसरी तरफ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — O(n) time, O(1) space (ignores the sorted structure)
# ============================================
def search_brute(nums: list[int], target: int) -> int:
    return nums.index(target) if target in nums else -1  # linear scan, then linear search again

# ============================================
# APPROACH 2: Modified binary search — O(log n) time, O(1) space ✅ PREFERRED
# ============================================
def search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1                  # inclusive window
    while lo <= hi:                            # while window not empty
        mid = (lo + hi) // 2                   # middle index
        if nums[mid] == target:                # found it
            return mid                         # return index
        if nums[lo] <= nums[mid]:              # left half [lo..mid] is sorted
            if nums[lo] <= target < nums[mid]: # target lies inside the sorted left half
                hi = mid - 1                   # keep the left half
            else:                              # target must be on the right
                lo = mid + 1                   # keep the right half
        else:                                  # right half [mid..hi] is sorted
            if nums[mid] < target <= nums[hi]: # target lies inside the sorted right half
                lo = mid + 1                   # keep the right half
            else:                              # target must be on the left
                hi = mid - 1                   # keep the left half
    return -1                                  # not present

# ============================================
# ALTERNATIVE: Find pivot first, then bisect on the correct sorted part
# ============================================
from bisect import bisect_left  # standard-library binary search

def search_pivot(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1                  # window for pivot search
    while lo < hi:                             # find index of the smallest value
        mid = (lo + hi) // 2                   # middle index
        if nums[mid] > nums[hi]:               # min is to the right of mid
            lo = mid + 1                       # discard left including mid
        else:                                  # min is at mid or to its left
            hi = mid                           # keep mid
    pivot = lo                                 # index of the smallest element
    for a, b in ((0, pivot), (pivot, len(nums))):  # the two sorted slices
        i = bisect_left(nums, target, a, b)    # bisect inside this slice only
        if i < b and nums[i] == target:        # confirm exact match
            return i                           # return absolute index
    return -1                                  # not in either slice

# ============================================
# TEST CASES
# ============================================
print(search_brute([4, 5, 6, 7, 0, 1, 2], 0))   # 4
print(search([4, 5, 6, 7, 0, 1, 2], 0))         # 4
print(search_pivot([4, 5, 6, 7, 0, 1, 2], 0))   # 4
print(search([4, 5, 6, 7, 0, 1, 2], 3))         # -1
print(search([1], 0))                           # -1
print(search([1], 1))                           # 0
print(search([3, 1], 1))                        # 1
print(search([5, 1, 3], 5))                     # 0
print(search_pivot([5, 1, 3], 3))               # 2
```

---

## 🔍 Why It Works
```
nums = [4,5,6,7,0,1,2], target = 0
lo=0 hi=6 mid=3 (7): left [4..7] sorted, 0 not in [4,7) -> lo=4
lo=4 hi=6 mid=5 (1): left [0..1] sorted, 0 in [0,1)    -> hi=4
lo=4 hi=4 mid=4 (0): found -> 4
```
हिंदी: rotation के बाद भी हर split में एक side हमेशा sorted रहती है, उसी से decision लेते हैं।

---

## 📊 Complexity
```
Brute force: Time O(n)     | Space O(1)
Modified BS: Time O(log n) | Space O(1) ← preferred
Pivot + BS:  Time O(log n) | Space O(1)
```

---

## ⚡ Variations

```python
# VARIANT 1: Duplicates allowed (LC 81) — when nums[lo]==nums[mid]==nums[hi], shrink lo/hi by one (worst case O(n))
# VARIANT 2: Find minimum in rotated sorted array (LC 153) — the pivot loop above
# VARIANT 3: Count how many times the array was rotated — return the pivot index
```

---

## ⚠️ Common Mistake
```python
# (not run) intentionally broken snippets
# ❌ Wrong: strict < when checking the sorted half
if nums[lo] < nums[mid]:          # fails for 2-element windows like [3, 1] where lo == mid
    ...

# ❌ Wrong: checking `nums[lo] <= target <= nums[mid]` after the mid-equality check is fine,
#    but forgetting the bounds check on the sorted half sends you to the wrong side

# ✅ Correct: use nums[lo] <= nums[mid] to detect the sorted left half, and half-open range checks
```

---

## 🎯 Interview Tip
Say: "At every mid, one side is guaranteed sorted. I decide which, test whether the target fits inside that sorted range, and discard the other half — still O(log n)." Mention the duplicates follow-up degrades to O(n).

---

## 🔗 Related Problems
→ D084 (Binary Search) | D086 (Find First and Last Position) | D082 (Maximum Product Subarray)
