---

# D006. Merge Intervals
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #56

---

## ❓ Problem
Given a list of intervals `[start, end]`, merge all overlapping intervals and return the non-overlapping intervals that cover the same ranges.

```
Input:  intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
```

---

## 💡 Quick Concept (2 lines only)
Sort by start. Then sweep: if the next interval starts at or before the current merged end, extend the end with `max`; otherwise start a new merged interval.
हिंदी: Start के हिसाब से sort करो, फिर अगर अगला interval overlap करे तो end बढ़ाओ, वरना नया interval जोड़ो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — repeatedly merge any overlapping pair
# O(n^2) per pass, may need several passes
# ============================================
def merge_brute(intervals: list[list[int]]) -> list[list[int]]:
    items = [list(i) for i in intervals]           # copy so input is not mutated
    merged = True                                  # loop until nothing merges
    while merged:                                  # another pass needed?
        merged = False                             # assume done
        for i in range(len(items)):                # first interval
            for j in range(i + 1, len(items)):     # second interval
                a, b = items[i], items[j]          # the pair
                if a[0] <= b[1] and b[0] <= a[1]:  # they overlap
                    items[i] = [min(a[0], b[0]), max(a[1], b[1])]  # union
                    items.pop(j)                   # remove the absorbed one
                    merged = True                  # run another pass
                    break                          # restart scan (list changed)
            if merged:                             # list changed
                break                              # restart outer loop
    return sorted(items)                           # sorted for stable output

# ============================================
# APPROACH 2: Sort + linear sweep ✅ PREFERRED
# O(n log n) time, O(n) space
# ============================================
def merge(intervals: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []                      # merged result
    for start, end in sorted(intervals):           # sorted by start (then end)
        if out and start <= out[-1][1]:            # overlaps with last merged
            out[-1][1] = max(out[-1][1], end)      # extend its end
        else:                                      # gap -> new interval
            out.append([start, end])               # add new
    return out                                     # result

# ============================================
# TEST CASES
# ============================================
print(merge_brute([[1,3],[2,6],[8,10],[15,18]]))   # [[1, 6], [8, 10], [15, 18]]
print(merge([[1,3],[2,6],[8,10],[15,18]]))         # [[1, 6], [8, 10], [15, 18]]
print(merge([[1,4],[4,5]]))                        # [[1, 5]]   (touching merges)
print(merge([[1,4],[0,4]]))                        # [[0, 4]]   (unsorted input)
print(merge([[1,10],[2,3],[4,5]]))                 # [[1, 10]]  (contained)
print(merge([]))                                   # []
```

---

## 🔍 Why It Works
```
sorted: [1,3] [2,6] [8,10] [15,18]
[1,3]            -> out=[[1,3]]
[2,6]  2<=3      -> out=[[1,6]]
[8,10] 8>6       -> out=[[1,6],[8,10]]
[15,18] 15>10    -> out=[[1,6],[8,10],[15,18]]
```
हिंदी: Sort के बाद overlap सिर्फ आख़िरी merged interval से ही हो सकता है, इसलिए एक ही sweep काफी है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) or worse | Space O(n)
Sort+sweep:  Time O(n log n)      | Space O(n)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Insert a new interval into a sorted list (LeetCode #57)
def insert(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    return merge(intervals + [new])                # simple: append then merge

print(insert([[1,3],[6,9]], [2,5]))                # [[1, 5], [6, 9]]

# VARIANT 2: Minimum meeting rooms (LeetCode #253) — sort starts/ends or use a heap
def min_rooms(intervals: list[list[int]]) -> int:
    starts = sorted(i[0] for i in intervals)       # sorted start times
    ends = sorted(i[1] for i in intervals)         # sorted end times
    rooms = best = j = 0                           # current rooms, max rooms, end pointer
    for s in starts:                               # each meeting start
        while ends[j] <= s:                        # free rooms that already ended
            j += 1                                 # advance end pointer
            rooms -= 1                             # one room freed
        rooms += 1                                 # take a room
        best = max(best, rooms)                    # track peak
    return best                                    # peak overlap

print(min_rooms([[0,30],[5,10],[15,20]]))          # 2

# VARIANT 3: Count non-overlapping intervals to remove (greedy by end time)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to sort, and overwriting end instead of taking max
def bad(intervals: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []                      # result
    for start, end in intervals:                   # NOT sorted (bug 1)
        if out and start <= out[-1][1]:            # overlap
            out[-1][1] = end                       # bug 2: should be max(...)
        else:                                      # gap
            out.append([start, end])               # new interval
    return out                                     # wrong results

print(bad([[1,10],[2,3]]))                         # [[1, 3]]  <- wrong, expected [[1, 10]]

# ✅ Correct: sort first and use max(out[-1][1], end) (see merge above)
```

---

## 🎯 Interview Tip
Say "sorting by start makes overlaps adjacent, so one pass with `max` on the end suffices — O(n log n) dominated by the sort". Clarify whether touching intervals like [1,4],[4,5] should merge.

---

## 🔗 Related Problems
→ D010 (Rotate Array) | D012 (Spiral Matrix) | D026 (Minimum Size Subarray Sum)
