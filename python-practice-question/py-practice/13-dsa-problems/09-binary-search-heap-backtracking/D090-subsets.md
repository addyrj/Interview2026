---

# D090. Subsets
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #78

---

## ❓ Problem
Given an array of unique integers, return all possible subsets (the power set). The result must not contain duplicate subsets.

```
Input:  nums = [1, 2, 3]
Output: [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]  (any order)
```

---

## 💡 Quick Concept (2 lines only)
For every element there are two choices: include it or skip it, giving 2^n subsets. Backtracking explores this decision tree.
हिंदी: हर element के लिए दो विकल्प हैं, लो या छोड़ो; कुल 2^n subsets बनते हैं, backtracking से सब generate करो।

---

## ✅ Solution

```python
from itertools import chain, combinations  # for the Pythonic alternative


# ============================================
# APPROACH 1: Iterative build — each new item doubles the list, O(n * 2^n)
# ============================================
def subsets_iterative(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = [[]]  # start with the empty subset
    for x in nums:  # for every number
        result += [s + [x] for s in result]  # copy all existing subsets and add x
    return result  # 2^n subsets


# ============================================
# APPROACH 2: Backtracking — O(n * 2^n) time, O(n) recursion depth ✅ PREFERRED
# ============================================
def subsets(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []  # all subsets collected here
    path: list[int] = []  # current subset being built

    def backtrack(start: int) -> None:
        result.append(path[:])  # every path is a valid subset (copy it!)
        for i in range(start, len(nums)):  # choose next element from start onward
            path.append(nums[i])  # choose
            backtrack(i + 1)  # explore with later elements only
            path.pop()  # un-choose (backtrack)

    backtrack(0)  # begin at index 0
    return result  # all subsets


# ============================================
# APPROACH 3: Bitmask — bit i of mask says "include nums[i]"
# ============================================
def subsets_bitmask(nums: list[int]) -> list[list[int]]:
    n = len(nums)  # size
    return [  # one subset per mask
        [nums[i] for i in range(n) if mask >> i & 1]  # pick elements whose bit is set
        for mask in range(1 << n)  # masks 0 .. 2^n - 1
    ]


# Pythonic: itertools
def subsets_itertools(nums: list[int]) -> list[list[int]]:
    return [list(c) for c in chain.from_iterable(combinations(nums, r) for r in range(len(nums) + 1))]  # all sizes


# ============================================
# TEST CASES
# ============================================
print(subsets([1, 2, 3]))            # [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
print(subsets_iterative([1, 2, 3]))  # [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
print(subsets_bitmask([1, 2, 3]))    # [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
print(subsets_itertools([1, 2, 3]))  # [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
print(subsets([0]))                  # [[], [0]]
print(subsets([]))                   # [[]]
print(len(subsets(list(range(10)))))  # 1024
```

---

## 🔍 Why It Works
```
backtrack tree for [1,2,3] (each node = a subset):
[]
├─[1] ─ [1,2] ─ [1,2,3]
│     └ [1,3]
├─[2] ─ [2,3]
└─[3]
Using "start" means we only pick later elements -> no duplicates like [2,1].
```
हिंदी: `start` से सिर्फ आगे के elements चुने जाते हैं इसलिए [1,2] और [2,1] जैसे duplicates नहीं बनते; हर node एक valid subset है।

---

## 📊 Complexity
```
All approaches: Time O(n * 2^n) | Space O(n) extra (excluding output of size n * 2^n)
```

---

## ⚡ Variations

```python
# VARIANT 1: Subsets II (duplicates in input) — sort, then skip if i > start and nums[i] == nums[i-1]
# VARIANT 2: Combinations (LeetCode 77) — only record when len(path) == k
# VARIANT 3: Subsets with sum == target — prune when running sum exceeds target
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: appending the live list -> every entry ends up as the same (final, empty) list
# result.append(path)          # all entries are [] at the end

# ✅ Correct: append a copy: result.append(path[:])   (or list(path))
```

---

## 🎯 Interview Tip
Say: "Each element is include/exclude, so 2^n results is unavoidable. I use backtracking with a start index to avoid duplicates and copy the path when recording." Mention the bitmask version.

---

## 🔗 Related Problems
→ D091 (Permutations) | D092 (Combination Sum) | D093 (N-Queens)
