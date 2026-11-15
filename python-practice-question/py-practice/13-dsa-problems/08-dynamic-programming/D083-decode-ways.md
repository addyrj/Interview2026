---

# D083. Decode Ways
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #91

---

## ❓ Problem
A message of digits is encoded with `'A' = 1, 'B' = 2, ... 'Z' = 26`. Given a digit string `s`, return the number of ways to decode it. Leading zeros are invalid (`"06"` cannot be decoded, `"0"` alone cannot be decoded).

```
Input:  s = "226"
Output: 3    ("BZ" = 2,26 | "VF" = 22,6 | "BBF" = 2,2,6)
```

---

## 💡 Quick Concept (2 lines only)
`dp[i]` = ways to decode the first `i` chars. A single digit `1-9` adds `dp[i-1]`; a valid two-digit number `10-26` adds `dp[i-2]`. Like Fibonacci, so only two variables are needed.
हिंदी: हर position पर देखो 1 digit valid है या 2 digit (10-26), और पिछले दो answers जोड़ दो।

---

## ✅ Solution

```python
from functools import lru_cache  # memoization decorator for the alternative

# ============================================
# APPROACH 1: Brute force recursion — O(2^n) time, O(n) stack
# ============================================
def num_decodings_brute(s: str) -> int:
    def go(i: int) -> int:                       # ways to decode s[i:]
        if i == len(s):                          # consumed everything -> 1 valid way
            return 1                             # base case success
        if s[i] == "0":                          # a leading zero can never start a code
            return 0                             # dead end
        ways = go(i + 1)                         # take one digit
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26:  # two digits valid (first is non-zero)
            ways += go(i + 2)                    # take two digits
        return ways                              # total ways from here
    return go(0)                                 # start from index 0

# ============================================
# APPROACH 2: Bottom-up DP with O(1) space — O(n) time ✅ PREFERRED
# ============================================
def num_decodings(s: str) -> int:
    if not s or s[0] == "0":                     # empty or leading zero -> impossible
        return 0                                 # no valid decoding
    prev2, prev1 = 1, 1                          # dp[i-2] (empty prefix) and dp[i-1] (first char)
    for i in range(1, len(s)):                   # process from the 2nd char onwards
        cur = 0                                  # ways for prefix of length i+1
        if s[i] != "0":                          # single digit 1-9 is valid
            cur += prev1                         # extend every way of the prefix i
        if 10 <= int(s[i - 1:i + 1]) <= 26:      # last two digits form 10..26
            cur += prev2                         # extend every way of the prefix i-1
        prev2, prev1 = prev1, cur                # slide the window forward
    return prev1                                 # ways for the whole string

# ============================================
# ALTERNATIVE: Pythonic top-down memo with lru_cache — O(n) time, O(n) space
# ============================================
def num_decodings_memo(s: str) -> int:
    @lru_cache(maxsize=None)                     # cache results per index
    def go(i: int) -> int:                       # ways to decode s[i:]
        if i == len(s):                          # reached the end
            return 1                             # one valid decoding
        if s[i] == "0":                          # cannot start with 0
            return 0                             # invalid
        total = go(i + 1)                        # single digit branch
        if s[i:i + 2] in {str(n) for n in range(10, 27)}:  # two-digit branch if 10..26
            total += go(i + 2)                   # add two-digit ways
        return total                             # result for index i
    return go(0)                                 # answer from the start

# ============================================
# TEST CASES
# ============================================
print(num_decodings_brute("226"))   # 3
print(num_decodings("226"))         # 3
print(num_decodings_memo("226"))    # 3
print(num_decodings("12"))          # 2
print(num_decodings("06"))          # 0
print(num_decodings("10"))          # 1
print(num_decodings("2101"))        # 1
print(num_decodings("100"))         # 0
print(num_decodings("1" * 40))      # 165580141
```

---

## 🔍 Why It Works
```
s = "226"
prefix "2"   -> prev1 = 1            (B)
prefix "22"  -> '2' ok (+1), "22" ok (+1) -> 2   (BB, V)
prefix "226" -> '6' ok (+2), "26" ok (+1) -> 3   (BBF, VF, BZ)
```
हिंदी: हर prefix के ways = (single digit valid? पिछला answer) + (two digit valid? उससे पिछला answer)।

---

## 📊 Complexity
```
Brute force: Time O(2^n) | Space O(n) — recursion stack
Memo / DP:   Time O(n)   | Space O(n) memo
Rolling DP:  Time O(n)   | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Decode Ways II (LC 639) — '*' wildcard means 1-9, multiply counts and take mod 1e9+7
# VARIANT 2: Return all decoded strings, not just the count — use backtracking (see D090)
# VARIANT 3: Different alphabet range (e.g. up to 52) — only change the two-digit limit
```

---

## ⚠️ Common Mistake
```python
# (not run) intentionally broken snippets
# ❌ Wrong: treating "06" as a valid two-digit code
if int(s[i - 1:i + 1]) <= 26:     # "06" -> 6 <= 26 passes but leading zero is invalid
    cur += prev2                  # counts a decoding that does not exist

# ❌ Wrong: adding prev1 when s[i] == "0" (a lone 0 has no letter)

# ✅ Correct: single digit needs s[i] != "0"; two digits need 10 <= value <= 26
```

---

## 🎯 Interview Tip
Say: "This is Fibonacci-like: each prefix depends on the previous two. I'll handle '0' explicitly — it is only valid as the second digit of 10 or 20 — then roll two variables for O(1) space." Always test "0", "06", "10", "100".

---

## 🔗 Related Problems
→ D072 (Climbing Stairs) | D073 (House Robber) | D080 (Word Break)
