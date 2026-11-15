---

# D091. Permutations
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #46

---

## ❓ Problem
Given an array of distinct integers, return all possible permutations (any order).

```
Input:  nums = [1, 2, 3]
Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

---

## 💡 Quick Concept (2 lines only)
Build a permutation position by position: try every unused element, recurse, then undo the choice. There are n! results.
हिंदी: हर position पर अब तक unused element चुनो, आगे recurse करो, वापस आकर choice undo करो; कुल n! permutations बनते हैं।

---

## ✅ Solution

```python
from itertools import permutations  # Pythonic alternative


# ============================================
# APPROACH 1: Recursive insertion — O(n * n!) time
# Insert the first element into every position of permutations of the rest
# ============================================
def permute_insert(nums: list[int]) -> list[list[int]]:
    if not nums:  # base case: one empty permutation
        return [[]]  # list containing the empty permutation
    result: list[list[int]] = []  # collected permutations
    for perm in permute_insert(nums[1:]):  # permutations of the remaining items
        for i in range(len(perm) + 1):  # every insertion position
            result.append(perm[:i] + [nums[0]] + perm[i:])  # insert first element at i
    return result  # all permutations


# ============================================
# APPROACH 2: Backtracking with used[] — O(n * n!) time, O(n) space ✅ PREFERRED
# ============================================
def permute(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []  # all permutations
    path: list[int] = []  # permutation being built
    used = [False] * len(nums)  # which indices are already in path

    def backtrack() -> None:
        if len(path) == len(nums):  # complete permutation
            result.append(path[:])  # record a copy
            return  # go back
        for i in range(len(nums)):  # try every element
            if used[i]:  # already placed
                continue  # skip it
            used[i] = True  # choose
            path.append(nums[i])  # add to path
            backtrack()  # explore
            path.pop()  # un-choose
            used[i] = False  # free the index again

    backtrack()  # start recursion
    return result  # all n! permutations


# ============================================
# APPROACH 3: Swap in place — O(n * n!) time, no used[] array
# ============================================
def permute_swap(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []  # collected permutations
    arr = nums[:]  # work on a copy

    def backtrack(first: int) -> None:
        if first == len(arr):  # all positions fixed
            result.append(arr[:])  # record copy
            return  # done with this branch
        for i in range(first, len(arr)):  # choose which element goes at 'first'
            arr[first], arr[i] = arr[i], arr[first]  # swap into position
            backtrack(first + 1)  # fix the next position
            arr[first], arr[i] = arr[i], arr[first]  # swap back

    backtrack(0)  # start at position 0
    return result  # all permutations


# ============================================
# TEST CASES
# ============================================
print(permute([1, 2, 3]))                 # [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
print(permute_insert([1, 2, 3]))          # [[1, 2, 3], [2, 1, 3], [2, 3, 1], [1, 3, 2], [3, 1, 2], [3, 2, 1]]
print(permute_swap([1, 2, 3]))            # [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 2, 1], [3, 1, 2]]
print([list(p) for p in permutations([1, 2, 3])] == permute([1, 2, 3]))  # True
print(permute([0, 1]))                    # [[0, 1], [1, 0]]
print(permute([1]))                       # [[1]]
print(len(permute(list(range(6)))))       # 720
```

---

## 🔍 Why It Works
```
path=[]  used=[F,F,F]
 choose 1 -> choose 2 -> choose 3 => [1,2,3] -> undo 3, undo 2
                choose 3 -> choose 2 => [1,3,2]
 choose 2 -> ... (and so on for 3)
The used[] array stops an element appearing twice in one path.
```
हिंदी: used[] से पता चलता है कौन सा element पहले ही path में है; वापस लौटते समय उसे False करना ज़रूरी है ताकि अगली branch में दोबारा use हो सके।

---

## 📊 Complexity
```
All approaches: Time O(n * n!) | Space O(n) extra (output itself is n * n!)
```

---

## ⚡ Variations

```python
# VARIANT 1: Permutations II (duplicates) — sort and skip if nums[i] == nums[i-1] and not used[i-1]
# VARIANT 2: Next Permutation (LeetCode 31) — in-place, O(n)
# VARIANT 3: Kth permutation sequence — use factorial number system, no full generation
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to reset used[i] after recursion -> only the first permutation is found
# ❌ Wrong: result.append(path) without copying -> all entries end up empty

# ✅ Correct: choose -> recurse -> un-choose (both path.pop() and used[i] = False)
```

---

## 🎯 Interview Tip
Say: "n! results is the lower bound, so O(n * n!) is optimal. I backtrack with a used array, and the swap approach avoids that array." Mention `itertools.permutations` but implement it manually first.

---

## 🔗 Related Problems
→ D090 (Subsets) | D092 (Combination Sum) | D093 (N-Queens)
