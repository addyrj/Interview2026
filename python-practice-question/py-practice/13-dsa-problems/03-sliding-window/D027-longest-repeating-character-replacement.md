
---

# D027. Longest Repeating Character Replacement
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐ Medium | LeetCode #424

---

## ❓ Problem
Given an uppercase string `s` and an integer `k`, you may change at most `k` characters to any other uppercase letter. Return the length of the longest substring containing the same letter after those changes.

```
Input:  s = "AABABBA", k = 1
Output: 4      (change one 'A' in "ABBB"/"AABA" -> "BBBB"/"AAAA")
```

---

## 💡 Quick Concept (2 lines only)
A window is valid if `window_length - count_of_most_frequent_char <= k` (the rest are replaced). Expand right always; shrink left only when the window becomes invalid.
हिंदी: Window में सबसे ज़्यादा आने वाले अक्षर को छोड़कर बाकी बदलने पड़ेंगे; अगर वो गिनती k से ज़्यादा हो तो left बढ़ाओ।

---

## ✅ Solution

```python
from collections import Counter  # frequency counter for window letters


# ============================================
# APPROACH 1: Brute force — every start, extend right
# O(n^2) time, O(1) space (at most 26 letters)
# ============================================
def char_replacement_brute(s: str, k: int) -> int:
    best = 0                                   # best window length so far
    for i in range(len(s)):                    # every possible start index
        counts: Counter[str] = Counter()       # letter counts for window s[i..j]
        max_freq = 0                           # most frequent letter count in window
        for j in range(i, len(s)):             # extend the window to the right
            counts[s[j]] += 1                  # add new char to counts
            max_freq = max(max_freq, counts[s[j]])  # update max frequency
            if (j - i + 1) - max_freq <= k:    # replacements needed <= k ?
                best = max(best, j - i + 1)    # window is valid, record length
            else:                              # needs more than k edits
                break                          # longer windows from i only get worse
    return best                                # longest valid window


# ============================================
# APPROACH 2: Sliding window — O(n) time, O(1) space  PREFERRED
# ============================================
def character_replacement(s: str, k: int) -> int:
    counts: dict[str, int] = {}                # letter -> count inside window
    left = 0                                   # left edge of the window
    max_freq = 0                               # highest count seen in any window (never decreased)
    best = 0                                   # answer

    for right, ch in enumerate(s):             # right edge moves one step each time
        counts[ch] = counts.get(ch, 0) + 1     # add s[right] to the window
        max_freq = max(max_freq, counts[ch])   # track the max frequency so far
        while (right - left + 1) - max_freq > k:  # too many replacements needed
            counts[s[left]] -= 1               # remove the left char from window
            left += 1                          # shrink from the left
        best = max(best, right - left + 1)     # window now valid, update answer
    return best                                # longest valid window length


# ============================================
# TEST CASES
# ============================================
for fn in (char_replacement_brute, character_replacement):  # run both approaches
    print(fn("ABAB", 2))      # 4
    print(fn("AABABBA", 1))   # 4
    print(fn("A", 0))         # 1
    print(fn("", 0))          # 0
    print(fn("ABCDE", 1))     # 2
```

---

## 🔍 Why It Works
```
s = "AABABBA", k = 1
window "AABA": len 4, max_freq(A)=3 -> 4-3 = 1 <= k  valid, best = 4
add 'B' -> "AABAB": 5-3 = 2 > k  -> shrink left once
max_freq is never lowered: a stale (too big) value can only
let the window stay the same size, never grow wrongly,
because the answer only improves when max_freq truly rises.
```
हिंदी: max_freq को कभी घटाते नहीं क्योंकि window तभी बड़ी होती है जब कोई नया असली max बने; इसलिए O(1) में काम हो जाता है।

---

## 📊 Complexity
```
Brute force:    Time O(n^2) | Space O(1)
Sliding window: Time O(n)   | Space O(1)  <- preferred (26 letters max)
```

---

## ⚡ Variations

```python
# VARIANT 1: Max Consecutive Ones III (D-style) — same window, "count of zeros <= k"
# VARIANT 2: Lowercase/any characters — use dict instead of 26-array, logic is unchanged
# VARIANT 3: Return the window itself — store best_left when best improves
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: recomputing max(counts.values()) inside the loop every step
#    still correct, but O(26*n) and hides the real trick (max_freq never needs to drop)
# ❌ Wrong: shrinking with "if" instead of "while" when max_freq is stale
#    the window may stay invalid -> over-counts the answer
# ✅ Correct: while (window_len - max_freq) > k: shrink left
```

---

## 🎯 Interview Tip
Say: "Window is valid when length minus the most frequent letter count is at most k. I keep a running max_freq that never decreases, because only a bigger max can produce a bigger answer." Follow-up: why not decrease max_freq?

---

## 🔗 Related Problems
→ D025 (Longest Substring Without Repeating Characters) | D026 (Minimum Size Subarray Sum) | D031 (Fruit Into Baskets)
