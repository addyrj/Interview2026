---

# D076. Longest Common Subsequence
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #1143

---

## ❓ Problem
Given two strings, return the length of their longest common subsequence (characters in order, not necessarily contiguous). Return 0 if none.

```
Input:  text1 = "abcde", text2 = "ace"   Output: 3   ("ace")
Input:  text1 = "abc",   text2 = "def"   Output: 0
```

---

## 💡 Quick Concept (2 lines only)
`dp[i][j]` = LCS of the first `i` chars of A and first `j` chars of B. If the chars match, `dp[i-1][j-1] + 1`; otherwise `max(dp[i-1][j], dp[i][j-1])`.
हिंदी: अक्षर मिलें तो diagonal + 1, न मिलें तो ऊपर या बाएँ का बड़ा मान लो।

---

## ✅ Solution

```python
from functools import lru_cache              # memoization decorator


# ============================================
# APPROACH 1: Brute force — plain recursion on suffixes
# O(2^(m+n)) time, O(m+n) stack
# ============================================
def lcs_brute(a: str, b: str) -> int:
    def go(i: int, j: int) -> int:           # LCS of a[i:] and b[j:]
        if i == len(a) or j == len(b):       # one string exhausted
            return 0                         # nothing common
        if a[i] == b[j]:                     # characters match
            return 1 + go(i + 1, j + 1)      # take it and move both
        return max(go(i + 1, j), go(i, j + 1))   # skip one char from either string

    return go(0, 0)                          # whole strings


# ============================================
# APPROACH 2: Bottom-up 2D table ✅ PREFERRED
# O(m*n) time, O(m*n) space
# ============================================
def longest_common_subsequence(a: str, b: str) -> int:
    m, n = len(a), len(b)                    # lengths
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # padding row/col of zeros
    for i in range(1, m + 1):                # prefix length of a
        for j in range(1, n + 1):            # prefix length of b
            if a[i - 1] == b[j - 1]:         # last chars equal
                dp[i][j] = dp[i - 1][j - 1] + 1   # extend diagonal
            else:                            # chars differ
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])   # drop a char from a or b
    return dp[m][n]                          # answer in the corner


# ============================================
# TEST CASES
# ============================================
print(lcs_brute("abcde", "ace"))             # Expected: 3
print(longest_common_subsequence("abcde", "ace"))   # Expected: 3
print(longest_common_subsequence("abc", "abc"))     # Expected: 3
print(longest_common_subsequence("abc", "def"))     # Expected: 0
print(longest_common_subsequence("", "abc"))        # Expected: 0
print(longest_common_subsequence("AGGTAB", "GXTXAYB"))   # Expected: 4  ("GTAB")
```

---

## 🔍 Why It Works
```
        ""  a  c  e
   ""    0  0  0  0
   a     0  1  1  1
   b     0  1  1  1
   c     0  1  2  2
   d     0  1  2  2
   e     0  1  2  3     <- answer 3
```
हिंदी: हर cell सिर्फ ऊपर, बाएँ और diagonal वाले cells पर निर्भर है, इसलिए table row-by-row भरता है।

---

## 📊 Complexity
```
Brute force: Time O(2^(m+n)) | Space O(m+n)
2D DP:       Time O(m*n)     | Space O(m*n) ← preferred (O(min(m,n)) with rolling rows)
```

---

## ⚡ Variations

```python
# Alternative: rolling single row -> O(min(m, n)) space
def lcs_1d(a: str, b: str) -> int:
    if len(b) > len(a):                      # keep the row short
        a, b = b, a                          # swap so b is the shorter string
    prev = [0] * (len(b) + 1)                # previous row
    for ch in a:                             # each char of the longer string
        cur = [0]                            # current row starts with 0
        for j, bc in enumerate(b, start=1):  # each char of shorter string
            if ch == bc:                     # match
                cur.append(prev[j - 1] + 1)  # diagonal + 1
            else:                            # no match
                cur.append(max(prev[j], cur[j - 1]))   # up or left
        prev = cur                           # roll the row
    return prev[-1]                          # last cell


print(lcs_1d("AGGTAB", "GXTXAYB"))           # Expected: 4


# VARIANT 1: Print the LCS string itself -> walk back from dp[m][n]
def lcs_string(a: str, b: str) -> str:
    m, n = len(a), len(b)                    # lengths
    dp = [[0] * (n + 1) for _ in range(m + 1)]   # table
    for i in range(1, m + 1):                # fill as before
        for j in range(1, n + 1):            # columns
            dp[i][j] = dp[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(dp[i-1][j], dp[i][j-1])   # recurrence
    out: list[str] = []                      # chars collected backwards
    i, j = m, n                              # start at the corner
    while i and j:                           # until a string is used up
        if a[i - 1] == b[j - 1]:             # part of the LCS
            out.append(a[i - 1])             # keep char
            i, j = i - 1, j - 1              # move diagonally
        elif dp[i - 1][j] >= dp[i][j - 1]:   # better to drop from a
            i -= 1                           # go up
        else:                                # better to drop from b
            j -= 1                           # go left
    return "".join(reversed(out))            # restore order


print(lcs_string("AGGTAB", "GXTXAYB"))       # Expected: GTAB
# VARIANT 2: Shortest Common Supersequence -> len(a) + len(b) - LCS
# VARIANT 3: Minimum deletions to make strings equal -> len(a) + len(b) - 2*LCS
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: confusing subsequence with substring -> resetting to 0 on mismatch (that is Longest Common Substring)
# ❌ Wrong: dp table without a padding row/column -> messy index -1 bugs
# ❌ Wrong: [[0]*n]*m -> all rows share one list

# ✅ Correct: (m+1)x(n+1) table via list comprehension, max(up, left) on mismatch
```

---

## 🎯 Interview Tip
Say: "Match: diagonal + 1. Mismatch: best of dropping a char from either string. O(m*n), and I can reduce space with two rows." Be ready to reconstruct the string.

---

## 🔗 Related Problems
→ D077 (Edit Distance) | D075 (Longest Increasing Subsequence) | D078 (0/1 Knapsack)
