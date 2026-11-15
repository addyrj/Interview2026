---

# D078. 0/1 Knapsack
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | Classic DP problem

---

## ❓ Problem
Given `n` items with `weights[i]` and `values[i]` and a knapsack of capacity `W`, choose a subset (each item at most once) with total weight at most `W` and maximum total value. Return that maximum value.

```
Input:  weights = [1,3,4,5], values = [1,4,5,7], W = 7
Output: 9   (take weights 3 and 4 -> values 4 + 5)
```

---

## 💡 Quick Concept (2 lines only)
`dp[w]` = best value with capacity `w`. For each item, update capacities from high to low: `dp[w] = max(dp[w], dp[w - wt] + val)`. Going high-to-low ensures each item is used only once.
हिंदी: हर item के लिए capacity को बड़े से छोटे की तरफ update करो ताकि वही item दोबारा न लग जाए।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — recursion: take or skip every item
# O(2^n) time, O(n) stack
# ============================================
def knapsack_brute(weights: list[int], values: list[int], cap: int) -> int:
    def go(i: int, left: int) -> int:        # best value from items i.. with `left` capacity
        if i == len(weights):                # no items left
            return 0                         # no value
        best = go(i + 1, left)               # option 1: skip item i
        if weights[i] <= left:               # option 2: take it if it fits
            best = max(best, values[i] + go(i + 1, left - weights[i]))   # take item i
        return best                          # better option

    return go(0, cap)                        # start with all items and full capacity


# ============================================
# APPROACH 2: 1D DP, capacity iterated downwards ✅ PREFERRED
# O(n * W) time, O(W) space
# ============================================
def knapsack(weights: list[int], values: list[int], cap: int) -> int:
    dp = [0] * (cap + 1)                     # dp[w] = best value using capacity w
    for wt, val in zip(weights, values):     # each item once
        for w in range(cap, wt - 1, -1):     # DOWNWARD: dp[w - wt] still reflects "item not yet used"
            dp[w] = max(dp[w], dp[w - wt] + val)   # skip vs take
    return dp[cap]                           # best value within capacity


# ============================================
# TEST CASES
# ============================================
wts, vals = [1, 3, 4, 5], [1, 4, 5, 7]       # sample items
print(knapsack_brute(wts, vals, 7))          # Expected: 9
print(knapsack(wts, vals, 7))                # Expected: 9
print(knapsack(wts, vals, 0))                # Expected: 0
print(knapsack(wts, vals, 100))              # Expected: 17  (take everything)
print(knapsack([10], [100], 5))              # Expected: 0   (item too heavy)
print(knapsack([2, 3, 4], [3, 4, 5], 5))     # Expected: 7   (items 0 and 1)
```

---

## 🔍 Why It Works
```
cap 7, items (w,v): (1,1) (3,4) (4,5) (5,7)
best subsets: {3,4} -> 9     {1,5} -> 8     {1,3} -> 5   ({3,4} wins)
dp after all items: [0,1,1,4,5,7,8,9]  -> dp[7] = 9
```
हिंदी: ऊपर से नीचे चलने पर dp[w - wt] पुराने (इस item से पहले वाले) मान को दिखाता है, इसलिए item एक ही बार गिना जाता है।

---

## 📊 Complexity
```
Brute force: Time O(2^n)  | Space O(n)
1D DP:       Time O(n*W)  | Space O(W) ← preferred (pseudo-polynomial in W)
```

---

## ⚡ Variations

```python
# Alternative: 2D table, easier to reconstruct which items were taken
def knapsack_2d(weights: list[int], values: list[int], cap: int) -> tuple[int, list[int]]:
    n = len(weights)                         # item count
    dp = [[0] * (cap + 1) for _ in range(n + 1)]   # dp[i][w] over first i items
    for i in range(1, n + 1):                # items
        for w in range(cap + 1):             # capacities
            dp[i][w] = dp[i - 1][w]          # skip item i-1
            if weights[i - 1] <= w:          # fits
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])   # take it
    chosen: list[int] = []                   # indexes of chosen items
    w = cap                                  # walk back from full capacity
    for i in range(n, 0, -1):                # last item to first
        if dp[i][w] != dp[i - 1][w]:         # value changed => item i-1 was taken
            chosen.append(i - 1)             # record it
            w -= weights[i - 1]              # reduce capacity
    return dp[n][cap], sorted(chosen)        # best value + item indexes


print(knapsack_2d(wts, vals, 7))             # Expected: (9, [1, 2])

# VARIANT 1: Unbounded knapsack (unlimited copies) -> iterate capacity UPWARD
# VARIANT 2: Subset Sum / Partition Equal Subset Sum -> same loop with booleans
# VARIANT 3: Large weights, small values -> DP indexed by value instead of weight
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating capacity upward in 1D -> the same item is reused (becomes unbounded knapsack)
#   for w in range(wt, cap + 1): dp[w] = max(dp[w], dp[w - wt] + val)   # knapsack([2],[3],6) gives 9, not 3

# ✅ Correct: for w in range(cap, wt - 1, -1)
```

---

## 🎯 Interview Tip
Say: "Take-or-skip per item gives 2^n; DP over capacity makes it O(n*W). In 1D I loop capacity downward so each item is used once." Note it is pseudo-polynomial.

---

## 🔗 Related Problems
→ D074 (Coin Change) | D076 (Longest Common Subsequence) | D072 (Climbing Stairs)
