---

# Q105. Implement Quick Sort
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `quick_sort(arr)` returning a new sorted list. Handle duplicates correctly and explain average vs worst-case complexity.

```python
quick_sort([3, 6, 8, 10, 1, 2, 1])   # [1, 1, 2, 3, 6, 8, 10]
```

---

## 💡 Quick Concept (2 lines only)
Pick a pivot, split into smaller / equal / larger, recursively sort the outer parts. Average O(n log n), worst O(n^2) with bad pivots.
हिंदी: एक pivot चुनो, छोटे और बड़े elements अलग करो, फिर दोनों हिस्सों को recursively sort करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def quick_sort(arr: list[int]) -> list[int]:  # returns a new sorted list
    if len(arr) <= 1:  # Step 1: base case (0 or 1 item is sorted)
        return arr[:]  # return a copy
    pivot = arr[len(arr) // 2]  # Step 2: middle element as pivot (good on sorted input)
    less = [x for x in arr if x < pivot]  # everything smaller than pivot
    equal = [x for x in arr if x == pivot]  # all copies of pivot (handles duplicates)
    greater = [x for x in arr if x > pivot]  # everything larger than pivot
    return quick_sort(less) + equal + quick_sort(greater)  # Step 3: sort sides, concatenate

# ============================================
# TEST CASES
# ============================================
import random  # for a random stress test
print(quick_sort([3, 6, 8, 10, 1, 2, 1]))  # Expected: [1, 1, 2, 3, 6, 8, 10]
print(quick_sort([]))  # Expected: []
print(quick_sort([5]))  # Expected: [5]
print(quick_sort([2, 2, 2]))  # Expected: [2, 2, 2]
print(quick_sort([5, 4, 3, 2, 1]))  # Expected: [1, 2, 3, 4, 5]
data = random.sample(range(1000), 200)  # 200 random unique numbers
print(quick_sort(data) == sorted(data))  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
After partitioning, every item in `less` is smaller than every item in `greater`, so sorted(less) + equal + sorted(greater) is fully sorted. The `equal` bucket guarantees progress even with many duplicates.
हिंदी: partition के बाद बायाँ हिस्सा हमेशा छोटा और दायाँ बड़ा होता है, इसलिए जोड़ने पर list sorted बनती है।

---

## ⚡ Alternative Solution
```python
# In-place Hoare partition with a random pivot: O(1) extra space, avoids worst case on sorted data
import random  # random pivot

def qs_inplace(a: list[int], lo: int = 0, hi: int | None = None) -> None:
    if hi is None:  # first call
        hi = len(a) - 1  # last index
    if lo >= hi:  # 0 or 1 element
        return  # nothing to do
    p = a[random.randint(lo, hi)]  # random pivot value
    i, j = lo, hi  # two pointers
    while i <= j:  # partition loop
        while a[i] < p: i += 1  # skip small items on the left
        while a[j] > p: j -= 1  # skip large items on the right
        if i <= j:  # both pointers on wrong side
            a[i], a[j] = a[j], a[i]  # swap them
            i += 1; j -= 1  # move inward
    qs_inplace(a, lo, j)  # sort left part
    qs_inplace(a, i, hi)  # sort right part

x = [3, 6, 8, 10, 1, 2, 1]  # sample
qs_inplace(x)  # sort in place
print(x)  # Expected: [1, 1, 2, 3, 6, 8, 10]
y = random.sample(range(1000), 200); z = sorted(y)  # random data + reference
qs_inplace(y)  # sort
print(y == z)  # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only "<" and ">" with the pivot kept once -> duplicates vanish
def bad(arr):
    if len(arr) <= 1: return arr
    p = arr[0]
    return bad([x for x in arr[1:] if x < p]) + [p] + bad([x for x in arr[1:] if x > p])
print(bad([3, 1, 3, 2]))  # Output: [1, 2, 3]  (a 3 is lost!)

# ✅ Correct: use >= on one side (or keep an `equal` bucket)
def good(arr):
    if len(arr) <= 1: return arr
    p = arr[0]
    return good([x for x in arr[1:] if x < p]) + [p] + good([x for x in arr[1:] if x >= p])
print(good([3, 1, 3, 2]))  # Output: [1, 2, 3, 3]
```

---

## 🎯 Interview Tip (1 line)
Say: "Average O(n log n), worst O(n^2) on bad pivots — I use a random/median pivot; recursion can hit Python's limit on adversarial input, so in-place with smaller-side-first helps."

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q106 (merge sort) | Q113 (sorted with key) | Q152 (complete merge sort)
