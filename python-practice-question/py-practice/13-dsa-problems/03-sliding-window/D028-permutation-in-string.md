
---

# D028. Permutation in String
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐ Medium | LeetCode #567

---

## ❓ Problem
Given two strings `s1` and `s2`, return `True` if `s2` contains a permutation of `s1` (some contiguous substring of `s2` is an anagram of `s1`).

```
Input:  s1 = "ab", s2 = "eidbaooo"
Output: True    ("ba" is a permutation of "ab")
```

---

## 💡 Quick Concept (2 lines only)
A permutation has the same letter counts as `s1`, so slide a fixed window of length `len(s1)` over `s2` and compare counts. Update counts in O(1) as the window moves instead of rebuilding.
हिंदी: Fixed size की window सरकाओ, नया अक्षर जोड़ो, पुराना हटाओ और देखो कि counts s1 के बराबर हैं या नहीं।

---

## ✅ Solution

```python
from collections import Counter  # letter frequency helper


# ============================================
# APPROACH 1: Brute force — sort every window
# O(n * m log m) time, O(m) space
# ============================================
def check_inclusion_brute(s1: str, s2: str) -> bool:
    m = len(s1)                                # window size
    target = sorted(s1)                        # sorted letters of s1
    for i in range(len(s2) - m + 1):           # every window start
        if sorted(s2[i:i + m]) == target:      # same letters when sorted -> anagram
            return True                        # found a permutation
    return False                               # none matched


# ============================================
# APPROACH 2: Fixed window + Counter compare — O(26*n) ~ O(n)
# ============================================
def check_inclusion_counter(s1: str, s2: str) -> bool:
    m = len(s1)                                # window size
    if m > len(s2):                            # s1 longer -> impossible
        return False                           # no window fits
    need = Counter(s1)                         # required letter counts
    window = Counter(s2[:m])                   # counts of the first window
    if window == need:                         # check first window
        return True                            # match at the start
    for i in range(m, len(s2)):                # slide one step at a time
        window[s2[i]] += 1                     # add the new right char
        left = s2[i - m]                       # char leaving the window
        window[left] -= 1                      # remove the left char
        if window[left] == 0:                  # drop zero entries so == works
            del window[left]                   # keep Counter comparison exact
        if window == need:                     # compare counts
            return True                        # permutation found
    return False                               # no window matched


# ============================================
# APPROACH 3: Sliding window with "matches" counter — O(n) time, O(1) space  PREFERRED
# ============================================
def check_inclusion(s1: str, s2: str) -> bool:
    m = len(s1)                                # window size
    if m > len(s2):                            # impossible case
        return False                           # s1 does not fit
    need = [0] * 26                            # s1 counts (a..z)
    win = [0] * 26                             # current window counts
    for a, b in zip(s1, s2[:m]):               # fill first window and need together
        need[ord(a) - 97] += 1                 # count char of s1
        win[ord(b) - 97] += 1                  # count char of first window
    matches = sum(x == y for x, y in zip(need, win))  # how many letters currently equal
    if matches == 26:                          # all 26 letters equal
        return True                            # match at the start
    for i in range(m, len(s2)):                # slide the window
        r = ord(s2[i]) - 97                    # index of char entering
        win[r] += 1                            # add it
        if win[r] == need[r]:                  # became equal
            matches += 1                       # one more matching letter
        elif win[r] == need[r] + 1:            # was equal, now off by one
            matches -= 1                       # one less matching letter
        l = ord(s2[i - m]) - 97                # index of char leaving
        win[l] -= 1                            # remove it
        if win[l] == need[l]:                  # became equal
            matches += 1                       # one more matching letter
        elif win[l] == need[l] - 1:            # was equal, now off by one
            matches -= 1                       # one less matching letter
        if matches == 26:                      # every letter matches
            return True                        # permutation found
    return False                               # not found


# ============================================
# TEST CASES
# ============================================
for fn in (check_inclusion_brute, check_inclusion_counter, check_inclusion):  # all approaches
    print(fn("ab", "eidbaooo"))   # True
    print(fn("ab", "eidboaoo"))   # False
    print(fn("abc", "ab"))        # False
    print(fn("a", "a"))           # True
```

---

## 🔍 Why It Works
```
s1 = "ab", s2 = "eidbaooo", window size 2
"ei" -> "id" -> "db" -> "ba"  (counts a:1, b:1 == need)  True
Each step: +1 for the entering char, -1 for the leaving char.
"matches" tracks how many of the 26 letters are equal, so
checking is O(1) instead of comparing 26 numbers each time.
```
हिंदी: हर step में सिर्फ दो letters का count बदलता है, इसलिए पूरा compare दोबारा नहीं करना पड़ता।

---

## 📊 Complexity
```
Brute force:     Time O(n * m log m) | Space O(m)
Counter compare: Time O(26 * n)      | Space O(1)
Matches counter: Time O(n)           | Space O(1)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Find All Anagrams in a String (LeetCode 438) — collect every start index instead of returning early
# VARIANT 2: Unicode input — use Counter/dict instead of the 26-array
# VARIANT 3: Return the first matching index — return i - m + 1 instead of True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only checking set(s1) <= set(s2) or s1 in s2
#    "ab" in "eidbaooo" is False, yet a permutation exists; sets ignore counts
# ❌ Wrong: Counter compare without deleting zero counts (older Python)
#    Counter({'a': 0}) != Counter() in some code paths, so equality may fail
# ✅ Correct: fixed-size window + counts (delete zeros or use arrays)
```

---

## 🎯 Interview Tip
Say: "A permutation means equal letter counts, so I slide a fixed window of len(s1) and update counts in O(1); a matches counter makes each comparison O(1) too." Follow-up: find all anagram start indices.

---

## 🔗 Related Problems
→ D029 (Minimum Window Substring) | D025 (Longest Substring Without Repeating Characters) | D027 (Longest Repeating Character Replacement)
