---

# D026. Minimum Size Subarray Sum
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐ Medium | LeetCode #209

---

## ❓ Problem
Given an array of **positive** integers `nums` and an integer `target`, return the minimal length of a contiguous subarray whose sum is `>= target`. Return `0` if none exists.

```
Input:  target = 7, nums = [2, 3, 1, 2, 4, 3]
Output: 2   (subarray [4, 3])
```

---

## 💡 Quick Concept (2 lines only)
Expand the right edge adding numbers; while the window sum is `>= target`, record the length and shrink from the left. Works only because all numbers are positive (shrinking always reduces the sum).
हिंदी: Right बढ़ाते जाओ, sum target के बराबर या ज़्यादा हो जाए तो left से छोटा करते हुए सबसे छोटी length नोट करो।

---

## ✅ Solution

```python
from bisect import bisect_left                 # binary search helper for the prefix-sum variant
from itertools import accumulate               # builds prefix sums


# ============================================
# APPROACH 1: Brute force — try every start, extend until sum >= target
# O(n^2) time, O(1) space
# ============================================
def min_subarray_brute(target: int, nums: list[int]) -> int:
    best = float("inf")                        # best length found so far
    for i in range(len(nums)):                 # every possible start index
        total = 0                              # running sum for this start
        for j in range(i, len(nums)):          # extend the end index
            total += nums[j]                   # add the new element
            if total >= target:                # window is now valid
                best = min(best, j - i + 1)    # record its length
                break                          # longer windows from i are worse
    return 0 if best == float("inf") else best # 0 when nothing qualified


# ============================================
# APPROACH 2: Sliding window — O(n) time, O(1) space  PREFERRED
# ============================================
def min_subarray_len(target: int, nums: list[int]) -> int:
    left = 0                                   # left edge of the window
    total = 0                                  # sum of current window
    best = len(nums) + 1                       # impossible length acts as "infinity"
    for right, value in enumerate(nums):       # grow the window one element at a time
        total += value                         # include nums[right]
        while total >= target:                 # while window is valid, try to shrink
            best = min(best, right - left + 1) # record current length
            total -= nums[left]                # drop the leftmost element
            left += 1                          # move left edge forward
    return 0 if best > len(nums) else best     # no valid window -> 0


# ============================================
# APPROACH 3: Prefix sums + binary search — O(n log n) time, O(n) space
# ============================================
def min_subarray_bisect(target: int, nums: list[int]) -> int:
    prefix = [0, *accumulate(nums)]            # prefix[i] = sum of first i numbers
    best = len(nums) + 1                       # "infinity" length
    for i in range(len(nums)):                 # each start index
        # smallest end where prefix[end] >= prefix[i] + target (prefix is increasing)
        end = bisect_left(prefix, prefix[i] + target, i + 1)
        if end <= len(nums):                   # a valid end exists
            best = min(best, end - i)          # candidate length
    return 0 if best > len(nums) else best     # no window -> 0


# ============================================
# TEST CASES
# ============================================
print(min_subarray_brute(7, [2, 3, 1, 2, 4, 3]))   # 2
print(min_subarray_len(7, [2, 3, 1, 2, 4, 3]))     # 2
print(min_subarray_bisect(7, [2, 3, 1, 2, 4, 3]))  # 2
print(min_subarray_len(4, [1, 4, 4]))              # 1
print(min_subarray_len(11, [1, 1, 1, 1, 1, 1, 1])) # 0
print(min_subarray_len(5, []))                     # 0
```

---

## 🔍 Why It Works
```
target=7  nums=[2,3,1,2,4,3]
[2,3,1,2]   sum=8 >=7 -> len 4, shrink -> [3,1,2] sum=6
[3,1,2,4]   sum=10    -> len 4, shrink -> [1,2,4] 7 -> len 3, shrink -> [2,4] 6
[2,4,3]     sum=9     -> len 3, shrink -> [4,3] 7 -> len 2  <- best
```
हिंदी: हर element window में एक बार आता है और एक बार निकलता है, इसलिए कुल काम O(n) है।

---

## 📊 Complexity
```
Brute force:     Time O(n^2)     | Space O(1)
Sliding window:  Time O(n)       | Space O(1)  <- preferred
Prefix + bisect: Time O(n log n) | Space O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: Array contains negatives -> sliding window breaks; use prefix sums + monotonic deque (LeetCode #862)
# VARIANT 2: Count subarrays with sum >= target -> at each right, add 'left' once window shrinks maximally
# VARIANT 3: Longest subarray with sum <= target (positives) -> same window, but track the max length
```

---

## ⚠️ Common Mistake
```python
# Wrong: using `if` instead of `while` when shrinking
#   if total >= target:        # shrinks only once per right step -> misses shorter windows
#       best = min(best, right - left + 1); total -= nums[left]; left += 1
# Wrong: returning len(nums)+1 / inf when nothing matches instead of 0
# Right: `while total >= target` and convert the sentinel back to 0 at the end
```

---

## 🎯 Interview Tip
Say: "Since all numbers are positive, the window sum is monotonic, so two pointers give O(n). If negatives were allowed I'd switch to prefix sums with a monotonic deque." Follow-up: D025 shows the same expand/shrink pattern.

---

## 🔗 Related Problems
→ D024 (Max Sum Subarray of Size K) | D025 (Longest Substring Without Repeating Characters) | D029 (Minimum Window Substring)
