---

# D077. Edit Distance
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐⭐ Hard | LeetCode #72

---

## ❓ Problem
Given two words, return the minimum number of operations (insert, delete, replace one character) needed to convert `word1` into `word2`.

```
Input:  word1 = "horse", word2 = "ros"          Output: 3
Input:  word1 = "intention", word2 = "execution" Output: 5
```

---

## 💡 Quick Concept (2 lines only)
`dp[i][j]` = edits to turn the first `i` chars of A into the first `j` chars of B. If the chars match, copy `dp[i-1][j-1]`; else `1 + min(insert, delete, replace)`.
हिंदी: अक्षर मिले तो diagonal वही मान; न मिले तो 1 + (insert, delete, replace) में से सबसे छोटा।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — recursion trying all three edits
# O(3^(m+n)) time, O(m+n) stack
# ============================================
def edit_brute(a: str, b: str) -> int:
    def go(i: int, j: int) -> int:           # edits to turn a[i:] into b[j:]
        if i == len(a):                      # a used up
            return len(b) - j                # insert the rest of b
        if j == len(b):                      # b used up
            return len(a) - i                # delete the rest of a
        if a[i] == b[j]:                     # equal chars
            return go(i + 1, j + 1)          # no edit needed
        return 1 + min(go(i, j + 1),         # insert b[j]
                       go(i + 1, j),         # delete a[i]
                       go(i + 1, j + 1))     # replace a[i] by b[j]

    return go(0, 0)                          # whole words


# ============================================
# APPROACH 2: Bottom-up DP table ✅ PREFERRED
# O(m*n) time, O(m*n) space
# ============================================
def min_distance(a: str, b: str) -> int:
    m, n = len(a), len(b)                    # lengths
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # (m+1) x (n+1) table
    for i in range(m + 1):                   # converting a[:i] to empty string
        dp[i][0] = i                         # i deletions
    for j in range(n + 1):                   # converting empty string to b[:j]
        dp[0][j] = j                         # j insertions
    for i in range(1, m + 1):                # each prefix of a
        for j in range(1, n + 1):            # each prefix of b
            if a[i - 1] == b[j - 1]:         # last chars match
                dp[i][j] = dp[i - 1][j - 1]  # free
            else:                            # need one edit
                dp[i][j] = 1 + min(dp[i - 1][j],      # delete from a
                                   dp[i][j - 1],      # insert into a
                                   dp[i - 1][j - 1])  # replace
    return dp[m][n]                          # answer in the corner


# ============================================
# TEST CASES
# ============================================
print(edit_brute("horse", "ros"))            # Expected: 3
print(min_distance("horse", "ros"))          # Expected: 3
print(min_distance("intention", "execution"))   # Expected: 5
print(min_distance("", "abc"))               # Expected: 3
print(min_distance("abc", ""))               # Expected: 3
print(min_distance("same", "same"))          # Expected: 0
```

---

## 🔍 Why It Works
```
horse -> ros:   horse -> rorse (replace h->r) -> rose (delete r) -> ros (delete e)   = 3 edits
```
हिंदी: तीनों operations table की तीन पड़ोसी cells से मेल खाते हैं; उनमें सबसे छोटा चुनकर +1 करते हैं।

---

## 📊 Complexity
```
Brute force: Time O(3^(m+n)) | Space O(m+n)
2D DP:       Time O(m*n)     | Space O(m*n) ← preferred (O(n) with two rows)
```

---

## ⚡ Variations

```python
# Alternative: memoised recursion with lru_cache
def edit_memo(a: str, b: str) -> int:
    @lru_cache(maxsize=None)                 # cache (i, j) pairs
    def go(i: int, j: int) -> int:           # edits for a[i:] -> b[j:]
        if i == len(a):                      # a finished
            return len(b) - j                # insert remaining
        if j == len(b):                      # b finished
            return len(a) - i                # delete remaining
        if a[i] == b[j]:                     # match
            return go(i + 1, j + 1)          # free move
        return 1 + min(go(i, j + 1), go(i + 1, j), go(i + 1, j + 1))   # insert / delete / replace
    return go(0, 0)                          # answer


print(edit_memo("intention", "execution"))   # Expected: 5


# Alternative: two rolling rows -> O(n) space
def min_distance_1d(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))           # row for i = 0
    for i, ca in enumerate(a, start=1):      # each char of a
        cur = [i]                            # dp[i][0] = i
        for j, cb in enumerate(b, start=1):  # each char of b
            if ca == cb:                     # match
                cur.append(prev[j - 1])      # diagonal
            else:                            # mismatch
                cur.append(1 + min(prev[j], cur[j - 1], prev[j - 1]))   # best edit
        prev = cur                           # roll
    return prev[-1]                          # last cell


print(min_distance_1d("horse", "ros"))       # Expected: 3

# VARIANT 1: Only insert/delete allowed -> len(a) + len(b) - 2*LCS (see D076)
# VARIANT 2: One Edit Distance (LeetCode 161) -> single pass compare
# VARIANT 3: Weighted costs per operation -> replace the +1 with the cost of each edit
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting the base row/column -> converting to/from the empty string breaks
# ❌ Wrong: on mismatch using only min(up, left) -> forgets replace (diagonal)
# ❌ Wrong: [[0]*(n+1)]*(m+1) -> all rows alias one list

# ✅ Correct: dp[i][0]=i, dp[0][j]=j, mismatch = 1 + min(up, left, diagonal)
```

---

## 🎯 Interview Tip
Say: "The three neighbours of dp[i][j] are delete, insert and replace. Base cases are the cost of building from or to the empty string." Mention space optimisation to two rows.

---

## 🔗 Related Problems
→ D076 (Longest Common Subsequence) | D075 (LIS) | D083 (Decode Ways)
