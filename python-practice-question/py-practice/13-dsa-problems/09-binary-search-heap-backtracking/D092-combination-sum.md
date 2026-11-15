---

# D092. Combination Sum
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #39

---

## ❓ Problem
Given distinct positive integers `candidates` and a `target`, return all unique combinations that sum to `target`. Each number may be used unlimited times.

```
Input:  candidates = [2, 3, 6, 7], target = 7
Output: [[2, 2, 3], [7]]
```

---

## 💡 Quick Concept (2 lines only)
Backtrack: pick a candidate (starting from the current index so combos aren't repeated in a different order), subtract it from the remaining target, and stop at 0 or when it goes negative.
हिंदी: Candidate चुनो, remaining target घटाओ, वही index दोबारा use कर सकते हो; target 0 पर सही combination, negative पर वापस लौटो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — try all candidates at every step, then dedupe
# Exponential and generates permutations of the same combination
# ============================================
def combination_sum_brute(candidates: list[int], target: int) -> list[list[int]]:
    found: set[tuple[int, ...]] = set()  # sorted tuples remove order duplicates

    def go(path: list[int], remaining: int) -> None:
        if remaining == 0:  # exact sum reached
            found.add(tuple(sorted(path)))  # normalise order
            return  # stop this branch
        if remaining < 0:  # overshoot
            return  # dead end
        for c in candidates:  # any candidate at any step
            go(path + [c], remaining - c)  # extend path

    go([], target)  # start with an empty path
    return sorted(list(t) for t in found)  # deterministic order


# ============================================
# APPROACH 2: Backtracking with start index + pruning ✅ PREFERRED
# Time O(N^(T/M)) where T = target, M = smallest candidate
# ============================================
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    candidates = sorted(candidates)  # sorting enables early break
    result: list[list[int]] = []  # valid combinations
    path: list[int] = []  # current combination

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:  # found a valid combination
            result.append(path[:])  # record a copy
            return  # stop here
        for i in range(start, len(candidates)):  # only candidates from 'start' on
            if candidates[i] > remaining:  # too big, and all later ones are bigger
                break  # prune the rest
            path.append(candidates[i])  # choose
            backtrack(i, remaining - candidates[i])  # i (not i+1): reuse allowed
            path.pop()  # un-choose

    backtrack(0, target)  # begin with the full target
    return result  # all combinations


# ============================================
# APPROACH 3: Bottom-up DP — combos for every sum 0..target
# ============================================
def combination_sum_dp(candidates: list[int], target: int) -> list[list[int]]:
    dp: list[list[list[int]]] = [[] for _ in range(target + 1)]  # dp[s] = combos summing to s
    dp[0] = [[]]  # one way to make 0: the empty combination
    for c in candidates:  # outer loop over coins prevents order duplicates
        for s in range(c, target + 1):  # unbounded: ascending sums
            for combo in dp[s - c]:  # extend every combo of the smaller sum
                dp[s].append(combo + [c])  # add c to it
    return dp[target]  # all combos for target


# ============================================
# TEST CASES
# ============================================
print(combination_sum_brute([2, 3, 6, 7], 7))   # [[2, 2, 3], [7]]
print(combination_sum([2, 3, 6, 7], 7))         # [[2, 2, 3], [7]]
print(combination_sum_dp([2, 3, 6, 7], 7))      # [[2, 2, 3], [7]]
print(combination_sum([2, 3, 5], 8))            # [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
print(combination_sum([2], 1))                  # []
print(combination_sum([1], 3))                  # [[1, 1, 1]]
print(len(combination_sum([2, 3, 5], 30)))      # 21
```

---

## 🔍 Why It Works
```
candidates [2,3,6,7], target 7
2 -> 2 -> 2 -> (remaining 1: 2>1 break)
        2 -> 3 -> remaining 0  => [2,2,3] ✅
2 -> 3 -> ... 6,7 too big
7 -> remaining 0 => [7] ✅
Passing i (not i+1) allows reuse; passing start prevents [3,2,2].
```
हिंदी: `i` आगे भेजने से वही number दोबारा चुन सकते हैं, और `start` से पीछे के numbers नहीं चुने जाते इसलिए [3,2,2] जैसा duplicate नहीं बनता।

---

## 📊 Complexity
```
Backtracking: Time O(N^(T/M)) worst case | Space O(T/M) recursion depth
DP:           Time O(T * N * output size)  | Space O(T * output size)
```

---

## ⚡ Variations

```python
# VARIANT 1: Combination Sum II (each number once, duplicates in input) — sort, recurse i+1, skip equal neighbours
# VARIANT 2: Combination Sum IV — count ordered ways; plain DP count, no backtracking
# VARIANT 3: Combination Sum III — k numbers from 1..9 summing to n
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: loop always starts at 0 -> [2,3,2], [3,2,2] and [2,2,3] all appear (duplicates)
# for i in range(len(candidates)): ...

# ❌ Wrong: recurse with i + 1 -> a number can only be used once (that's Combination Sum II)

# ✅ Correct: for i in range(start, n) and recurse with i
```

---

## 🎯 Interview Tip
Say: "I sort and pass a start index so combinations are generated in non-decreasing order, which avoids duplicates, and break early when a candidate exceeds the remaining target." State the exponential bound.

---

## 🔗 Related Problems
→ D090 (Subsets) | D091 (Permutations) | D074 (Coin Change)
