---

# D081. Partition Equal Subset Sum
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #416

---

## ❓ Problem
Given an array of positive integers, return `True` if it can be split into two subsets with equal sum.

```
Input:  nums = [1, 5, 11, 5]
Output: True   ([1, 5, 5] and [11])
```

---

## 💡 Quick Concept (2 lines only)
If the total is odd, answer is False. Otherwise it's subset-sum: can some subset reach `total / 2`? Use a 1D boolean DP (0/1 knapsack).
हिंदी: Total odd हो तो सीधे False; वरना देखो कि कोई subset total/2 बना सकता है या नहीं (0/1 knapsack)।

---

## ✅ Solution

```python
from functools import lru_cache  # memoization for top-down version


# ============================================
# APPROACH 1: Brute force — include/exclude each item, O(2^n)
# ============================================
def can_partition_brute(nums: list[int]) -> bool:
    total = sum(nums)  # total sum
    if total % 2:  # odd total can never split equally
        return False  # impossible

    def go(i: int, remaining: int) -> bool:
        if remaining == 0:  # reached target exactly
            return True  # found a subset
        if i == len(nums) or remaining < 0:  # out of items or overshoot
            return False  # dead end
        return go(i + 1, remaining - nums[i]) or go(i + 1, remaining)  # take it or skip it

    return go(0, total // 2)  # need a subset summing to half


# ============================================
# APPROACH 2: 1D DP — O(n * target) time, O(target) space ✅ PREFERRED
# ============================================
def can_partition(nums: list[int]) -> bool:
    total = sum(nums)  # total sum
    if total % 2:  # odd -> impossible
        return False  # early exit
    target = total // 2  # each half must equal this
    dp = [False] * (target + 1)  # dp[s]: some subset sums to s
    dp[0] = True  # empty subset sums to 0
    for num in nums:  # consider each number once
        for s in range(target, num - 1, -1):  # go backwards so num is used at most once
            dp[s] = dp[s] or dp[s - num]  # either already reachable or reachable via num
        if dp[target]:  # early stop once target is reachable
            return True  # partition exists
    return dp[target]  # final answer


# ============================================
# APPROACH 3: Bitset trick — big int as set of reachable sums
# ============================================
def can_partition_bitset(nums: list[int]) -> bool:
    total = sum(nums)  # total sum
    if total % 2:  # odd -> impossible
        return False  # early exit
    bits = 1  # bit 0 set: sum 0 reachable
    for num in nums:  # for each number
        bits |= bits << num  # shift = "add num to every reachable sum"
    return bool(bits >> (total // 2) & 1)  # is bit target set?


@lru_cache(maxsize=None)  # memo helper used only for demonstration of top-down
def _reach(nums: tuple[int, ...], i: int, remaining: int) -> bool:
    if remaining == 0:  # exact hit
        return True  # success
    if i == len(nums) or remaining < 0:  # no items left / overshoot
        return False  # fail
    return _reach(nums, i + 1, remaining - nums[i]) or _reach(nums, i + 1, remaining)  # take / skip


# ============================================
# TEST CASES
# ============================================
print(can_partition_brute([1, 5, 11, 5]))     # True
print(can_partition([1, 5, 11, 5]))           # True
print(can_partition_bitset([1, 5, 11, 5]))    # True
print(can_partition([1, 2, 3, 5]))            # False
print(can_partition([1]))                     # False
print(can_partition([2, 2, 1, 1]))            # True
print(_reach((3, 3, 3, 4, 5), 0, 9))          # True
```

---

## 🔍 Why It Works
```
nums = [1,5,11,5], target = 11
dp after 1 : sums {0,1}
dp after 5 : sums {0,1,5,6}
dp after 11: sums {0,1,5,6,11,12,16,17}  -> 11 reachable -> True
Backward loop = each number used once (forward loop would reuse it).
```
हिंदी: Inner loop उल्टी चलती है ताकि एक number सिर्फ एक बार use हो; सीधी चलाने पर वही number बार-बार जुड़ जाता।

---

## 📊 Complexity
```
Brute force: Time O(2^n)        | Space O(n)
1D DP:       Time O(n * target) | Space O(target)   ← preferred
Bitset:      Time O(n * target / 64 effectively) | Space O(target) bits
```

---

## ⚡ Variations

```python
# VARIANT 1: Target Sum (LeetCode 494) — count subsets with a given sum (dp[s] += dp[s - num])
# VARIANT 2: Last Stone Weight II — minimize the difference between two subsets
# VARIANT 3: Partition into k equal subsets — backtracking with pruning
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forward inner loop -> reuses the same number multiple times
# for s in range(num, target + 1): dp[s] = dp[s] or dp[s - num]
# e.g. [2, 6] -> total 8, target 4: forward gives dp[4] True via 2+2 (wrong, only one 2)

# ✅ Correct: iterate s from target down to num
```

---

## 🎯 Interview Tip
Say: "Odd sum is an instant False. Then it's 0/1 knapsack for sum/2 and I iterate sums backwards to avoid reusing an item." Mention the Python bitset one-liner as a bonus.

---

## 🔗 Related Problems
→ D078 (0/1 Knapsack) | D074 (Coin Change) | D083 (Decode Ways)
