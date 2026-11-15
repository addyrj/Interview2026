---

# D080. Word Break
# Category: DSA — Dynamic Programming
# Difficulty: ⭐⭐ Medium | LeetCode #139

---

## ❓ Problem
Given a string `s` and a dictionary `wordDict`, return `True` if `s` can be split into a sequence of one or more dictionary words (words may be reused).

```
Input:  s = "leetcode", wordDict = ["leet", "code"]
Output: True
```

---

## 💡 Quick Concept (2 lines only)
`dp[i]` = can the first `i` characters be segmented? `dp[i]` is True if some `j < i` has `dp[j]` True and `s[j:i]` is a word.
हिंदी: dp[i] बताता है कि पहले i अक्षर तोड़े जा सकते हैं या नहीं; कोई j ऐसा हो जहाँ dp[j] सही हो और s[j:i] dictionary में हो।

---

## ✅ Solution

```python
from functools import lru_cache  # cache for the top-down version


# ============================================
# APPROACH 1: Brute force recursion — O(2^n) time
# ============================================
def word_break_brute(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)  # O(1) membership checks

    def can(start: int) -> bool:
        if start == len(s):  # consumed the whole string
            return True  # success
        for end in range(start + 1, len(s) + 1):  # try every prefix from start
            if s[start:end] in words and can(end):  # prefix is a word and the rest works
                return True  # found a valid split
        return False  # no prefix leads to success

    return can(0)  # start from index 0


# ============================================
# APPROACH 2: Bottom-up DP — O(n * L) time, O(n) space ✅ PREFERRED
# L = longest word length (limits the inner loop)
# ============================================
def word_break(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)  # fast lookup
    max_len = max(map(len, words), default=0)  # longest word bounds the slice size
    dp = [False] * (len(s) + 1)  # dp[i]: s[:i] can be segmented
    dp[0] = True  # empty prefix is always valid
    for i in range(1, len(s) + 1):  # for each end position
        for j in range(max(0, i - max_len), i):  # only starts within max_len
            if dp[j] and s[j:i] in words:  # valid prefix + word in between
                dp[i] = True  # s[:i] is segmentable
                break  # no need to look further
    return dp[-1]  # can the whole string be segmented?


# ============================================
# APPROACH 3: Memoized recursion — O(n^2) time
# ============================================
def word_break_memo(s: str, word_dict: list[str]) -> bool:
    words = frozenset(word_dict)  # immutable set

    @lru_cache(maxsize=None)  # remember results per start index
    def can(start: int) -> bool:
        if start == len(s):  # reached the end
            return True  # fully segmented
        return any(  # any prefix that works
            s[start:end] in words and can(end)  # word + rest segmentable
            for end in range(start + 1, len(s) + 1)  # all candidate ends
        )

    return can(0)  # answer for whole string


# ============================================
# TEST CASES
# ============================================
print(word_break_brute("leetcode", ["leet", "code"]))                         # True
print(word_break("leetcode", ["leet", "code"]))                               # True
print(word_break("applepenapple", ["apple", "pen"]))                          # True
print(word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]))         # False
print(word_break_memo("catsandog", ["cats", "dog", "sand", "and", "cat"]))    # False
print(word_break("a" * 30 + "b", ["a", "aa"]))                                 # False
print(word_break_memo("abcd", ["a", "abc", "b", "cd"]))                       # True
```

---

## 🔍 Why It Works
```
s = "leetcode", words = {leet, code}
dp: idx 0 1 2 3 4 5 6 7 8
        T F F F T F F F T
dp[4] = dp[0] and "leet" in words
dp[8] = dp[4] and "code" in words  -> True
```
हिंदी: पहले अक्षर 0 से शुरू (dp[0]=True), "leet" मिला तो dp[4]=True, फिर "code" मिला तो dp[8]=True यानी जवाब True।

---

## 📊 Complexity
```
Brute force: Time O(2^n)   | Space O(n) — recursion depth
Bottom-up:   Time O(n * L) | Space O(n)   ← preferred (slice cost adds a factor of L)
Memoized:    Time O(n^2)   | Space O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: Word Break II — return all sentences (backtracking + memo of suffix results)
# VARIANT 2: Count the number of ways — dp[i] += dp[j] instead of a boolean
# VARIANT 3: Use a Trie instead of a set to prune early when no word has that prefix
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: greedy — take the longest matching word first
# s = "abcd", words = ["a", "abc", "b", "cd"]: greedy takes "abc" then "d" fails,
# but "a" + "b" + "cd" works

# ❌ Wrong: using a list for words -> "in" is O(k), makes it slower

# ✅ Correct: DP over all split points, with a set for lookups
```

---

## 🎯 Interview Tip
Say: "Brute force retries the same suffixes, so I memoize on the start index. Bottom-up DP with a set is O(n * L) when I bound the inner loop by the longest word." Mention Word Break II as follow-up.

---

## 🔗 Related Problems
→ D083 (Decode Ways) | D074 (Coin Change) | D076 (Longest Common Subsequence)
