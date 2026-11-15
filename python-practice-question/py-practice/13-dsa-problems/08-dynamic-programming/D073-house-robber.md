---

# D073. House Robber
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #198

---

## ❓ Problem
Houses in a row hold `nums[i]` money. You cannot rob two adjacent houses. Return the maximum amount you can rob.

```
Input:  nums = [1,2,3,1]     Output: 4   (rob houses 0 and 2)
Input:  nums = [2,7,9,3,1]   Output: 12  (2 + 9 + 1)
```

---

## 💡 Quick Concept (2 lines only)
For each house choose: skip it (keep best so far) or rob it (its money + best up to two houses back). `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`.
हिंदी: हर घर पर दो विकल्प: छोड़ो (पिछला best) या लूटो (इस घर का पैसा + दो घर पीछे का best); बड़ा चुनो।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — recursion over take / skip
# O(2^n) time, O(n) stack
# ============================================
def rob_brute(nums: list[int]) -> int:
    def go(i: int) -> int:                   # best loot from houses i..end
        if i >= len(nums):                   # no houses left
            return 0                         # nothing to rob
        return max(go(i + 1), nums[i] + go(i + 2))   # skip i, or rob i and skip i+1

    return go(0)                             # start from the first house


# ============================================
# APPROACH 2: Two rolling variables ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def rob(nums: list[int]) -> int:
    take, skip = 0, 0                        # best if last house robbed / not robbed
    for x in nums:                           # each house
        take, skip = skip + x, max(take, skip)   # rob x (needs previous skipped) / skip x
    return max(take, skip)                   # best overall


# ============================================
# TEST CASES
# ============================================
print(rob_brute([2, 7, 9, 3, 1]))            # Expected: 12
print(rob([1, 2, 3, 1]))                     # Expected: 4
print(rob([2, 7, 9, 3, 1]))                  # Expected: 12
print(rob([5]))                              # Expected: 5
print(rob([]))                               # Expected: 0
print(rob([2, 1, 1, 2]))                     # Expected: 4  (greedy "take bigger" would give 3)
```

---

## 🔍 Why It Works
```
nums = [2,7,9,3,1]
dp   = [2,7,11,11,12]     dp[2] = max(7, 2+9) = 11 ... dp[4] = max(11, 11+1) = 12
```
हिंदी: dp[i] सिर्फ dp[i-1] और dp[i-2] पर निर्भर है, इसलिए दो variables काफी हैं।

---

## 📊 Complexity
```
Brute force: Time O(2^n) | Space O(n)
Rolling:     Time O(n)   | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: top-down memoisation
def rob_memo(nums: list[int]) -> int:
    @lru_cache(maxsize=None)                 # cache by index
    def go(i: int) -> int:                   # best loot from house i onward
        if i >= len(nums):                   # past the end
            return 0                         # nothing left
        return max(go(i + 1), nums[i] + go(i + 2))   # skip or rob
    return go(0)                             # answer from the start


print(rob_memo([2, 7, 9, 3, 1]))             # Expected: 12


# VARIANT 1: House Robber II (circular street) -> max(rob(nums[1:]), rob(nums[:-1])), special-case length 1
def rob_circular(nums: list[int]) -> int:
    if len(nums) == 1:                       # single house
        return nums[0]                       # just rob it
    return max(rob(nums[1:]), rob(nums[:-1]))   # exclude first or exclude last


print(rob_circular([2, 3, 2]))               # Expected: 3
print(rob_circular([1, 2, 3, 1]))            # Expected: 4

# VARIANT 2: House Robber III (binary tree) -> return (rob, skip) pair per node
# VARIANT 3: Delete and Earn -> reduce to House Robber over value buckets
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: greedy "always take the larger of neighbours" -> [2,1,1,2] gives 3, optimum is 4
# ❌ Wrong: alternating sums (even indexes vs odd indexes) -> fails on [2,1,1,2]-style gaps
# ❌ Wrong: dp[i] = dp[i-1] + nums[i] -> robs adjacent houses

# ✅ Correct: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
```

---

## 🎯 Interview Tip
Say: "At each house I either skip (carry best) or rob (best two back + this house). That recurrence only needs two values, so O(1) space." Mention the circular variant.

---

## 🔗 Related Problems
→ D072 (Climbing Stairs) | D074 (Coin Change) | D083 (Decode Ways)
