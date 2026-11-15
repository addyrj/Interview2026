---

# D075. Longest Increasing Subsequence
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #300

---

## ❓ Problem
Given an integer array, return the length of the longest strictly increasing subsequence (elements keep their order but need not be contiguous).

```
Input:  nums = [10,9,2,5,3,7,101,18]   Output: 4   (e.g. 2,3,7,101)
Input:  nums = [0,1,0,3,2,3]           Output: 4
```

---

## 💡 Quick Concept (2 lines only)
O(n^2) DP: `dp[i]` = LIS ending at `i`. Faster: keep a `tails` list where `tails[k]` is the smallest possible tail of an increasing subsequence of length `k+1`, and place each number with binary search.
हिंदी: DP में dp[i] = i पर खत्म होने वाली सबसे लंबी; तेज़ तरीका: tails list रखो और हर number को bisect से सही जगह पर बैठाओ।

---

## ✅ Solution

```python
from bisect import bisect_left               # binary search for the insertion point


# ============================================
# APPROACH 1: Brute force — recursion: skip or take each element
# O(2^n) time, O(n) stack
# ============================================
def lis_brute(nums: list[int]) -> int:
    def go(i: int, prev: float) -> int:      # best length from index i given previous chosen value
        if i == len(nums):                   # end of array
            return 0                         # nothing more to add
        best = go(i + 1, prev)               # option 1: skip nums[i]
        if nums[i] > prev:                   # option 2: take it if it keeps strictly increasing
            best = max(best, 1 + go(i + 1, nums[i]))   # take nums[i]
        return best                          # better of the two

    return go(0, float("-inf"))              # nothing chosen yet


# ============================================
# APPROACH 2: O(n^2) DP (the standard stepping stone)
# O(n^2) time, O(n) space
# ============================================
def lis_dp(nums: list[int]) -> int:
    if not nums:                             # empty input
        return 0                             # no subsequence
    dp = [1] * len(nums)                     # every element alone has length 1
    for i in range(len(nums)):               # end index
        for j in range(i):                   # earlier index
            if nums[j] < nums[i]:            # can extend that subsequence
                dp[i] = max(dp[i], dp[j] + 1)   # best extension
    return max(dp)                           # best end anywhere


# ============================================
# APPROACH 3: Patience sorting with bisect ✅ PREFERRED
# O(n log n) time, O(n) space
# ============================================
def length_of_lis(nums: list[int]) -> int:
    tails: list[int] = []                    # tails[k] = smallest tail of an increasing subseq of length k+1
    for x in nums:                           # each number
        i = bisect_left(tails, x)            # first tail >= x (strict increase => bisect_left)
        if i == len(tails):                  # x is bigger than all tails
            tails.append(x)                  # LIS grows by one
        else:                                # x can improve an existing length
            tails[i] = x                     # smaller tail keeps more future options
    return len(tails)                        # tails length = LIS length (tails itself is NOT the LIS)


# ============================================
# TEST CASES
# ============================================
print(lis_brute([10, 9, 2, 5, 3, 7, 101, 18]))   # Expected: 4
print(lis_dp([10, 9, 2, 5, 3, 7, 101, 18]))      # Expected: 4
print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))   # Expected: 4
print(length_of_lis([0, 1, 0, 3, 2, 3]))     # Expected: 4
print(length_of_lis([7, 7, 7, 7]))           # Expected: 1  (strictly increasing)
print(length_of_lis([]))                     # Expected: 0
```

---

## 🔍 Why It Works
```
nums: 10 9 2 5 3 7 101 18
tails: [10] -> [9] -> [2] -> [2,5] -> [2,3] -> [2,3,7] -> [2,3,7,101] -> [2,3,7,18]
length 4 (the list itself is not the real subsequence, only its length is valid)
```
हिंदी: tails हमेशा sorted रहती है, इसलिए bisect काम करता है; छोटा tail बाद में ज़्यादा elements जोड़ने देता है।

---

## 📊 Complexity
```
Brute force: Time O(2^n)    | Space O(n)
DP:          Time O(n^2)    | Space O(n)
Bisect:      Time O(n log n)| Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: non-decreasing LIS -> use bisect_right instead of bisect_left
from bisect import bisect_right              # insertion after equal elements


def length_of_non_decreasing(nums: list[int]) -> int:
    tails: list[int] = []                    # same tails idea
    for x in nums:                           # each number
        i = bisect_right(tails, x)           # equal values are allowed to extend
        if i == len(tails):                  # bigger or equal to all tails
            tails.append(x)                  # grow
        else:                                # replace
            tails[i] = x                     # keep smallest tail
    return len(tails)                        # length


print(length_of_non_decreasing([7, 7, 7, 7]))   # Expected: 4

# VARIANT 1: Return the actual subsequence -> keep parent indexes (or use DP with prev[] array)
# VARIANT 2: Number of LIS (LeetCode 673) -> DP storing (length, count)
# VARIANT 3: Russian Doll Envelopes -> sort by width asc, height desc, then LIS on heights
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: printing `tails` as the answer subsequence -> it can be a mix that is not a real subsequence
# ❌ Wrong: bisect_right for a STRICT increase -> [7,7,7,7] returns 4 instead of 1
# ❌ Wrong: dp[i] = dp[i-1] + 1 only comparing adjacent elements -> misses non-contiguous subsequences

# ✅ Correct: bisect_left for strict, len(tails) for the length
```

---

## 🎯 Interview Tip
Start with the O(n^2) DP to show the idea, then say: "I can improve to O(n log n) by keeping the smallest tail for each length and binary searching." Know that `tails` is not the subsequence itself.

---

## 🔗 Related Problems
→ D076 (Longest Common Subsequence) | D074 (Coin Change) | D073 (House Robber)
