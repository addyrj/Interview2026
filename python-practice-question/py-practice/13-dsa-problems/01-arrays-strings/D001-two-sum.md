---

# D001. Two Sum
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #1

---

## ❓ Problem
Given a list of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`. Exactly one solution exists and you may not use the same element twice.

```
Input:  nums = [2, 7, 11, 15], target = 9
Output: [0, 1]   (because nums[0] + nums[1] == 9)
```

---

## 💡 Quick Concept (2 lines only)
For each number, the needed partner is `target - num`. Keep a dict of value -> index of numbers already seen; if the partner is in the dict, you are done in one pass.
हिंदी: हर number के लिए `target - num` चाहिए — dict में पहले देखे numbers रखो, partner मिलते ही answer।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — check every pair
# O(n^2) time, O(1) space
# ============================================
def two_sum_brute(nums: list[int], target: int) -> list[int]:
    n = len(nums)                                  # list length
    for i in range(n):                             # first index
        for j in range(i + 1, n):                  # second index after i (no reuse)
            if nums[i] + nums[j] == target:        # pair sums to target
                return [i, j]                      # found
    return []                                      # no pair (not expected per problem)

# ============================================
# APPROACH 2: One-pass hash map ✅ PREFERRED
# O(n) time, O(n) space
# ============================================
def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}                      # value -> index of earlier numbers
    for i, num in enumerate(nums):                 # walk with index
        need = target - num                        # partner required
        if need in seen:                           # partner already seen?
            return [seen[need], i]                 # earlier index first, then current
        seen[num] = i                              # store AFTER check (no self-reuse)
    return []                                      # no pair found

# ============================================
# TEST CASES
# ============================================
print(two_sum_brute([2, 7, 11, 15], 9))   # [0, 1]
print(two_sum([2, 7, 11, 15], 9))         # [0, 1]
print(two_sum([3, 2, 4], 6))              # [1, 2]
print(two_sum([3, 3], 6))                 # [0, 1]   (duplicates work)
print(two_sum([-1, -2, -3, -4, -5], -8))  # [2, 4]   (negatives work)
print(two_sum([1, 2], 10))                # []       (no pair)
```

---

## 🔍 Why It Works
```
nums=[2,7,11,15] target=9
i=0 num=2 need=7  seen={}        -> not found, seen={2:0}
i=1 num=7 need=2  seen={2:0}     -> found! return [0,1]
```
हिंदी: जो चाहिए वो पहले देखा हो तो मिल गया, नहीं तो current number को dict में डालकर आगे बढ़ो।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Hash map:    Time O(n)   | Space O(n)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Sorted input -> two pointers, O(1) space (see D017)
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    lo, hi = 0, len(nums) - 1                      # pointers at both ends
    while lo < hi:                                 # until they meet
        s = nums[lo] + nums[hi]                    # current sum
        if s == target:                            # match
            return [lo, hi]                        # indices
        lo, hi = (lo + 1, hi) if s < target else (lo, hi - 1)  # move the needed side
    return []                                      # none

print(two_sum_sorted([2, 7, 11, 15], 9))           # [0, 1]

# VARIANT 2: Return the values, not indices -> a set is enough
def two_sum_values(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: set[int] = set()                         # numbers seen so far
    for n in nums:                                 # scan
        if target - n in seen:                     # partner seen
            return (target - n, n)                 # values
        seen.add(n)                                # remember
    return None                                    # none

print(two_sum_values([2, 7, 11, 15], 9))           # (2, 7)

# VARIANT 3: Count all pairs (see 3Sum D018 for the triplet version)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: storing before checking lets one element pair with itself
def bad(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}                      # value -> index
    for i, n in enumerate(nums):                   # walk
        seen[n] = i                                # stored first (bug)
        if target - n in seen:                     # finds itself when n*2 == target
            return [seen[target - n], i]           # returns [i, i]
    return []                                      # none

print(bad([3, 2, 4], 6))                           # [0, 0]  <- wrong

# ✅ Correct: check first, store after (see two_sum above) -> [1, 2]
```

---

## 🎯 Interview Tip
Start with brute force O(n^2), then say "I trade O(n) space for time using a hash map of value to index". Mention you store after checking to avoid reusing an element. Follow-up: sorted input -> two pointers (D017).

---

## 🔗 Related Problems
→ D017 (Two Sum II) | D018 (3Sum) | D003 (Contains Duplicate)
