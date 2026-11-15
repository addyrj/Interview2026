---

# D009. Longest Common Prefix
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #14

---

## ❓ Problem
Return the longest common prefix string among an array of strings. If there is none, return `""`.

```
Input:  strs = ["flower","flow","flight"]
Output: "fl"
```

---

## 💡 Quick Concept (2 lines only)
The common prefix can never be longer than the shortest word. Compare column by column, or shrink a candidate prefix until every word starts with it.
हिंदी: सबसे छोटे word से ज्यादा लंबा prefix नहीं हो सकता; column-by-column compare करो और जहाँ mismatch हो वहीं रुक जाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — try every prefix length of the first word
# O(n * m^2) time (slicing + startswith), O(1) extra space
# ============================================
def lcp_brute(strs: list[str]) -> str:
    if not strs:                                         # no words at all
        return ""                                        # nothing in common
    best = ""                                            # longest valid prefix found
    for end in range(1, len(strs[0]) + 1):               # try lengths 1..len(first)
        cand = strs[0][:end]                             # candidate prefix
        if all(s.startswith(cand) for s in strs):        # does every word start with it?
            best = cand                                  # yes -> remember it
        else:                                            # first failure
            break                                        # longer ones will fail too
    return best                                          # answer


# ============================================
# APPROACH 2: Vertical scanning ✅ PREFERRED
# O(S) time (S = total chars), O(1) space
# ============================================
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:                                         # empty input
        return ""                                        # nothing in common
    for i, ch in enumerate(strs[0]):                     # column i of the first word
        for s in strs[1:]:                               # compare with every other word
            if i == len(s) or s[i] != ch:                # word too short or mismatch
                return strs[0][:i]                       # prefix ends before column i
    return strs[0]                                       # first word is a prefix of all


# ============================================
# APPROACH 3: min/max trick — only compare lexicographic extremes
# O(S) time, O(1) space
# ============================================
def lcp_minmax(strs: list[str]) -> str:
    if not strs:                                         # empty input
        return ""                                        # nothing in common
    lo, hi = min(strs), max(strs)                        # smallest and largest alphabetically
    for i, (a, b) in enumerate(zip(lo, hi)):             # walk both together
        if a != b:                                       # first difference
            return lo[:i]                                # prefix before it
    return lo                                            # lo is a prefix of hi


# ============================================
# TEST CASES
# ============================================
print(lcp_brute(["flower", "flow", "flight"]))           # fl
print(longest_common_prefix(["flower", "flow", "flight"]))  # fl
print(lcp_minmax(["flower", "flow", "flight"]))          # fl
print(repr(longest_common_prefix(["dog", "racecar", "car"])))  # ''
print(longest_common_prefix(["a"]))                      # a
print(longest_common_prefix(["ab", "a"]))                # a
print(repr(longest_common_prefix([])))                   # ''
print(repr(longest_common_prefix(["", "abc"])))          # ''
```

---

## 🔍 Why It Works
```
flower
flow      column 0 'f' ok, column 1 'l' ok,
flight    column 2: 'o' vs 'o' vs 'i'  -> mismatch -> answer = first 2 chars = "fl"
```
हिंदी: जिस column पर पहली बार कोई word अलग निकले, उससे पहले तक का हिस्सा ही common prefix है।

---

## 📊 Complexity
```
Brute force:   Time O(n * m^2) | Space O(m)
Vertical scan: Time O(S)       | Space O(1)  ← preferred (S = sum of all lengths)
Min/Max trick: Time O(S)       | Space O(1)
```

---

## ⚡ Variations

```python
# VARIANT 1: os.path.commonprefix (works on any sequence, char by char)
import os                                                # stdlib helper
print(os.path.commonprefix(["flower", "flow", "flight"]))  # fl

# VARIANT 2: zip + set — columns where all chars are equal
def lcp_zip(strs: list[str]) -> str:
    out = []                                             # collected chars
    for col in zip(*strs):                               # tuples of the i-th char of each word
        if len(set(col)) != 1:                           # not all the same
            break                                        # stop
        out.append(col[0])                               # keep the shared char
    return "".join(out)                                  # build prefix

print(lcp_zip(["flower", "flow", "flight"]))             # fl

# VARIANT 3: Longest common SUFFIX -> reverse each word, reuse, reverse result
print(longest_common_prefix([w[::-1] for w in ["running", "jumping"]])[::-1])  # ing
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: indexing beyond a shorter word
# s[i] raises IndexError when i == len(s)  -> always check i == len(s) first

# ❌ Wrong: forgetting the empty-list edge case
# strs[0] raises IndexError for []

# ✅ Correct: guard `if not strs`, and check length before indexing
```

---

## 🎯 Interview Tip
Say: "Vertical scanning stops at the first mismatch, so it never does more work than the total characters." Mention the sort/min-max trick as a neat shortcut and the trie for many queries.

---

## 🔗 Related Problems
→ D007 (Valid Anagram) | D008 (Group Anagrams) | D016 (Valid Palindrome)
