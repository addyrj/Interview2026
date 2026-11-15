---

# D020. Remove Duplicates from Sorted Array
# Category: DSA — Two Pointers
# Difficulty: ⭐ Easy | LeetCode #26

---

## ❓ Problem
Given a sorted array `nums`, remove duplicates **in place** so each value appears once. Return `k`, the number of unique values; the first `k` slots of `nums` must hold them in order.

```
Input:  nums = [0,0,1,1,1,2,2,3,3,4]
Output: k = 5, nums[:5] = [0,1,2,3,4]
```

---

## 💡 Quick Concept (2 lines only)
Because the array is sorted, duplicates are adjacent. Keep a write pointer `w`; copy an element forward only when it differs from the last kept one.
हिंदी: Sorted होने से duplicates साथ-साथ होते हैं; नया value मिले तभी उसे `w` पर लिखो और `w` बढ़ाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — set + sort back into place
# O(n log n) time, O(n) space (ignores that input is sorted)
# ============================================
def remove_dups_set(nums: list[int]) -> int:
    uniq = sorted(set(nums))                             # unique values, sorted
    nums[:len(uniq)] = uniq                              # write them to the front (in place)
    return len(uniq)                                     # k


# ============================================
# APPROACH 2: Delete while scanning — correct but slow
# O(n^2) time (each del shifts the tail), O(1) space
# ============================================
def remove_dups_del(nums: list[int]) -> int:
    i = 1                                                # start from the second item
    while i < len(nums):                                 # list shrinks as we delete
        if nums[i] == nums[i - 1]:                       # duplicate of previous
            del nums[i]                                  # remove it (O(n) shift); don't advance i
        else:                                            # new value
            i += 1                                       # move on
    return len(nums)                                     # k


# ============================================
# APPROACH 3: Two pointers ✅ PREFERRED
# O(n) time, O(1) space
# ============================================
def remove_duplicates(nums: list[int]) -> int:
    if not nums:                                         # empty input
        return 0                                         # no uniques
    w = 1                                                # next write slot (nums[0] is always kept)
    for r in range(1, len(nums)):                        # read pointer
        if nums[r] != nums[w - 1]:                       # differs from last kept value
            nums[w] = nums[r]                            # keep it
            w += 1                                       # advance write slot
    return w                                             # number of unique values


# ============================================
# TEST CASES
# ============================================
for fn in (remove_dups_set, remove_dups_del, remove_duplicates):  # every approach
    a = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]                   # fresh input
    k = fn(a)                                            # run it
    print(fn.__name__, k, a[:k])                         # 5 [0, 1, 2, 3, 4]

b = [1, 1, 2]
k = remove_duplicates(b)
print(k, b[:k])                                          # 2 [1, 2]
c = [1]
print(remove_duplicates(c), c)                           # 1 [1]
print(remove_duplicates([]))                             # 0
d = [2, 2, 2, 2]
k = remove_duplicates(d)
print(k, d[:k])                                          # 1 [2]
```

---

## 🔍 Why It Works
```
[0,0,1,1,1,2]   w=1
r=1: 0 == nums[0] skip
r=2: 1 != 0 -> nums[1]=1, w=2
r=3: 1 == nums[1] skip
r=4: 1 skip
r=5: 2 != 1 -> nums[2]=2, w=3      -> first 3 slots: 0,1,2
```
हिंदी: `nums[w-1]` हमेशा आखिरी unique value है; उससे अलग मिले तो नया unique है।

---

## 📊 Complexity
```
Set + sort:   Time O(n log n) | Space O(n)
Delete loop:  Time O(n^2)     | Space O(1)
Two pointers: Time O(n)       | Space O(1)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Allow each value at most TWICE (LeetCode #80) -> compare with nums[w - 2]
def remove_dups_k(nums: list[int], k: int = 2) -> int:
    w = 0                                                # write slot
    for x in nums:                                       # each value
        if w < k or x != nums[w - k]:                    # fewer than k kept, or differs from k-back
            nums[w] = x                                  # keep it
            w += 1                                       # advance
    return w                                             # new length

e = [1, 1, 1, 2, 2, 3]
k = remove_dups_k(e)
print(k, e[:k])                                          # 5 [1, 1, 2, 2, 3]

# VARIANT 2: Unsorted input, keep first occurrences -> use a set of seen values (D003)
# VARIANT 3: Pythonic (not in place): list(dict.fromkeys(nums)) keeps order
print(list(dict.fromkeys([3, 1, 3, 2, 1])))              # [3, 1, 2]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: deleting inside `for x in nums` skips elements
nums = [1, 1, 1, 2]
for i, x in enumerate(nums):
    if i and x == nums[i - 1]:
        nums.remove(x)                                   # removes FIRST match and shifts the list
print(nums)                                              # [1, 1, 2]  <- still has a duplicate

# ❌ Wrong: return len(set(nums)) only -> the array itself isn't compacted in place

# ✅ Correct: two pointers; return w and ignore everything after nums[:w]
```

---

## 🎯 Interview Tip
Say: "Sorted means duplicates are adjacent, so a read/write pointer pair does it in one pass, O(1) space." Ask whether elements beyond `k` matter (they don't).

---

## 🔗 Related Problems
→ D011 (Move Zeroes) | D003 (Contains Duplicate) | D021 (Sort Colors)
