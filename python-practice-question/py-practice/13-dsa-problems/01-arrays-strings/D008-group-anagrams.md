---

# D008. Group Anagrams
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #49

---

## ❓ Problem
Given a list of strings, group the anagrams together. Groups and the order inside groups can be returned in any order.

```
Input:  strs = ["eat","tea","tan","ate","nat","bat"]
Output: [["eat","tea","ate"],["tan","nat"],["bat"]]
```

---

## 💡 Quick Concept (2 lines only)
Anagrams share a canonical "signature": the sorted string, or a 26-count tuple. Use a dict from signature -> list of words.
हिंदी: हर word की एक common key बनाओ (sorted letters या count tuple) और dict में उसी key के नीचे words जमा करते जाओ।

---

## ✅ Solution

```python
from collections import defaultdict                      # dict that auto-creates lists


# ============================================
# APPROACH 1: Brute force — compare every word with every group
# O(n^2 * k log k) time, O(n*k) space
# ============================================
def group_anagrams_brute(strs: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []                         # result groups
    for word in strs:                                    # each word
        for g in groups:                                 # try existing groups
            if sorted(g[0]) == sorted(word):             # same letters as the group's first word?
                g.append(word)                           # join that group
                break                                    # stop searching
        else:                                            # no group matched
            groups.append([word])                        # start a new group
    return groups                                        # all groups


# ============================================
# APPROACH 2: Sorted word as key — O(n * k log k) time, O(n*k) space
# ============================================
def group_anagrams_sorted(strs: list[str]) -> list[list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)    # signature -> words
    for word in strs:                                    # each word
        buckets["".join(sorted(word))].append(word)      # sorted letters are the signature
    return list(buckets.values())                        # groups in first-seen order


# ============================================
# APPROACH 3: Count tuple as key ✅ PREFERRED (lowercase a-z)
# O(n * k) time, O(n*k) space
# ============================================
def group_anagrams(strs: list[str]) -> list[list[str]]:
    buckets: dict[tuple[int, ...], list[str]] = defaultdict(list)  # counts -> words
    for word in strs:                                    # each word
        counts = [0] * 26                                # one slot per letter
        for ch in word:                                  # count letters
            counts[ord(ch) - ord("a")] += 1              # a -> 0, b -> 1, ...
        buckets[tuple(counts)].append(word)              # lists are unhashable, tuples are fine
    return list(buckets.values())                        # groups


# ============================================
# TEST CASES
# ============================================
words = ["eat", "tea", "tan", "ate", "nat", "bat"]
print(group_anagrams_brute(words))                       # [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
print(group_anagrams_sorted(words))                      # [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
print(group_anagrams(words))                             # [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
print(group_anagrams([""]))                              # [['']]
print(group_anagrams(["a"]))                             # [['a']]
print(group_anagrams([]))                                # []
```

---

## 🔍 Why It Works
```
"eat" -> sorted "aet"      "tea" -> "aet"     "ate" -> "aet"   -> one bucket
"tan" -> "ant"             "nat" -> "ant"                       -> second bucket
"bat" -> "abt"                                                  -> third bucket
```
हिंदी: Anagrams की sorted spelling हमेशा same होती है, इसलिए वो एक ही dict key पर पहुँचते हैं।

---

## 📊 Complexity
```
Brute force: Time O(n^2 * k log k) | Space O(n*k)
Sorted key:  Time O(n * k log k)   | Space O(n*k)
Count key:   Time O(n * k)         | Space O(n*k)  ← preferred (k = max word length)
```

---

## ⚡ Variations

```python
# VARIANT 1: Any characters (not only a-z) -> use frozenset of Counter items
from collections import Counter                          # frequency counter

def group_any_chars(strs: list[str]) -> list[list[str]]:
    buckets: dict[frozenset, list[str]] = defaultdict(list)  # hashable signature
    for w in strs:                                       # each word
        buckets[frozenset(Counter(w).items())].append(w) # (char, count) pairs
    return list(buckets.values())                        # groups

print(group_any_chars(["Ab", "bA", "ab"]))               # [['Ab', 'bA'], ['ab']]

# VARIANT 2: Return only the largest group
print(max(group_anagrams(words), key=len))               # ['eat', 'tea', 'ate']

# VARIANT 3: Group by "shifted" strings (abc ~ bcd) -> signature = differences between letters
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: a list cannot be a dict key
# d = {}; d[sorted("eat")] = 1      # TypeError: unhashable type: 'list'

# ❌ Wrong: using set(word) as key -> loses counts
print(set("aab") == set("abb"))                          # True  <- but they are not anagrams

# ✅ Correct: use "".join(sorted(word)) or tuple(counts) as the key
```

---

## 🎯 Interview Tip
Say: "The key is a canonical form of each word. Sorting gives O(k log k) per word; a 26-count tuple makes it O(k)." Ask whether input is lowercase a-z only.

---

## 🔗 Related Problems
→ D007 (Valid Anagram) | D028 (Permutation in String) | D003 (Contains Duplicate)
