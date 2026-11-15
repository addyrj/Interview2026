
---

# D029. Minimum Window Substring
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐⭐ Hard | LeetCode #76

---

## ❓ Problem
Given strings `s` and `t`, return the shortest substring of `s` that contains every character of `t` (with multiplicity). If none exists, return `""`.

```
Input:  s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
```

---

## 💡 Quick Concept (2 lines only)
Expand `right` until the window covers all of `t`, then shrink `left` as far as it stays valid, recording the smallest window. Track how many distinct needed letters are fully satisfied (`formed`).
हिंदी: पहले right बढ़ाकर window को valid बनाओ, फिर left घटाकर उसे छोटा करो; सबसे छोटी valid window ही जवाब है।

---

## ✅ Solution

```python
from collections import Counter  # counts of required characters


# ============================================
# APPROACH 1: Brute force — try every substring
# O(n^2 * ...) time, check with Counter subtraction
# ============================================
def min_window_brute(s: str, t: str) -> str:
    need = Counter(t)                          # required counts
    best = ""                                  # best (shortest) window so far
    for i in range(len(s)):                    # every start index
        for j in range(i + len(t), len(s) + 1):  # every end (exclusive), at least len(t) long
            if best and j - i >= len(best):    # cannot beat current best
                break                          # longer ends are worse
            if not (need - Counter(s[i:j])):   # nothing missing -> window covers t
                best = s[i:j]                  # new shortest window
                break                          # first valid end is shortest for this start
    return best                                # shortest window or ""


# ============================================
# APPROACH 2: Sliding window with "formed" counter — O(n + m) time, O(m) space  PREFERRED
# ============================================
def min_window(s: str, t: str) -> str:
    if not t or len(t) > len(s):               # impossible cases
        return ""                              # nothing to return
    need = Counter(t)                          # required counts per char
    required = len(need)                       # number of distinct chars to satisfy
    have: dict[str, int] = {}                  # counts inside current window
    formed = 0                                 # distinct chars whose need is met
    best_len = float("inf")                    # length of best window
    best_l = 0                                 # start of best window
    left = 0                                   # left edge

    for right, ch in enumerate(s):             # expand the window
        have[ch] = have.get(ch, 0) + 1         # add s[right]
        if ch in need and have[ch] == need[ch]:  # this char just became satisfied
            formed += 1                        # one more satisfied char
        while formed == required:              # window is valid -> try shrinking
            if right - left + 1 < best_len:    # smaller than best?
                best_len = right - left + 1    # remember the length
                best_l = left                  # remember the start
            lc = s[left]                       # char about to leave
            have[lc] -= 1                      # remove it from window
            if lc in need and have[lc] < need[lc]:  # now missing a needed char
                formed -= 1                    # window invalid
            left += 1                          # shrink from the left
    return "" if best_len == float("inf") else s[best_l:best_l + int(best_len)]  # slice answer


# ============================================
# TEST CASES
# ============================================
for fn in (min_window_brute, min_window):  # run both approaches
    print(repr(fn("ADOBECODEBANC", "ABC")))  # 'BANC'
    print(repr(fn("a", "a")))                # 'a'
    print(repr(fn("a", "aa")))               # ''
    print(repr(fn("ab", "b")))               # 'b'
    print(repr(fn("aab", "aab")))            # 'aab'
```

---

## 🔍 Why It Works
```
s = "ADOBECODEBANC", t = "ABC"
right reaches 'C' (idx 5): "ADOBEC" covers A,B,C -> shrink left
  shrink while valid: drop 'A' -> invalid, so best = "ADOBEC" (6)
keep expanding ... window "BANC" (4) is the smallest valid one.
formed == required means every needed char has enough copies.
```
हिंदी: formed बताता है कितने अक्षरों की ज़रूरत पूरी हो गई; पूरी होते ही left घटाकर window छोटी करते हैं।

---

## 📊 Complexity
```
Brute force:    Time O(n^2 * m) | Space O(m)
Sliding window: Time O(n + m)   | Space O(m)  <- preferred (each char enters/leaves once)
```

---

## ⚡ Variations

```python
# VARIANT 1: Return only the length — keep best_len, skip slicing
# VARIANT 2: Smallest window containing all distinct chars of s — need = set(s)
# VARIANT 3: Unicode strings — same code, dict handles any hashable char
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: checking "set(t) <= set(window)" — ignores duplicates in t
#    t = "aa", window "a" would be accepted as valid
# ❌ Wrong: comparing have[ch] >= need[ch] when adding -> formed is counted many times
# ✅ Correct: increment formed only when have[ch] == need[ch] exactly
```

---

## 🎯 Interview Tip
Say: "Two pointers: expand until all required counts are met, then shrink while still valid. A formed-versus-required counter makes the validity check O(1), so total work is O(n + m)." Follow-up: why is it linear though there is a nested while?

---

## 🔗 Related Problems
→ D028 (Permutation in String) | D025 (Longest Substring Without Repeating Characters) | D026 (Minimum Size Subarray Sum)
