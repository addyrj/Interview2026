---

# D015. Longest Consecutive Sequence
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #128

---

## ❓ Problem
Given an unsorted array of integers, return the length of the longest run of consecutive numbers (e.g. 3,4,5,6). Must run in O(n) time.

```
Input:  nums = [100, 4, 200, 1, 3, 2]
Output: 4          # 1, 2, 3, 4
```

---

## 💡 Quick Concept (2 lines only)
Put all numbers in a set. Only start counting from a number whose predecessor (`n - 1`) is NOT in the set — that is the start of a run — then walk upward.
हिंदी: सारे numbers set में डालो; सिर्फ वहीं से गिनना शुरू करो जहाँ n-1 set में नहीं है, फिर n+1, n+2… देखते जाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — sort, then scan runs
# O(n log n) time, O(n) space
# ============================================
def longest_consecutive_sort(nums: list[int]) -> int:
    if not nums:  # empty input
        return 0  # no sequence
    arr = sorted(set(nums))  # sort unique values
    best = cur = 1  # best run and current run length
    for i in range(1, len(arr)):  # compare each value with previous
        if arr[i] == arr[i - 1] + 1:  # consecutive
            cur += 1  # extend current run
        else:  # gap found
            cur = 1  # restart run
        best = max(best, cur)  # remember the longest
    return best  # longest run length

# ============================================
# APPROACH 2: Hash set, start only at run beginnings — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def longest_consecutive(nums: list[int]) -> int:
    values = set(nums)  # O(1) membership checks, removes duplicates
    best = 0  # longest run found
    for n in values:  # iterate unique numbers
        if n - 1 not in values:  # n is the start of a run
            length = 1  # run contains n itself
            while n + length in values:  # keep walking upward
                length += 1  # extend run
            best = max(best, length)  # update answer
    return best  # longest run length

# ============================================
# TEST CASES
# ============================================
print(longest_consecutive_sort([100, 4, 200, 1, 3, 2]))  # 4
print(longest_consecutive([100, 4, 200, 1, 3, 2]))  # 4
print(longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))  # 9
print(longest_consecutive([]))  # 0
print(longest_consecutive([5]))  # 1
print(longest_consecutive([1, 2, 0, 1]))  # 3
print(longest_consecutive([-1, -2, -3, 10]))  # 3
```

---

## 🔍 Why It Works
```
nums = [100, 4, 200, 1, 3, 2]
100: 99 not in set  -> start, run 1
4:   3 in set       -> skip (not a start)
1:   0 not in set   -> start: 1,2,3,4 -> length 4
Each number is visited at most twice -> O(n)
```
हिंदी: हर run सिर्फ अपनी शुरुआत से एक बार चलता है, इसलिए हर number ज़्यादा से ज़्यादा दो बार छुआ जाता है → O(n)।

---

## 📊 Complexity
```
Sorting:  Time O(n log n) | Space O(n)
Hash set: Time O(n)       | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Return the actual sequence, not just its length
def longest_consecutive_seq(nums: list[int]) -> list[int]:
    values = set(nums)  # unique values
    best_start, best_len = 0, 0  # best run so far
    for n in values:  # iterate unique numbers
        if n - 1 not in values:  # only start at beginnings
            length = 1  # current run length
            while n + length in values:  # extend upward
                length += 1  # grow run
            if length > best_len:  # new best
                best_start, best_len = n, length  # remember it
    return list(range(best_start, best_start + best_len))  # rebuild the run

print(longest_consecutive_seq([100, 4, 200, 1, 3, 2]))  # [1, 2, 3, 4]
# VARIANT 2: Union-Find — union n with n+1, answer is the biggest component size
# VARIANT 3: Longest run with allowed gap of 1 (see sliding window problems)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: walking from every number -> O(n^2) on input like [1,2,3,...,n]
for n in nums:
    length = 1
    while n + length in values:   # re-walks the same run from every element
        length += 1

# ❌ Wrong: sorting without removing duplicates -> [1,2,2,3] looks like a break

# ✅ Correct: start only when (n - 1) not in the set
```

---

## 🎯 Interview Tip
Say: "Sorting is O(n log n), but the problem wants O(n), so I use a set and only expand from numbers with no predecessor, so each element is processed a constant number of times."

---

## 🔗 Related Problems
→ D003 (Contains Duplicate) | D001 (Two Sum) | D025 (Longest Substring Without Repeating Characters)
