---

# D024. Max Sum Subarray of Size K
# Category: DSA — Sliding Window
# Difficulty: ⭐ Easy

---

## ❓ Problem
Given an integer array `nums` and an integer `k`, find the maximum sum of any contiguous subarray of length exactly `k`. Return `0` if `k` is invalid (`k <= 0` or `k > len(nums)`).

```
Input:  nums = [2,1,5,1,3,2], k = 3
Output: 9    (subarray [5,1,3])
```

---

## 💡 Quick Concept (2 lines only)
Fixed-size sliding window: compute the first window sum once, then slide by adding the entering element and subtracting the leaving one — O(1) per move instead of re-summing k items.
हिंदी: पहली window का sum निकालो; आगे हर step में नया element जोड़ो और सबसे पुराना घटाओ — दोबारा पूरा sum नहीं करना।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — sum every window
# O(n * k) time, O(1) space
# ============================================
def max_sum_brute(nums: list[int], k: int) -> int:
    if k <= 0 or k > len(nums):                          # invalid window size
        return 0                                         # by problem definition
    best = sum(nums[:k])                                 # start with the first window
    for i in range(1, len(nums) - k + 1):                # every other window start
        best = max(best, sum(nums[i:i + k]))             # re-sum k items each time
    return best                                          # largest sum seen


# ============================================
# APPROACH 2: Sliding window ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def max_sum_subarray(nums: list[int], k: int) -> int:
    if k <= 0 or k > len(nums):                          # invalid window size
        return 0                                         # by problem definition
    window = sum(nums[:k])                               # sum of the first window
    best = window                                        # best so far
    for i in range(k, len(nums)):                        # i = index entering the window
        window += nums[i] - nums[i - k]                  # add new element, drop the oldest
        best = max(best, window)                         # update the answer
    return best                                          # largest window sum


# ============================================
# APPROACH 3: Prefix sums
# O(n) time, O(n) space
# ============================================
def max_sum_prefix(nums: list[int], k: int) -> int:
    if k <= 0 or k > len(nums):                          # invalid window size
        return 0                                         # by problem definition
    prefix = [0]                                         # prefix[i] = sum of first i items
    for x in nums:                                       # build running totals
        prefix.append(prefix[-1] + x)                    # cumulative sum
    return max(prefix[i + k] - prefix[i] for i in range(len(nums) - k + 1))  # window = difference


# ============================================
# TEST CASES
# ============================================
print(max_sum_brute([2, 1, 5, 1, 3, 2], 3))              # 9
print(max_sum_subarray([2, 1, 5, 1, 3, 2], 3))           # 9
print(max_sum_prefix([2, 1, 5, 1, 3, 2], 3))             # 9
print(max_sum_subarray([2, 3, 4, 1, 5], 2))              # 7
print(max_sum_subarray([-1, -2, -3, -4], 2))             # -3  (negatives work)
print(max_sum_subarray([5], 1))                          # 5
print(max_sum_subarray([1, 2], 3))                       # 0   (k larger than array)
print(max_sum_subarray([1, 2, 3], 3))                    # 6   (k == n)
```

---

## 🔍 Why It Works
```
nums = [2,1,5,1,3,2], k=3
window [2,1,5] = 8
slide: +1 -2 -> [1,5,1] = 7
slide: +3 -1 -> [5,1,3] = 9   <- best
slide: +2 -5 -> [1,3,2] = 6
```
हिंदी: Window खिसकाने पर सिर्फ दो elements बदलते हैं, इसलिए पूरा sum दोबारा निकालने की ज़रूरत नहीं।

---

## 📊 Complexity
```
Brute force:    Time O(n*k) | Space O(1)
Sliding window: Time O(n)   | Space O(1)  ← preferred
Prefix sums:    Time O(n)   | Space O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: Also return the start index of the best window
def best_window(nums: list[int], k: int) -> tuple[int, int]:
    window = sum(nums[:k])                               # first window
    best, start = window, 0                              # best sum and where it starts
    for i in range(k, len(nums)):                        # slide
        window += nums[i] - nums[i - k]                  # update sum
        if window > best:                                # new best?
            best, start = window, i - k + 1              # remember it and its start
    return best, start                                   # (sum, start index)

print(best_window([2, 1, 5, 1, 3, 2], 3))                # (9, 2)

# VARIANT 2: Maximum AVERAGE subarray of length k (#643) -> best / k
print(max_sum_subarray([1, 12, -5, -6, 50, 3], 4) / 4)   # 12.75

# VARIANT 3: Variable window (Minimum Size Subarray Sum, D026) -> shrink with a second pointer
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: initialising best = 0 -> wrong when every window sum is negative
def buggy(nums: list[int], k: int) -> int:
    best = 0                                             # BUG: should start from the first window
    window = sum(nums[:k])
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best

print(buggy([-1, -2, -3, -4], 2))                        # 0   <- wrong, expected -3

# ❌ Wrong: off-by-one window update (nums[i - k + 1]) / not checking k > n

# ✅ Correct: seed best with the first window sum
```

---

## 🎯 Interview Tip
Say: "Fixed window: compute the first sum, then each slide is `+new -old`, so O(n) time and O(1) space." Handle `k > n` and negative numbers (don't seed with 0).

---

## 🔗 Related Problems
→ D025 (Longest Substring Without Repeating Characters) | D026 (Minimum Size Subarray Sum) | D005 (Maximum Subarray)
