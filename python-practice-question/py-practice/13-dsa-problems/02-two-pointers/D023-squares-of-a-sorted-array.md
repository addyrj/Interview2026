---

# D023. Squares of a Sorted Array
# Category: DSA — Two Pointers
# Difficulty: ⭐ Easy | LeetCode #977

---

## ❓ Problem
Given an integer array sorted in non-decreasing order (may contain negatives), return an array of the squares of each number, also sorted in non-decreasing order.

```
Input:  nums = [-4,-1,0,3,10]
Output: [0,1,9,16,100]
```

---

## 💡 Quick Concept (2 lines only)
The largest square is at one of the two ends (a big negative or a big positive). Use two pointers at the ends and fill the result from the back with the larger square.
हिंदी: सबसे बड़ा square हमेशा किसी एक सिरे पर होता है; दोनों सिरों से compare करो और result को पीछे से भरते जाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — square then sort
# O(n log n) time, O(n) space
# ============================================
def sorted_squares_brute(nums: list[int]) -> list[int]:
    return sorted(x * x for x in nums)                   # square each, then sort


# ============================================
# APPROACH 2: Two pointers, fill from the end ✅ PREFERRED
# O(n) time, O(n) space (output)
# ============================================
def sorted_squares(nums: list[int]) -> list[int]:
    n = len(nums)                                        # length
    out = [0] * n                                        # result placeholder
    left, right = 0, n - 1                               # pointers at both ends
    for pos in range(n - 1, -1, -1):                     # fill from the largest slot down
        if abs(nums[left]) > abs(nums[right]):           # left end has the bigger magnitude
            out[pos] = nums[left] ** 2                   # place its square
            left += 1                                    # consume left
        else:                                            # right end is bigger (or equal)
            out[pos] = nums[right] ** 2                  # place its square
            right -= 1                                   # consume right
    return out                                           # sorted squares


# ============================================
# APPROACH 3: Split at zero and merge two sorted halves
# O(n) time, O(n) space
# ============================================
def sorted_squares_merge(nums: list[int]) -> list[int]:
    neg = [x * x for x in reversed([v for v in nums if v < 0])]  # squares of negatives, ascending
    pos = [x * x for x in nums if x >= 0]                # squares of non-negatives, ascending
    out: list[int] = []                                  # merged result
    i = j = 0                                            # pointers into neg / pos
    while i < len(neg) and j < len(pos):                 # merge step
        if neg[i] <= pos[j]:                             # smaller first
            out.append(neg[i]); i += 1                   # take from neg
        else:
            out.append(pos[j]); j += 1                   # take from pos
    return out + neg[i:] + pos[j:]                       # append leftovers


# ============================================
# TEST CASES
# ============================================
print(sorted_squares_brute([-4, -1, 0, 3, 10]))          # [0, 1, 9, 16, 100]
print(sorted_squares([-4, -1, 0, 3, 10]))                # [0, 1, 9, 16, 100]
print(sorted_squares_merge([-4, -1, 0, 3, 10]))          # [0, 1, 9, 16, 100]
print(sorted_squares([-7, -3, 2, 3, 11]))                # [4, 9, 9, 49, 121]
print(sorted_squares([-5, -4, -3]))                      # [9, 16, 25]  (all negative)
print(sorted_squares([1, 2, 3]))                         # [1, 4, 9]    (all positive)
print(sorted_squares([2]))                               # [4]
print(sorted_squares([]))                                # []
```

---

## 🔍 Why It Works
```
[-4,-1,0,3,10]
pos4: |-4|=4 vs |10|=10 -> 100 ; right moves
pos3: 4 vs 3 -> 16 ; left moves
pos2: |-1|=1 vs 3 -> 9 ; right moves
pos1: 1 vs 0 -> 1 ; left moves
pos0: 0 -> 0
=> [0,1,9,16,100]
```
हिंदी: Negatives के squares बड़े होते हैं, इसलिए सबसे बड़ा square हमेशा किसी end पर मिलता है — बीच वाले छोटे होते हैं।

---

## 📊 Complexity
```
Square + sort: Time O(n log n) | Space O(n)
Two pointers:  Time O(n)       | Space O(n)  ← preferred (output array only)
Split + merge: Time O(n)       | Space O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: heapq.merge on the two already-sorted halves (lazy merge)
import heapq                                             # standard heap utilities

def sorted_squares_heapq(nums: list[int]) -> list[int]:
    neg = [x * x for x in reversed([v for v in nums if v < 0])]  # ascending squares
    pos = [x * x for x in nums if x >= 0]                # ascending squares
    return list(heapq.merge(neg, pos))                   # O(n) merge of sorted iterables

print(sorted_squares_heapq([-4, -1, 0, 3, 10]))          # [0, 1, 9, 16, 100]

# VARIANT 2: Sort by absolute value (key=abs) then square
print([x * x for x in sorted([-4, -1, 0, 3, 10], key=abs)])  # [0, 1, 9, 16, 100]

# VARIANT 3: Closest-to-target sorted arrangement -> same two-pointer idea with |x - target|
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: squaring in place and assuming it is still sorted
nums = [-4, -1, 0, 3, 10]
print([x * x for x in nums])                              # [16, 1, 0, 9, 100]  <- not sorted

# ❌ Wrong: filling the result from the front with two pointers at the ends
#    (you'd be picking the LARGEST first, so the order is reversed)

# ✅ Correct: fill from the back with the larger |value|, or square then sort
```

---

## 🎯 Interview Tip
Say: "Square-then-sort is O(n log n); because the input is sorted I can do O(n) with two pointers from the ends, writing from the back." Mention the min-magnitude-outward alternative.

---

## 🔗 Related Problems
→ D017 (Two Sum II sorted) | D018 (3Sum) | D019 (Container With Most Water)
