---

# D087. Kth Largest Element (heap)
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #215

---

## ❓ Problem
Given an integer array `nums` and an integer `k`, return the kth largest element (by sorted order, duplicates counted).

```
Input:  nums = [3, 2, 1, 5, 6, 4], k = 2
Output: 5
```

---

## 💡 Quick Concept (2 lines only)
Keep a min-heap of size `k`. After scanning everything, the heap root is the kth largest, because it is the smallest of the k biggest.
हिंदी: Size k का min-heap रखो; सबसे छोटा root हटाते जाओ, अंत में root ही k-th सबसे बड़ा element होता है।

---

## ✅ Solution

```python
import heapq  # built-in binary heap (min-heap)
import random  # for quickselect pivot


# ============================================
# APPROACH 1: Brute force — sort, O(n log n)
# ============================================
def kth_largest_sort(nums: list[int], k: int) -> int:
    return sorted(nums, reverse=True)[k - 1]  # descending order, pick index k-1


# ============================================
# APPROACH 2: Min-heap of size k — O(n log k) time, O(k) space ✅ PREFERRED
# ============================================
def kth_largest(nums: list[int], k: int) -> int:
    heap: list[int] = []  # will hold the k largest seen so far
    for x in nums:  # scan every number
        if len(heap) < k:  # heap not full yet
            heapq.heappush(heap, x)  # just add
        elif x > heap[0]:  # bigger than the smallest of the top-k
            heapq.heapreplace(heap, x)  # pop smallest and push x in one step
    return heap[0]  # root = kth largest


# ============================================
# APPROACH 3: Quickselect — O(n) average, O(n^2) worst
# ============================================
def kth_largest_quickselect(nums: list[int], k: int) -> int:
    target = len(nums) - k  # index of answer in ascending order

    def select(items: list[int], idx: int) -> int:
        pivot = random.choice(items)  # random pivot avoids worst case
        lows = [x for x in items if x < pivot]  # smaller than pivot
        highs = [x for x in items if x > pivot]  # larger than pivot
        equal_count = len(items) - len(lows) - len(highs)  # copies of pivot
        if idx < len(lows):  # answer lies in the lows
            return select(lows, idx)  # recurse left
        if idx < len(lows) + equal_count:  # answer equals the pivot
            return pivot  # found it
        return select(highs, idx - len(lows) - equal_count)  # recurse right

    return select(nums, target)  # start with the whole list


# Pythonic one-liner using the standard library
def kth_largest_nlargest(nums: list[int], k: int) -> int:
    return heapq.nlargest(k, nums)[-1]  # k largest, last one is the kth


# ============================================
# TEST CASES
# ============================================
print(kth_largest_sort([3, 2, 1, 5, 6, 4], 2))                  # 5
print(kth_largest([3, 2, 1, 5, 6, 4], 2))                       # 5
print(kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))              # 4
print(kth_largest_quickselect([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))  # 4
print(kth_largest_nlargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))     # 4
print(kth_largest([1], 1))                                      # 1
print(kth_largest([7, 7, 7], 2))                                # 7
```

---

## 🔍 Why It Works
```
nums = [3,2,1,5,6,4], k = 2
heap: [3] -> [2,3] -> 1 skipped (1 < 2) -> 5 replaces 2: [3,5]
      -> 6 replaces 3: [5,6] -> 4 skipped (4 < 5)
heap[0] = 5  -> 2nd largest
```
हिंदी: Heap में हमेशा अब तक के सबसे बड़े k elements रहते हैं और उनमें सबसे छोटा root पर होता है, वही जवाब है।

---

## 📊 Complexity
```
Sort:        Time O(n log n) | Space O(n)
Min-heap k:  Time O(n log k) | Space O(k)   ← preferred
Quickselect: Time O(n) avg   | Space O(n) here (list comprehensions)
```

---

## ⚡ Variations

```python
# VARIANT 1: Kth smallest — use a max-heap (push negated values) of size k
# VARIANT 2: Streaming kth largest (LeetCode 703) — keep the size-k min-heap alive between adds
# VARIANT 3: Kth largest in a sorted matrix — heap of row heads
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: Python has only a min-heap; a max-heap of ALL items then popping k times is O(n log n)
# ❌ Wrong: de-duplicating with set() -> the problem counts duplicates ([3,2,3,1,2,4,5,5,6], k=4 -> 4)

# ✅ Correct: min-heap capped at size k, answer is heap[0]
```

---

## 🎯 Interview Tip
Say: "Sorting is O(n log n); a size-k min-heap gives O(n log k) and works on streams. Quickselect is O(n) average if they want the optimal." Know both.

---

## 🔗 Related Problems
→ D088 (Top K Frequent Elements) | D089 (Merge K Sorted Lists) | D084 (Binary Search)
