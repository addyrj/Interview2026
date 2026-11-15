---

# D007. Valid Anagram
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #242

---

## ❓ Problem
Given two strings `s` and `t`, return `True` if `t` is an anagram of `s` (same letters, same counts, any order), else `False`.

```
Input:  s = "anagram", t = "nagaram"
Output: True
```

---

## 💡 Quick Concept (2 lines only)
Two strings are anagrams if their character counts are identical. Compare sorted strings (O(n log n)) or compare frequency counters (O(n)).
हिंदी: दोनों strings में हर character की count बराबर हो तो anagram — sort करो या Counter बनाओ।

---

## ✅ Solution

```python
from collections import Counter                    # frequency counter

# ============================================
# APPROACH 1: Brute force — remove each char of s from a copy of t
# O(n^2) time, O(n) space
# ============================================
def is_anagram_brute(s: str, t: str) -> bool:
    if len(s) != len(t):                           # different lengths can't match
        return False                               # quick exit
    rest = list(t)                                 # mutable copy of t
    for ch in s:                                   # each char of s
        if ch in rest:                             # still available in t?
            rest.remove(ch)                        # use it (O(n) removal)
        else:                                      # not available
            return False                           # not an anagram
    return not rest                                # everything consumed

# ============================================
# APPROACH 2: Sort both strings
# O(n log n) time, O(n) space
# ============================================
def is_anagram_sort(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)                  # same letters in same order after sort

# ============================================
# APPROACH 3: Counter / frequency map ✅ PREFERRED
# O(n) time, O(k) space (k = alphabet size)
# ============================================
def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):                           # lengths must match
        return False                               # early exit
    return Counter(s) == Counter(t)                # compare character counts

# ============================================
# TEST CASES
# ============================================
print(is_anagram_brute("anagram", "nagaram"))      # True
print(is_anagram_sort("rat", "car"))               # False
print(is_anagram("anagram", "nagaram"))            # True
print(is_anagram("rat", "car"))                    # False
print(is_anagram("", ""))                          # True
print(is_anagram("aab", "abb"))                    # False (same length, different counts)
print(is_anagram("ab", "abc"))                     # False (different length)
```

---

## 🔍 Why It Works
```
"anagram" -> a:3 n:1 g:1 r:1 m:1
"nagaram" -> a:3 n:1 g:1 r:1 m:1   -> equal -> True
```
हिंदी: Order मायने नहीं रखता, सिर्फ हर letter कितनी बार आया — वो बराबर तो anagram।

---

## 📊 Complexity
```
Brute force: Time O(n^2)     | Space O(n)
Sorting:     Time O(n log n) | Space O(n)
Counter:     Time O(n)       | Space O(1) for fixed alphabet (O(k) in general)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Fixed 26-letter array (lowercase a-z only), no hashing
def is_anagram_array(s: str, t: str) -> bool:
    if len(s) != len(t):                           # lengths must match
        return False                               # quick exit
    counts = [0] * 26                              # one slot per letter
    for a, b in zip(s, t):                         # walk both strings together
        counts[ord(a) - ord("a")] += 1             # count letter of s
        counts[ord(b) - ord("a")] -= 1             # uncount letter of t
    return not any(counts)                         # all zeros -> anagram

print(is_anagram_array("anagram", "nagaram"))      # True

# VARIANT 2: Unicode / case-insensitive / ignore spaces
def is_anagram_loose(s: str, t: str) -> bool:
    norm = lambda x: Counter(x.replace(" ", "").casefold())  # normalise text
    return norm(s) == norm(t)                      # compare counters

print(is_anagram_loose("Dormitory", "Dirty room")) # True

# VARIANT 3: Group anagrams together -> D008
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing sets ignores letter counts
print(set("aab") == set("abb"))                    # True  <- wrong, they are not anagrams

# ❌ Wrong: comparing only lengths / sums of char codes can collide
print(sum(map(ord, "ad")) == sum(map(ord, "bc")))  # True  <- wrong ('a'+'d' == 'b'+'c')

# ✅ Correct: compare Counter(s) == Counter(t) or sorted(s) == sorted(t)
print(Counter("aab") == Counter("abb"))            # False
```

---

## 🎯 Interview Tip
Give sort first (simple), then Counter for O(n). Ask about Unicode/case; for lowercase a-z mention a 26-slot array for O(1) space.

---

## 🔗 Related Problems
→ D008 (Group Anagrams) | D028 (Permutation in String) | D003 (Contains Duplicate)
