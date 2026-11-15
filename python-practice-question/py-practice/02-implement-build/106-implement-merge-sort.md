---

# Q106. Implement Merge Sort
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `merge_sort(arr)` returning a new sorted list. It must be stable and run in O(n log n) in all cases.

```python
merge_sort([38, 27, 43, 3, 9, 82, 10])   # [3, 9, 10, 27, 38, 43, 82]
```

---

## 💡 Quick Concept (2 lines only)
Split the list in half, sort each half recursively, then merge the two sorted halves with two pointers. Always O(n log n) time, O(n) extra space.
हिंदी: list को आधा-आधा बाँटो, दोनों को sort करो, फिर दो pointers से merge कर दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def merge_sort(arr: list[int]) -> list[int]:  # returns a new sorted list
    if len(arr) <= 1:  # Step 1: base case
        return arr[:]  # already sorted
    mid = len(arr) // 2  # Step 2: split point
    left = merge_sort(arr[:mid])  # sort left half
    right = merge_sort(arr[mid:])  # sort right half
    return merge(left, right)  # Step 3: combine

def merge(left: list[int], right: list[int]) -> list[int]:  # merge two sorted lists
    out: list[int] = []  # result list
    i = j = 0  # one pointer per list
    while i < len(left) and j < len(right):  # both have items
        if left[i] <= right[j]:  # <= keeps equal items in original order (stable)
            out.append(left[i]); i += 1  # take from left
        else:
            out.append(right[j]); j += 1  # take from right
    out.extend(left[i:])  # leftovers from left (if any)
    out.extend(right[j:])  # leftovers from right (if any)
    return out  # merged sorted list

# ============================================
# TEST CASES
# ============================================
import random  # for a stress test
print(merge_sort([38, 27, 43, 3, 9, 82, 10]))  # Expected: [3, 9, 10, 27, 38, 43, 82]
print(merge_sort([]))  # Expected: []
print(merge_sort([1]))  # Expected: [1]
print(merge_sort([2, 1]))  # Expected: [1, 2]
print(merge_sort([5, 5, 1, 1]))  # Expected: [1, 1, 5, 5]
d = random.sample(range(1000), 300)  # random data
print(merge_sort(d) == sorted(d))  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
Merging two sorted lists needs only one linear pass, and halving gives log n levels, so total O(n log n). Using `<=` takes the left item first on ties, which preserves stability.
हिंदी: दो sorted lists को एक pass में merge कर सकते हैं, और log n levels होते हैं।

---

## ⚡ Alternative Solution
```python
# Use heapq.merge (lazy, stdlib) for the merge step
import heapq  # has a ready-made k-way merge

print(list(heapq.merge([1, 4, 7], [2, 3, 9])))  # Expected: [1, 2, 3, 4, 7, 9]

def ms2(a: list[int]) -> list[int]:
    if len(a) <= 1: return a[:]  # base case
    m = len(a) // 2  # midpoint
    return list(heapq.merge(ms2(a[:m]), ms2(a[m:])))  # sort halves + merge

print(ms2([38, 27, 43, 3, 9, 82, 10]))  # Expected: [3, 9, 10, 27, 38, 43, 82]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to append the leftovers after the while loop
def bad_merge(l, r):
    out = []; i = j = 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]: out.append(l[i]); i += 1
        else: out.append(r[j]); j += 1
    return out  # ❌ remaining items are dropped
print(bad_merge([1, 5], [2, 3, 9]))  # Output: [1, 2, 3, 5]  (9 is lost!)

# ✅ Correct: out.extend(l[i:]); out.extend(r[j:]) before returning
```

---

## 🎯 Interview Tip (1 line)
Say: "Guaranteed O(n log n), stable, O(n) extra space — good for linked lists and external sorting; Python's own Timsort is a merge-sort hybrid."

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q105 (quick sort) | Q152 (complete merge sort) | Q113 (sorted with key)
