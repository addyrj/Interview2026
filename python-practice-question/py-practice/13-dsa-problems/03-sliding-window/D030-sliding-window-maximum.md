
---

# D030. Sliding Window Maximum
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐⭐ Hard | LeetCode #239

---

## ❓ Problem
Given an integer array `nums` and a window size `k`, the window slides one step at a time from the left to the right. Return the maximum of each window.

```
Input:  nums = [1,3,-1,-3,5,3,6,7], k = 3
Output: [3,3,5,5,6,7]
```

---

## 💡 Quick Concept (2 lines only)
Keep a deque of indices whose values are in decreasing order; the front is always the maximum of the current window. Pop smaller values from the back as new numbers arrive, and pop the front when it leaves the window.
हिंदी: Deque में indices रखो (values घटते क्रम में); front हमेशा window का max होता है, बाहर गए index को front से हटा दो।

---

## ✅ Solution

```python
from collections import deque  # double-ended queue with O(1) pops at both ends
import heapq                   # heap for the alternative approach


# ============================================
# APPROACH 1: Brute force — max() of every window
# O(n * k) time, O(1) extra space
# ============================================
def max_sliding_window_brute(nums: list[int], k: int) -> list[int]:
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]  # max of each slice


# ============================================
# APPROACH 2: Monotonic deque — O(n) time, O(k) space  PREFERRED
# ============================================
def max_sliding_window(nums: list[int], k: int) -> list[int]:
    dq: deque[int] = deque()                   # indices, values decreasing front -> back
    result: list[int] = []                     # answers
    for i, x in enumerate(nums):               # process each element
        while dq and nums[dq[-1]] <= x:        # back elements smaller than x are useless
            dq.pop()                           # remove them forever
        dq.append(i)                           # add current index
        if dq[0] <= i - k:                     # front index slid out of the window
            dq.popleft()                       # remove it
        if i >= k - 1:                         # first full window reached
            result.append(nums[dq[0]])         # front is the max
    return result                              # list of window maxima


# ============================================
# APPROACH 3: Max-heap with lazy deletion — O(n log n)
# ============================================
def max_sliding_window_heap(nums: list[int], k: int) -> list[int]:
    heap: list[tuple[int, int]] = []           # (-value, index) because heapq is a min-heap
    result: list[int] = []                     # answers
    for i, x in enumerate(nums):               # process each element
        heapq.heappush(heap, (-x, i))          # push negative value for max behaviour
        while heap[0][1] <= i - k:             # top is outside the window
            heapq.heappop(heap)                # lazily discard it
        if i >= k - 1:                         # window is full
            result.append(-heap[0][0])         # top is the max (undo negation)
    return result                              # list of window maxima


# ============================================
# TEST CASES
# ============================================
for fn in (max_sliding_window_brute, max_sliding_window, max_sliding_window_heap):  # all approaches
    print(fn([1, 3, -1, -3, 5, 3, 6, 7], 3))  # [3, 3, 5, 5, 6, 7]
    print(fn([1], 1))                         # [1]
    print(fn([9, 11], 2))                     # [11]
    print(fn([4, 3, 2, 1], 2))                # [4, 3, 2]
    print(fn([1, -1], 1))                     # [1, -1]
```

---

## 🔍 Why It Works
```
nums = [1,3,-1,-3,5,3,6,7], k = 3 (deque shows values)
i=0: [1]          i=1: 3 kills 1 -> [3]        i=2: [3,-1]   -> out 3
i=3: [3,-1,-3]    -> out 3 (still in window)   i=4: 5 kills all -> [5] -> out 5
A smaller value behind a bigger one can never be a max again,
because the bigger one leaves the window later.
```
हिंदी: जो छोटा element किसी बड़े के पीछे आए वो कभी max नहीं बन सकता, इसलिए उसे deque से हटा देते हैं।

---

## 📊 Complexity
```
Brute force: Time O(n*k)     | Space O(1)
Heap:        Time O(n log n) | Space O(n)
Deque:       Time O(n)       | Space O(k)  <- preferred (each index pushed/popped once)
```

---

## ⚡ Variations

```python
# VARIANT 1: Sliding window minimum — flip the comparison to >= when popping
# VARIANT 2: Return indices of the maximums — append dq[0] instead of nums[dq[0]]
# VARIANT 3: Max of sums/ranges (e.g. constrained subsequence sum) — same deque over dp values
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: storing values in the deque instead of indices
#    you cannot tell when the front value has left the window
# ❌ Wrong: using < instead of <= when popping the back
#    still correct, but keeps duplicates and wastes space
# ✅ Correct: store indices, pop smaller from back, pop front if index <= i - k
```

---

## 🎯 Interview Tip
Say: "A monotonic decreasing deque of indices: front is the window max. Each index enters and leaves once, so it is O(n)." Mention the heap solution first as an easier O(n log n) fallback.

---

## 🔗 Related Problems
→ D024 (Max Sum Subarray of Size K) | D014 (Trapping Rain Water) | D045 (Daily Temperatures)
