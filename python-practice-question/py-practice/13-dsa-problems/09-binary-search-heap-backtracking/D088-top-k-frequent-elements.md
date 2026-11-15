---

# D088. Top K Frequent Elements
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐ Medium | LeetCode #347

---

## ❓ Problem
Given an integer array and `k`, return the `k` most frequent elements (any order).

```
Input:  nums = [1, 1, 1, 2, 2, 3], k = 2
Output: [1, 2]
```

---

## 💡 Quick Concept (2 lines only)
Count frequencies with a dict, then pick the top `k` by count: sort (O(n log n)), heap (O(n log k)), or bucket sort by frequency (O(n)).
हिंदी: पहले हर element की frequency गिनो, फिर सबसे ज़्यादा frequency वाले k चुनो: sort, heap या bucket से।

---

## ✅ Solution

```python
import heapq  # heap for top-k selection
from collections import Counter  # frequency counting


# ============================================
# APPROACH 1: Brute force — count, then sort by frequency, O(n log n)
# ============================================
def top_k_sort(nums: list[int], k: int) -> list[int]:
    freq: dict[int, int] = {}  # value -> count
    for x in nums:  # count manually
        freq[x] = freq.get(x, 0) + 1  # increment count
    ordered = sorted(freq, key=lambda v: freq[v], reverse=True)  # most frequent first
    return ordered[:k]  # first k values


# ============================================
# APPROACH 2: Heap — O(n log k) time
# ============================================
def top_k_heap(nums: list[int], k: int) -> list[int]:
    freq = Counter(nums)  # value -> count
    return heapq.nlargest(k, freq.keys(), key=freq.get)  # k keys with the largest counts


# ============================================
# APPROACH 3: Bucket sort — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def top_k_frequent(nums: list[int], k: int) -> list[int]:
    freq = Counter(nums)  # value -> count
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]  # index = frequency
    for value, count in freq.items():  # place each value in its frequency bucket
        buckets[count].append(value)  # same count -> same bucket
    result: list[int] = []  # answer list
    for count in range(len(buckets) - 1, 0, -1):  # from highest frequency downward
        for value in buckets[count]:  # every value with this frequency
            result.append(value)  # take it
            if len(result) == k:  # collected k elements
                return result  # done
    return result  # fewer than k distinct values (not expected by constraints)


# Pythonic one-liner
def top_k_most_common(nums: list[int], k: int) -> list[int]:
    return [v for v, _ in Counter(nums).most_common(k)]  # most_common returns (value, count)


# ============================================
# TEST CASES
# ============================================
print(sorted(top_k_sort([1, 1, 1, 2, 2, 3], 2)))         # [1, 2]
print(sorted(top_k_heap([1, 1, 1, 2, 2, 3], 2)))         # [1, 2]
print(sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)))     # [1, 2]
print(sorted(top_k_most_common([1, 1, 1, 2, 2, 3], 2)))  # [1, 2]
print(top_k_frequent([1], 1))                            # [1]
print(sorted(top_k_frequent([4, 4, 5, 5, 5, 6, 6, 6, 6], 2)))  # [5, 6]
print(top_k_frequent([-1, -1], 1))                       # [-1]
```

---

## 🔍 Why It Works
```
nums = [1,1,1,2,2,3]
freq    = {1:3, 2:2, 3:1}
buckets = [[], [3], [2], [1], [], [], []]   (index = count)
scan from the right: bucket[3] -> 1, bucket[2] -> 2  => [1, 2]
```
हिंदी: Frequency कभी len(nums) से ज़्यादा नहीं हो सकती, इसलिए frequency को index बनाकर bucket में रखो और पीछे से k elements उठा लो।

---

## 📊 Complexity
```
Sort:   Time O(n log n) | Space O(n)
Heap:   Time O(n log k) | Space O(n)
Bucket: Time O(n)       | Space O(n)   ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Top K frequent words (LeetCode 692) — ties broken alphabetically, sort key (-count, word)
# VARIANT 2: Sort characters by frequency — same count + build the string
# VARIANT 3: Streaming top-k — Counter + heap, or Count-Min Sketch for huge streams
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: sorting dict items by key instead of by count
# sorted(freq)[:k]            # sorts by value of the number, not frequency

# ❌ Wrong: Counter.most_common() with no argument then slicing sorts everything (fine, but O(n log n))

# ✅ Correct: sort/heap/bucket on the COUNT, return the keys
```

---

## 🎯 Interview Tip
Say: "Count with a hash map, then bucket by frequency since count is at most n — that beats O(n log n). A size-k heap is the fallback if memory for buckets matters." Mention `Counter.most_common`.

---

## 🔗 Related Problems
→ D087 (Kth Largest Element) | D089 (Merge K Sorted Lists) | D090 (Subsets)
