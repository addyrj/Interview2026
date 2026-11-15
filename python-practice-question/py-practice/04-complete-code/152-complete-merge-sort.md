---

# Q152. Complete Merge Sort
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to complete a stable merge sort (returns a new sorted list).

```python
def merge_sort(a: list[int]) -> list[int]:
    if len(a) ____ 1:                              # BLANK 1: base case
        return a
    mid = len(a) // 2
    left = merge_sort(a[:____])                    # BLANK 2: left half
    right = merge_sort(a[____:])                   # BLANK 3: right half
    return merge(left, right)


def merge(l: list[int], r: list[int]) -> list[int]:
    out: list[int] = []
    i = j = 0
    while i < len(l) and j < len(r):
        if l[i] ____ r[j]:                         # BLANK 4: <= keeps the sort stable
            out.append(l[i]); i += 1
        else:
            out.append(r[j]); j += 1
    return out + ____ + ____                       # BLANK 5, 6: leftovers
```

---

## 💡 Quick Concept (2 lines only)
Split in half, sort each half recursively, then merge two sorted lists with two pointers: O(n log n) time, O(n) extra space.
हिंदी: आधा-आधा बाँटो, दोनों को sort करो, फिर दो pointers से merge करो — O(n log n)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def merge_sort(a: list[int]) -> list[int]:         # returns a NEW sorted list
    if len(a) <= 1:                                # BLANK 1: 0 or 1 element is already sorted
        return a                                   # nothing to do
    mid = len(a) // 2                              # Step 1: split point
    left = merge_sort(a[:mid])                     # BLANK 2: sort the left half
    right = merge_sort(a[mid:])                    # BLANK 3: sort the right half
    return merge(left, right)                      # Step 2: combine


def merge(l: list[int], r: list[int]) -> list[int]:  # merge two SORTED lists
    out: list[int] = []                            # result
    i = j = 0                                      # read positions in l and r
    while i < len(l) and j < len(r):               # both have items
        if l[i] <= r[j]:                           # BLANK 4: on ties take left first (stable)
            out.append(l[i]); i += 1               # take from left
        else:
            out.append(r[j]); j += 1               # take from right
    return out + l[i:] + r[j:]                     # BLANK 5/6: one of these is empty, other is the rest


# ============================================
# TEST CASES
# ============================================
print(merge_sort([5, 2, 9, 1, 5, 6]))              # Expected: [1, 2, 5, 5, 6, 9]
print(merge_sort([]))                              # Expected: []
print(merge_sort([3]))                             # Expected: [3]
print(merge_sort([4, 3, 2, 1]))                    # Expected: [1, 2, 3, 4]
data = [3, 1, 2]
print(merge_sort(data), data)                      # Expected: [1, 2, 3] [3, 1, 2]  (input untouched)
```

---

## 🔍 Why This Works (3 lines max)
Lists of length 0/1 are sorted; merging two sorted lists by always taking the smaller head yields a sorted list. Depth is log n and each level does O(n) work. `<=` keeps equal items in original order.
हिंदी: Base case पर list पहले से sorted है; दो sorted lists का merge हमेशा छोटा head लेकर sorted बनता है।

---

## ⚡ Alternative Solution
```python
# Let heapq.merge do the merging (lazy, also stable)
from heapq import merge as hmerge


def merge_sort(a: list[int]) -> list[int]:
    if len(a) <= 1:                                # base case
        return a
    mid = len(a) // 2                              # split
    return list(hmerge(merge_sort(a[:mid]), merge_sort(a[mid:])))  # merge sorted halves

print(merge_sort([5, 2, 9, 1, 5, 6]))              # Expected: [1, 2, 5, 5, 6, 9]
print(sorted([5, 2, 9, 1, 5, 6]))                  # Expected: [1, 2, 5, 5, 6, 9]  (Timsort in real code)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: base case `len(a) == 0` only -> infinite recursion on a 1-element list
# ❌ Wrong: `<` instead of `<=` in merge -> still sorted but NOT stable
# ❌ Wrong: forgetting leftovers (out only) -> items silently dropped
# ✅ Correct: base case <= 1, <= in merge, append both remainders
```

---

## 🎯 Interview Tip (1 line)
Say: "O(n log n) always, stable, O(n) extra space — great for linked lists and external sorting; Python's built-in is Timsort, a merge-sort hybrid."

---

## 🔗 Related Questions
→ Q105 (quick sort) | Q106 (implement merge sort) | Q113 (sorted with key) | D033 (merge two sorted lists)
