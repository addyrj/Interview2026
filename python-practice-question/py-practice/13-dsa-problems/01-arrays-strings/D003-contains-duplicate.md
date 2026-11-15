---

# D003. Contains Duplicate
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #217

---

## ❓ Problem
Given a list of integers `nums`, return `True` if any value appears at least twice, and `False` if all elements are distinct.

```
Input:  nums = [1, 2, 3, 1]
Output: True
```

---

## 💡 Quick Concept (2 lines only)
A set stores only unique values with O(1) lookup. If you meet a number already in the set, it is a duplicate; or compare `len(set(nums))` with `len(nums)`.
हिंदी: Set में पहले देखे numbers रखो — दोबारा मिला तो duplicate है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — compare every pair
# O(n^2) time, O(1) space
# ============================================
def contains_duplicate_brute(nums: list[int]) -> bool:
    for i in range(len(nums)):                     # first element
        for j in range(i + 1, len(nums)):          # every later element
            if nums[i] == nums[j]:                 # same value
                return True                        # duplicate found
    return False                                   # all distinct

# ============================================
# APPROACH 2: Sort, then check neighbours
# O(n log n) time, O(1) extra space if sorting in place
# ============================================
def contains_duplicate_sort(nums: list[int]) -> bool:
    s = sorted(nums)                               # sorted copy (keeps input intact)
    return any(a == b for a, b in zip(s, s[1:]))   # duplicates sit side by side

# ============================================
# APPROACH 3: Hash set, early exit ✅ PREFERRED
# O(n) time, O(n) space
# ============================================
def contains_duplicate(nums: list[int]) -> bool:
    seen: set[int] = set()                         # numbers seen so far
    for n in nums:                                 # scan once
        if n in seen:                              # O(1) membership
            return True                            # duplicate, stop early
        seen.add(n)                                # remember it
    return False                                   # no duplicate

# ============================================
# TEST CASES
# ============================================
print(contains_duplicate_brute([1, 2, 3, 1]))        # True
print(contains_duplicate_sort([1, 2, 3, 4]))         # False
print(contains_duplicate([1, 2, 3, 1]))              # True
print(contains_duplicate([1, 2, 3, 4]))              # False
print(contains_duplicate([]))                        # False
print(contains_duplicate([1, 1, 1, 3, 3, 4, 3, 2]))  # True
```

---

## 🔍 Why It Works
```
nums=[1,2,3,1]
1 -> seen={1}   2 -> seen={1,2}   3 -> seen={1,2,3}   1 -> already in seen -> True
```
हिंदी: Set में हर element एक ही बार रह सकता है, इसलिए दोबारा दिखना मतलब duplicate।

---

## 📊 Complexity
```
Brute force: Time O(n^2)     | Space O(1)
Sorting:     Time O(n log n) | Space O(n) here (sorted copy)
Hash set:    Time O(n)       | Space O(n)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: One-liner (no early exit, always builds the whole set)
def has_dup_oneliner(nums: list[int]) -> bool:
    return len(set(nums)) != len(nums)             # set drops duplicates -> shorter

print(has_dup_oneliner([1, 2, 3, 1]))              # True

# VARIANT 2: Duplicates within distance k (LeetCode #219)
def near_duplicate(nums: list[int], k: int) -> bool:
    last: dict[int, int] = {}                      # value -> last index
    for i, n in enumerate(nums):                   # walk
        if n in last and i - last[n] <= k:         # close enough?
            return True                            # yes
        last[n] = i                                # update last seen index
    return False                                   # none

print(near_duplicate([1, 2, 3, 1], 3))             # True
print(near_duplicate([1, 2, 3, 1], 2))             # False

# VARIANT 3: Return all duplicated values -> collections.Counter (see D007)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using a list for "seen" makes membership O(n) -> whole solution O(n^2)
def slow(nums: list[int]) -> bool:
    seen: list[int] = []                           # list lookup is linear
    for n in nums:                                 # scan
        if n in seen:                              # O(n) each time
            return True                            # duplicate
        seen.append(n)                             # remember
    return False                                   # none

print(slow([1, 2, 3, 1]))                          # True but slow for big inputs

# ✅ Correct: use a set for O(1) lookups (see contains_duplicate above)
```

---

## 🎯 Interview Tip
Offer the three trade-offs: brute force O(1) space, sort O(n log n), hash set O(n) time/O(n) space — and ask whether memory is constrained. Mention the one-liner `len(set(nums)) != len(nums)`.

---

## 🔗 Related Problems
→ D001 (Two Sum) | D015 (Longest Consecutive Sequence) | D007 (Valid Anagram)
