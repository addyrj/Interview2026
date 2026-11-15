---

# D005. Maximum Subarray (Kadane)
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #53

---

## ❓ Problem
Given an integer list `nums`, find the contiguous non-empty subarray with the largest sum and return that sum.

```
Input:  nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6   (subarray [4, -1, 2, 1])
```

---

## 💡 Quick Concept (2 lines only)
Kadane: at each element, either extend the previous best subarray ending here or start fresh at this element — `cur = max(x, cur + x)`. The answer is the max `cur` seen.
हिंदी: हर element पर तय करो — पिछला subarray आगे बढ़ाओ या यहीं से नया शुरू करो (जो बड़ा हो)।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — every subarray sum
# O(n^2) time (running sum), O(1) space
# ============================================
def max_subarray_brute(nums: list[int]) -> int:
    best = nums[0]                                 # at least one element is required
    for i in range(len(nums)):                     # start index
        total = 0                                  # running sum from i
        for j in range(i, len(nums)):              # end index
            total += nums[j]                       # extend subarray
            best = max(best, total)                # track the maximum
    return best                                    # answer

# ============================================
# APPROACH 2: Kadane's algorithm ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def max_subarray(nums: list[int]) -> int:
    cur = best = nums[0]                           # best sum ending here / overall
    for x in nums[1:]:                             # remaining elements
        cur = max(x, cur + x)                      # extend or restart at x
        best = max(best, cur)                      # update global best
    return best                                    # answer

# ============================================
# TEST CASES
# ============================================
print(max_subarray_brute([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # 6
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))        # 6
print(max_subarray([1]))                                    # 1
print(max_subarray([5, 4, -1, 7, 8]))                       # 23
print(max_subarray([-3, -1, -2]))                           # -1  (all negative)
print(max_subarray([0, 0, 0]))                              # 0
```

---

## 🔍 Why It Works
```
x:    -2  1  -3  4  -1  2  1  -5  4
cur:  -2  1  -2  4   3  5  6   1  5
best: -2  1   1  4   4  5  6   6  6
```
हिंदी: अगर पिछला sum negative है तो वो बोझ है — छोड़कर नया शुरू करो; इसलिए cur = max(x, cur + x)।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Kadane:      Time O(n)   | Space O(1)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Also return the subarray indices
def max_subarray_range(nums: list[int]) -> tuple[int, int, int]:
    cur = best = nums[0]                           # sums
    start = best_l = best_r = 0                    # current start, best window
    for i in range(1, len(nums)):                  # walk
        if nums[i] > cur + nums[i]:                # restarting is better
            cur, start = nums[i], i                # new window starts at i
        else:                                      # extend
            cur += nums[i]                         # add element
        if cur > best:                             # new global best
            best, best_l, best_r = cur, start, i   # record window
    return best, best_l, best_r                    # sum, left, right

print(max_subarray_range([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # (6, 3, 6)

# VARIANT 2: Divide and conquer, O(n log n) (good to mention, rarely coded)

# VARIANT 3: Maximum product subarray (D082) — track both max and min product
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: initialising best = 0 fails when every number is negative
def bad(nums: list[int]) -> int:
    cur = best = 0                                 # 0 means "empty subarray" (not allowed)
    for x in nums:                                 # walk
        cur = max(x, cur + x)                      # kadane step
        best = max(best, cur)                      # update
    return best                                    # returns 0, not -1

print(bad([-3, -1, -2]))                           # 0   <- wrong, expected -1

# ✅ Correct: start with cur = best = nums[0] (see max_subarray above)
```

---

## 🎯 Interview Tip
Say "the best subarray ending at i either extends the one ending at i-1 or starts at i". Mention initialising from `nums[0]` to handle all-negative input. Offer the index-tracking follow-up.

---

## 🔗 Related Problems
→ D002 (Best Time to Buy and Sell Stock) | D082 (Maximum Product Subarray) | D004 (Product of Array Except Self)
