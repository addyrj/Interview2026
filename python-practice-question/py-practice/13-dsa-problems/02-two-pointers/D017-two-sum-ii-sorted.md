---

# D017. Two Sum II (sorted)
# Category: DSA — Two Pointers
# Difficulty: ⭐ Easy | LeetCode #167

---

## ❓ Problem
Given a **1-indexed sorted** array `numbers` and a `target`, return the 1-based indices `[i, j]` (i < j) of the two numbers that add up to `target`. Exactly one solution exists. Use O(1) extra space.

```
Input:  numbers = [2, 7, 11, 15], target = 9
Output: [1, 2]
```

---

## 💡 Quick Concept (2 lines only)
Because the array is sorted, start with pointers at both ends. If the sum is too big move the right pointer left; if too small move the left pointer right.
हिंदी: Array sorted है, इसलिए दोनों सिरों से शुरू करो; sum बड़ा हो तो right घटाओ, छोटा हो तो left बढ़ाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — check every pair
# O(n^2) time, O(1) space
# ============================================
def two_sum_brute(numbers: list[int], target: int) -> list[int]:
    n = len(numbers)  # array length
    for i in range(n):  # first element
        for j in range(i + 1, n):  # second element after it
            if numbers[i] + numbers[j] == target:  # found the pair
                return [i + 1, j + 1]  # convert to 1-based indices
    return []  # no answer (never happens per problem)

# ============================================
# APPROACH 2: Two pointers — O(n) time, O(1) space ✅ PREFERRED
# ============================================
def two_sum(numbers: list[int], target: int) -> list[int]:
    l, r = 0, len(numbers) - 1  # pointers at both ends
    while l < r:  # until they meet
        s = numbers[l] + numbers[r]  # current sum
        if s == target:  # found the pair
            return [l + 1, r + 1]  # 1-based indices
        if s < target:  # sum too small
            l += 1  # need a bigger left value
        else:  # sum too big
            r -= 1  # need a smaller right value
    return []  # no answer (never happens per problem)

# ============================================
# TEST CASES
# ============================================
print(two_sum_brute([2, 7, 11, 15], 9))  # [1, 2]
print(two_sum([2, 7, 11, 15], 9))  # [1, 2]
print(two_sum([2, 3, 4], 6))  # [1, 3]
print(two_sum([-1, 0], -1))  # [1, 2]
print(two_sum([1, 2, 3, 4, 4, 9, 56, 90], 8))  # [4, 5]
print(two_sum([5, 25, 75], 100))  # [2, 3]
```

---

## 🔍 Why It Works
```
[2, 7, 11, 15], target 9
l=0,r=3: 2+15=17 > 9 -> r--
l=0,r=2: 2+11=13 > 9 -> r--
l=0,r=1: 2+7 = 9 -> answer [1, 2]
```
हिंदी: Sorted होने से हर कदम पर एक pointer हटाना safe है, क्योंकि उस element के साथ कोई सही pair बन ही नहीं सकता।

---

## 📊 Complexity
```
Brute force:  Time O(n^2)   | Space O(1)
Two pointers: Time O(n)     | Space O(1) ← preferred
Binary search per element: Time O(n log n) | Space O(1)
```

---

## ⚡ Variations

```python
# VARIANT 1: Binary search for the complement — O(n log n)
from bisect import bisect_left  # binary search helper

def two_sum_bisect(numbers: list[int], target: int) -> list[int]:
    for i, x in enumerate(numbers):  # fix first number
        j = bisect_left(numbers, target - x, i + 1)  # search complement after i
        if j < len(numbers) and numbers[j] == target - x:  # complement exists
            return [i + 1, j + 1]  # 1-based indices
    return []  # no answer

print(two_sum_bisect([2, 7, 11, 15], 9))  # [1, 2]
print(two_sum_bisect([5, 25, 75], 100))  # [2, 3]
# VARIANT 2: Unsorted input -> hash map one pass (D001 Two Sum)
# VARIANT 3: Count all pairs with the given sum (skip duplicates carefully)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: returning 0-based indices
return [l, r]

# ❌ Wrong: using a hash map -> works but breaks the O(1) space requirement

# ✅ Correct: two pointers and return [l + 1, r + 1]
```

---

## 🎯 Interview Tip
Say: "Sorted input is the hint for two pointers. Each step discards one element, so it's O(n) time and O(1) space; a hash map would use extra space."

---

## 🔗 Related Problems
→ D001 (Two Sum) | D018 (3Sum) | D019 (Container With Most Water)
