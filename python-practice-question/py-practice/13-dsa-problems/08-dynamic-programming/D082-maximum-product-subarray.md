---

# D082. Maximum Product Subarray
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #152

---

## ❓ Problem
Given an integer array, find the contiguous subarray with the largest product and return that product.

```
Input:  nums = [2, 3, -2, 4]
Output: 6   ([2, 3])
```

---

## 💡 Quick Concept (2 lines only)
A negative number flips the largest product into the smallest and vice versa. Track both the max and min product ending at each index.
हिंदी: Negative number आने पर सबसे बड़ा product सबसे छोटा हो जाता है, इसलिए हर index पर max और min दोनों साथ रखो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — every subarray, O(n^2)
# ============================================
def max_product_brute(nums: list[int]) -> int:
    best = nums[0]  # at least one element must be chosen
    for i in range(len(nums)):  # subarray start
        prod = 1  # running product for this start
        for j in range(i, len(nums)):  # subarray end
            prod *= nums[j]  # extend subarray
            best = max(best, prod)  # update global best
    return best  # largest product seen


# ============================================
# APPROACH 2: Track max & min ending here — O(n) time, O(1) space ✅ PREFERRED
# ============================================
def max_product(nums: list[int]) -> int:
    cur_max = cur_min = best = nums[0]  # products of subarrays ending at index 0
    for x in nums[1:]:  # process remaining numbers
        candidates = (x, cur_max * x, cur_min * x)  # start fresh, extend max, extend min
        cur_max, cur_min = max(candidates), min(candidates)  # new max and min ending here
        best = max(best, cur_max)  # update global answer
    return best  # maximum product found


# ============================================
# APPROACH 3: Prefix / suffix products — O(n) time, O(1) space
# Zeros reset the running product
# ============================================
def max_product_prefix_suffix(nums: list[int]) -> int:
    best = nums[0]  # global best
    prefix = suffix = 1  # running products from left and from right
    n = len(nums)  # length
    for i in range(n):  # walk both directions at once
        prefix = (prefix or 1) * nums[i]  # restart after a zero
        suffix = (suffix or 1) * nums[n - 1 - i]  # same from the right
        best = max(best, prefix, suffix)  # update best
    return best  # answer


# ============================================
# TEST CASES
# ============================================
print(max_product_brute([2, 3, -2, 4]))            # 6
print(max_product([2, 3, -2, 4]))                  # 6
print(max_product_prefix_suffix([2, 3, -2, 4]))    # 6
print(max_product([-2, 0, -1]))                    # 0
print(max_product([-2, 3, -4]))                    # 24
print(max_product([-2]))                           # -2
print(max_product([0, 2]))                         # 2
print(max_product_prefix_suffix([-2, 0, -1]))      # 0
```

---

## 🔍 Why It Works
```
nums = [-2, 3, -4]
i=0: max=-2 min=-2
i=1: x=3  -> candidates (3, -6, -6)  -> max=3  min=-6
i=2: x=-4 -> candidates (-4, -12, 24) -> max=24 min=-12
best = 24  (the earlier min -6 times -4 became the max)
```
हिंदी: पिछला min (-6) को negative (-4) से गुणा करने पर सबसे बड़ा product (24) बन गया, इसीलिए min भी track करना ज़रूरी है।

---

## 📊 Complexity
```
Brute force:   Time O(n^2) | Space O(1)
Max/Min track: Time O(n)   | Space O(1)   ← preferred
Prefix/Suffix: Time O(n)   | Space O(1)
```

---

## ⚡ Variations

```python
# VARIANT 1: Maximum Subarray sum (Kadane) — only the max is needed
# VARIANT 2: Return the subarray itself — remember start/end indices when best updates
# VARIANT 3: Maximum product of 3 numbers — sort or track top-3 and bottom-2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: Kadane with only max -> misses negative * negative
# cur = max(x, cur * x)   # [-2, 3, -4] gives 3, not 24

# ❌ Wrong: updating cur_max first then using the NEW cur_max to compute cur_min
# (compute both from the old values, as the tuple unpacking above does)

# ✅ Correct: keep max and min, derive both from the old values
```

---

## 🎯 Interview Tip
Say: "This is Kadane, but multiplication needs the minimum too since a negative can turn it into a maximum. Zero naturally resets via the 'start fresh' candidate." Mention the prefix/suffix trick.

---

## 🔗 Related Problems
→ D073 (House Robber) | D075 (Longest Increasing Subsequence) | D072 (Climbing Stairs)
