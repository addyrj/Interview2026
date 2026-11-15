---

# D079. Unique Paths
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #62

---

## ❓ Problem
A robot sits at the top-left of an `m x n` grid and can only move right or down. Count the unique paths to the bottom-right corner.

```
Input:  m = 3, n = 7
Output: 28
```

---

## 💡 Quick Concept (2 lines only)
Paths to a cell = paths from the cell above + paths from the cell on the left. First row and first column have exactly 1 path each.
हिंदी: हर cell तक पहुँचने के रास्ते = ऊपर वाले cell के रास्ते + बाएँ वाले cell के रास्ते; पहली row और column में सिर्फ 1 रास्ता होता है।

---

## ✅ Solution

```python
from functools import lru_cache  # memoization for the brute-force recursion
from math import comb            # binomial coefficient for the math solution


# ============================================
# APPROACH 1: Brute force recursion — O(2^(m+n)) time
# ============================================
def unique_paths_brute(m: int, n: int) -> int:
    if m == 1 or n == 1:  # single row/column -> only one path
        return 1  # base case
    return unique_paths_brute(m - 1, n) + unique_paths_brute(m, n - 1)  # came from above + from left


# ============================================
# APPROACH 2: 1D DP — O(m*n) time, O(n) space ✅ PREFERRED
# ============================================
def unique_paths(m: int, n: int) -> int:
    row = [1] * n  # first row: every cell has exactly 1 path
    for _ in range(1, m):  # process remaining rows
        for j in range(1, n):  # first column stays 1
            row[j] += row[j - 1]  # row[j] (above) + row[j-1] (left)
    return row[-1]  # bottom-right cell


# ============================================
# APPROACH 3: Math — O(min(m,n)) time, O(1) space
# Choose which (m-1) of the (m+n-2) moves are "down"
# ============================================
def unique_paths_math(m: int, n: int) -> int:
    return comb(m + n - 2, m - 1)  # C(total moves, down moves)


# Memoized top-down variant (same idea as brute force, but cached)
@lru_cache(maxsize=None)  # cache results so each (m, n) is computed once
def unique_paths_memo(m: int, n: int) -> int:
    if m == 1 or n == 1:  # base case
        return 1  # only one path along an edge
    return unique_paths_memo(m - 1, n) + unique_paths_memo(m, n - 1)  # sum of both sources


# ============================================
# TEST CASES
# ============================================
print(unique_paths_brute(3, 7))   # 28
print(unique_paths(3, 7))         # 28
print(unique_paths_math(3, 7))    # 28
print(unique_paths_memo(3, 7))    # 28
print(unique_paths(3, 2))         # 3
print(unique_paths(1, 1))         # 1
print(unique_paths(7, 3))         # 28
print(unique_paths(23, 12))       # 193536720
```

---

## 🔍 Why It Works
```
m=3, n=4 grid (each cell = number of paths to reach it):
1  1  1  1
1  2  3  4
1  3  6  10     <- answer 10
1D row trick: row = [1,1,1,1] -> [1,2,3,4] -> [1,3,6,10]
```
हिंदी: पिछली row ही काफी है, इसलिए पूरा 2D table नहीं चाहिए; row[j] में पहले से "ऊपर" वाली value रखी होती है।

---

## 📊 Complexity
```
Brute force: Time O(2^(m+n)) | Space O(m+n) — recursion stack
1D DP:       Time O(m*n)     | Space O(n)   ← preferred
Math:        Time O(min(m,n))| Space O(1)
```

---

## ⚡ Variations

```python
# VARIANT 1: Unique Paths II — obstacles: set dp cell to 0 where grid[i][j] == 1
# VARIANT 2: Minimum Path Sum — dp[j] = grid[i][j] + min(dp[j], dp[j-1])
# VARIANT 3: Allow diagonal moves — add the diagonal neighbour to the sum (Delannoy numbers)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain recursion without cache -> exponential, times out for (23, 12)
# def paths(m, n): return 1 if m == 1 or n == 1 else paths(m-1, n) + paths(m, n-1)

# ❌ Wrong: [[1] * n] * m shares one row object -> all rows change together

# ✅ Correct: 1D DP row, or lru_cache, or math.comb
```

---

## 🎯 Interview Tip
Say: "Brute force is exponential because subproblems repeat; DP stores them. Only the previous row matters, so space drops to O(n). Mathematically it's C(m+n-2, m-1)." Mention the obstacle follow-up.

---

## 🔗 Related Problems
→ D072 (Climbing Stairs) | D073 (House Robber) | D078 (0/1 Knapsack)
