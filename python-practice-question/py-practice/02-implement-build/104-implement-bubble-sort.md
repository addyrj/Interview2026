---

# Q104. Implement Bubble Sort
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `bubble_sort(arr)` that returns a new sorted list (ascending) without mutating the input. Add the early-exit optimization for already-sorted input.

```python
bubble_sort([5, 2, 9, 1, 5, 6])   # [1, 2, 5, 5, 6, 9]
```

---

## 💡 Quick Concept (2 lines only)
Repeatedly swap adjacent out-of-order pairs; after each pass the largest remaining value "bubbles" to the end. O(n^2) worst case, O(n) best case with the early exit.
हिंदी: पास-पास के elements swap करते रहो — हर pass में सबसे बड़ा element अंत में पहुँच जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def bubble_sort(arr: list[int]) -> list[int]:  # returns a sorted copy
    a = arr[:]  # Step 1: copy so the input is not mutated
    n = len(a)  # number of elements
    for i in range(n - 1):  # Step 2: at most n-1 passes
        swapped = False  # track whether this pass changed anything
        for j in range(n - 1 - i):  # last i items are already in place
            if a[j] > a[j + 1]:  # neighbours out of order?
                a[j], a[j + 1] = a[j + 1], a[j]  # swap with tuple assignment
                swapped = True  # remember we swapped
        if not swapped:  # Step 3: no swaps -> already sorted
            break  # early exit
    return a  # sorted copy

# ============================================
# TEST CASES
# ============================================
print(bubble_sort([5, 2, 9, 1, 5, 6]))  # Expected: [1, 2, 5, 5, 6, 9]
print(bubble_sort([]))  # Expected: []
print(bubble_sort([1]))  # Expected: [1]
print(bubble_sort([3, 2, 1]))  # Expected: [1, 2, 3]
print(bubble_sort([1, 2, 3]))  # Expected: [1, 2, 3]  (one pass, early exit)
orig = [3, 1, 2]  # original list
bubble_sort(orig)  # sort a copy
print(orig)  # Expected: [3, 1, 2]  (unchanged)
```

---

## 🔍 Why This Works (3 lines max)
Each pass fixes the largest unsorted item at the end, so the inner range shrinks by one. The `swapped` flag stops early when a full pass makes no swaps.
हिंदी: हर pass में एक बड़ा element अपनी जगह पहुँचता है, और swap न हो तो loop जल्दी रुक जाता है।

---

## ⚡ Alternative Solution
```python
# In-place version that also shrinks the range to the last swap position
def bubble_inplace(a: list[int]) -> None:
    n = len(a)  # current unsorted length
    while n > 1:  # until range is trivial
        new_n = 0  # index of the last swap in this pass
        for j in range(1, n):  # compare neighbours
            if a[j - 1] > a[j]:  # out of order
                a[j - 1], a[j] = a[j], a[j - 1]  # swap
                new_n = j  # remember last swap position
        n = new_n  # everything after it is already sorted

x = [5, 2, 9, 1]  # sample list
bubble_inplace(x)  # sort in place
print(x)  # Expected: [1, 2, 5, 9]
# In real code just use sorted() / list.sort() (Timsort, O(n log n))
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: inner loop goes to the end -> a[j + 1] is out of range
def bad(a):
    for i in range(len(a)):
        for j in range(len(a)):  # ❌ should be range(len(a) - 1 - i)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
try:
    bad([3, 1, 2])
except IndexError as e:
    print(e)  # Output: list index out of range

# ✅ Correct: inner range(n - 1 - i)
```

---

## 🎯 Interview Tip (1 line)
Say: "O(n^2) time, O(1) space, stable; with the swapped flag it is O(n) on sorted data — but I'd never use it in production over sorted()."

---

## 🔗 Related Questions
→ Q105 (quick sort) | Q106 (merge sort) | Q113 (sorted with key) | Q103 (binary search)
