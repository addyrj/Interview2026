---

# D021. Sort Colors (Dutch flag)
# Category: DSA — Two Pointers
# Difficulty: ⭐⭐ Medium | LeetCode #75

---

## ❓ Problem
Given an array with only `0`, `1`, `2` (red, white, blue), sort it in place so equal colors are adjacent in the order 0, 1, 2. Do not use the library sort.

```
Input:  nums = [2,0,2,1,1,0]
Output: [0,0,1,1,2,2]
```

---

## 💡 Quick Concept (2 lines only)
Dutch National Flag: three pointers `lo`, `mid`, `hi`. Everything before `lo` is 0, after `hi` is 2, and `mid` scans the unknown middle. Swap 0s to the left, 2s to the right.
हिंदी: `lo` तक सब 0, `hi` के बाद सब 2; `mid` बीच के अनजान हिस्से को scan करता है — 0 मिले तो आगे भेजो, 2 मिले तो पीछे।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Counting sort — two passes
# O(n) time, O(1) space (only 3 counters)
# ============================================
def sort_colors_count(nums: list[int]) -> None:
    counts = [0, 0, 0]                                   # how many 0s, 1s, 2s
    for x in nums:                                       # pass 1: count
        counts[x] += 1                                   # tally
    i = 0                                                # write position
    for color, c in enumerate(counts):                   # pass 2: overwrite
        for _ in range(c):                               # c copies of this color
            nums[i] = color                              # write it
            i += 1                                       # next slot


# ============================================
# APPROACH 2: Dutch national flag ✅ PREFERRED (single pass)
# O(n) time, O(1) space
# ============================================
def sort_colors(nums: list[int]) -> None:
    lo, mid, hi = 0, 0, len(nums) - 1                    # boundaries of 0s / unknown / 2s
    while mid <= hi:                                     # until unknown zone is empty
        if nums[mid] == 0:                               # a 0 belongs on the left
            nums[lo], nums[mid] = nums[mid], nums[lo]    # swap into the 0-zone
            lo += 1                                      # 0-zone grows
            mid += 1                                     # swapped-in value is a known 1 (or same index)
        elif nums[mid] == 1:                             # a 1 is already in place
            mid += 1                                     # just move on
        else:                                            # a 2 belongs on the right
            nums[mid], nums[hi] = nums[hi], nums[mid]    # swap into the 2-zone
            hi -= 1                                      # 2-zone grows; do NOT advance mid (unknown value)


# ============================================
# TEST CASES
# ============================================
for fn in (sort_colors_count, sort_colors):              # both approaches
    a = [2, 0, 2, 1, 1, 0]                               # fresh input
    fn(a)                                                # sort in place
    print(fn.__name__, a)                                # [0, 0, 1, 1, 2, 2]

b = [2, 0, 1]
sort_colors(b)
print(b)                                                 # [0, 1, 2]
c = [0]
sort_colors(c)
print(c)                                                 # [0]
d = [1, 1, 1]
sort_colors(d)
print(d)                                                 # [1, 1, 1]
e = [2, 2, 1, 1, 0, 0]
sort_colors(e)
print(e)                                                 # [0, 0, 1, 1, 2, 2]
f: list[int] = []
sort_colors(f)
print(f)                                                 # []
```

---

## 🔍 Why It Works
```
[2,0,2,1,1,0]  lo=0 mid=0 hi=5
mid=0 sees 2 -> swap with hi  -> [0,0,2,1,1,2] hi=4
mid=0 sees 0 -> swap with lo  -> lo=1 mid=1
mid=1 sees 0 -> lo=2 mid=2
mid=2 sees 2 -> swap with hi  -> [0,0,1,1,2,2] hi=3
mid=2 sees 1 -> mid=3 ; mid=3 sees 1 -> mid=4 > hi stop
```
हिंदी: 2 को `hi` से swap करने के बाद `mid` आगे नहीं बढ़ता क्योंकि `hi` से आई value अभी check नहीं हुई।

---

## 📊 Complexity
```
Counting sort: Time O(n), two passes | Space O(1)
Dutch flag:    Time O(n), one pass   | Space O(1)  ← preferred
(Library sort: O(n log n) — not allowed here)
```

---

## ⚡ Variations

```python
# VARIANT 1: Counting sort with Counter (readable, not one-pass)
from collections import Counter                          # frequency map

def sort_colors_counter(nums: list[int]) -> None:
    c = Counter(nums)                                    # counts per color
    nums[:] = [0] * c[0] + [1] * c[1] + [2] * c[2]       # rebuild in order

x = [2, 0, 2, 1, 1, 0]
sort_colors_counter(x)
print(x)                                                 # [0, 0, 1, 1, 2, 2]

# VARIANT 2: Partition around a pivot (3-way partition in quicksort) -> same lo/mid/hi idea
# VARIANT 3: Sort by parity/sign (0 | 1 split) -> two pointers with one swap rule
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: advancing mid after swapping with hi -> skips checking the swapped-in value
def buggy(nums: list[int]) -> None:
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]; lo += 1; mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[hi] = nums[hi], nums[mid]; hi -= 1; mid += 1   # BUG: mid += 1

t = [2, 0, 1, 2, 0]
buggy(t)
print(t)                                                 # [0, 0, 1, 2, 2]  (happens to work here)
t = [1, 2, 0]
buggy(t)
print(t)                                                 # [1, 0, 2]  <- WRONG, not sorted

# ✅ Correct: after swapping with hi, do hi -= 1 only (keep mid)
```

---

## 🎯 Interview Tip
Say: "It's a 3-way partition: invariants are `[0:lo)=0`, `[lo:mid)=1`, `(hi:]=2`. One pass, O(1) space." Mention the 2-pass counting sort as the fallback.

---

## 🔗 Related Problems
→ D011 (Move Zeroes) | D020 (Remove Duplicates from Sorted Array) | D022 (Reverse String)
