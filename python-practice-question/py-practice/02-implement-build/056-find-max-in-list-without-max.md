---

# Q056. Find Max in List Without max()
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `find_max(nums: list[int]) -> int` without using the built-in `max()`. Raise `ValueError` for an empty list.

```python
find_max([3, 9, 2, 7])    # 9
find_max([-5, -1, -8])    # -1
```

---

## 💡 Quick Concept (2 lines only)
Start with the first element as the best so far, scan the rest, and replace it whenever you see a larger value. Never start from 0 — negatives would break.
हिंदी: पहला element best मानो, बाकी में बड़ा मिले तो बदल दो — 0 से शुरू मत करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def find_max(nums: list[int]) -> int:
    if not nums:                              # Step 1: guard the empty case
        raise ValueError("find_max() arg is an empty list")  # same idea as built-in max()
    best = nums[0]                            # Step 2: first element is the initial best
    for n in nums[1:]:                        # Step 3: scan the remaining items
        if n > best:                          # found a larger value?
            best = n                          # update the best
    return best                               # Step 4: largest value seen

# ============================================
# TEST CASES
# ============================================
print(find_max([3, 9, 2, 7]))                 # Expected: 9
print(find_max([-5, -1, -8]))                 # Expected: -1
print(find_max([42]))                         # Expected: 42
try:
    find_max([])                              # empty input
except ValueError as e:
    print("ValueError:", e)                   # Expected: ValueError: find_max() arg is an empty list
```

---

## 🔍 Why This Works (3 lines max)
Each element is compared once, giving O(n) time and O(1) space. Seeding with `nums[0]` (not 0 or `-inf` hard-coded) works for all-negative lists and any comparable type.
हिंदी: हर element एक बार compare होता है — O(n) time, O(1) space।

---

## ⚡ Alternative Solution
```python
from functools import reduce                  # fold a list into one value
import heapq                                  # heap helpers

print(reduce(lambda a, b: a if a >= b else b, [3, 9, 2, 7]))  # Output: 9
print(sorted([3, 9, 2, 7])[-1])               # Output: 9  (O(n log n), wasteful)
print(heapq.nlargest(1, [3, 9, 2, 7])[0])     # Output: 9

# With a key function, like max(items, key=...)
def find_max_key(items, key):
    it = iter(items)                          # works for any iterable
    best = next(it)                           # raises StopIteration if empty (guard in real code)
    for x in it:
        if key(x) > key(best):                # compare by key
            best = x
    return best

print(find_max_key(["aa", "b", "cccc"], len)) # Output: cccc
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: starting from 0 breaks all-negative lists
def bad(nums):
    best = 0
    for n in nums:
        if n > best:
            best = n
    return best

print(bad([-5, -1, -8]))                      # Output: 0  (0 is not even in the list!)

# ✅ Correct: start from nums[0] (or float("-inf") for numbers)
print(find_max([-5, -1, -8]))                 # Output: -1
```

---

## 🎯 Interview Tip (1 line)
Say: "Initialize with the first element, handle empty input explicitly, and note it is O(n) — sorting would be needless O(n log n)."

---

## 🔗 Related Questions
→ Q057 (find min) | Q055 (remove duplicates) | Q109 (implement reduce) | Q113 (sorted with key)
