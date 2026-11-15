---

# D025. Longest Substring Without Repeating Characters
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐ Medium | LeetCode #3

---

## ❓ Problem
Given a string `s`, return the length of the longest substring that contains no repeated characters.

```
Input:  s = "abcabcbb"
Output: 3    ("abc")
```

---

## 💡 Quick Concept (2 lines only)
Variable-size sliding window `[left, right]`. Store each character's last index; when `s[right]` was seen inside the current window, jump `left` just past that previous index.
हिंदी: Window बढ़ाते रहो; कोई character window में दोबारा आए तो `left` को उसके पिछले index के ठीक आगे कूदा दो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — check every substring
# O(n^3) time (n^2 substrings, O(n) uniqueness check), O(min(n, k)) space
# ============================================
def longest_brute(s: str) -> int:
    best = 0                                             # longest valid length
    for i in range(len(s)):                              # start index
        for j in range(i, len(s)):                       # end index (inclusive)
            sub = s[i:j + 1]                             # candidate substring
            if len(set(sub)) == len(sub):                # all characters unique?
                best = max(best, j - i + 1)              # update best
    return best                                          # answer


# ============================================
# APPROACH 2: Sliding window with a set
# O(n) time, O(k) space (k = alphabet size)
# ============================================
def longest_set(s: str) -> int:
    seen: set[str] = set()                               # characters in the current window
    left = best = 0                                      # window start, best length
    for right, ch in enumerate(s):                       # grow window to the right
        while ch in seen:                                # duplicate inside window?
            seen.remove(s[left])                         # shrink from the left
            left += 1                                    # move start forward
        seen.add(ch)                                     # now ch is unique in the window
        best = max(best, right - left + 1)               # update best
    return best                                          # answer


# ============================================
# APPROACH 3: Sliding window with last-index map ✅ PREFERRED
# O(n) time, O(k) space, left pointer only moves forward
# ============================================
def length_of_longest_substring(s: str) -> int:
    last: dict[str, int] = {}                            # char -> most recent index
    left = best = 0                                      # window start, best length
    for right, ch in enumerate(s):                       # right end of the window
        if ch in last and last[ch] >= left:              # seen inside the current window?
            left = last[ch] + 1                          # jump just past the old copy
        last[ch] = right                                 # record latest position
        best = max(best, right - left + 1)               # update best
    return best                                          # answer


# ============================================
# TEST CASES
# ============================================
print(longest_brute("abcabcbb"))                         # 3
print(longest_set("abcabcbb"))                           # 3
print(length_of_longest_substring("abcabcbb"))           # 3
print(length_of_longest_substring("bbbbb"))              # 1
print(length_of_longest_substring("pwwkew"))             # 3   ("wke", not "pwke": must be contiguous)
print(length_of_longest_substring(""))                   # 0
print(length_of_longest_substring("abba"))               # 2   (tests the `>= left` check)
print(length_of_longest_substring("dvdf"))               # 3   ("vdf")
print(length_of_longest_substring("a b"))                # 3   (spaces count)
```

---

## 🔍 Why It Works
```
s = "abba"
r=0 'a': last[a]=0, window "a"           best=1
r=1 'b': last[b]=1, window "ab"          best=2
r=2 'b': seen at 1 >= left(0) -> left=2, window "b"
r=3 'a': last[a]=0 < left(2) -> stale, ignore! window "ba"  best=2
```
हिंदी: Map में पुराने (window से बाहर) index भी रहते हैं, इसलिए `last[ch] >= left` check ज़रूरी है वरना `left` पीछे चला जाएगा।

---

## 📊 Complexity
```
Brute force:     Time O(n^3) | Space O(k)
Set window:      Time O(n)   | Space O(k)    (each char added/removed once)
Last-index map:  Time O(n)   | Space O(k)  ← preferred (k = alphabet size)
```

---

## ⚡ Variations

```python
# VARIANT 1: Return the substring itself, not just its length
def longest_substring_text(s: str) -> str:
    last: dict[str, int] = {}                            # char -> latest index
    left = start = best = 0                              # window start, best start, best length
    for right, ch in enumerate(s):                       # extend right
        if ch in last and last[ch] >= left:              # duplicate in window
            left = last[ch] + 1                          # shrink
        last[ch] = right                                 # update index
        if right - left + 1 > best:                      # new best window
            best, start = right - left + 1, left         # remember it
    return s[start:start + best]                         # slice out the answer

print(longest_substring_text("abcabcbb"))                # abc

# VARIANT 2: At most K distinct characters -> keep a Counter and shrink while len > K (D031)
# VARIANT 3: Longest substring with at most K repeats -> D027 (character replacement)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: moving `left` without checking it is inside the window
def buggy(s: str) -> int:
    last: dict[str, int] = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last:
            left = last[ch] + 1                          # BUG: can move left BACKWARDS
        last[ch] = right
        best = max(best, right - left + 1)
    return best

print(buggy("abba"))                                     # 3  <- wrong, expected 2

# ❌ Wrong: confusing substring (contiguous) with subsequence ("pwke" is not valid for "pwwkew")

# ✅ Correct: left = max(left, last[ch] + 1)  or  check last[ch] >= left
```

---

## 🎯 Interview Tip
Say: "Sliding window with a last-seen map: when a repeat appears inside the window I jump `left` past it, so each index is visited once — O(n)." Test with `abba` to show the stale-index pitfall.

---

## 🔗 Related Problems
→ D026 (Minimum Size Subarray Sum) | D027 (Longest Repeating Character Replacement) | D031 (Fruit Into Baskets) | D029 (Minimum Window Substring)
