---

# D004. Product of Array Except Self
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #238

---

## ❓ Problem
Given a list `nums`, return a list `answer` where `answer[i]` is the product of all elements of `nums` except `nums[i]`. Do it in O(n) WITHOUT using division.

```
Input:  nums = [1, 2, 3, 4]
Output: [24, 12, 8, 6]
```

---

## 💡 Quick Concept (2 lines only)
`answer[i]` = (product of everything to the left of i) x (product of everything to the right of i). Build the left products in one pass, then multiply by running right products in a second pass.
हिंदी: हर index के लिए बाएँ का product × दाएँ का product — दो passes में, division के बिना।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — multiply all others for each index
# O(n^2) time, O(1) extra space
# ============================================
def product_except_self_brute(nums: list[int]) -> list[int]:
    out: list[int] = []                            # result list
    for i in range(len(nums)):                     # for each index
        prod = 1                                   # running product
        for j in range(len(nums)):                 # all other elements
            if j != i:                             # skip itself
                prod *= nums[j]                    # multiply
        out.append(prod)                           # store
    return out                                     # result

# ============================================
# APPROACH 2: Prefix and suffix products ✅ PREFERRED
# O(n) time, O(1) extra space (output list not counted)
# ============================================
def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)                                  # length
    out = [1] * n                                  # out[i] will hold left product first
    left = 1                                       # product of elements left of i
    for i in range(n):                             # left-to-right pass
        out[i] = left                              # store product of everything left
        left *= nums[i]                            # include nums[i] for next index
    right = 1                                      # product of elements right of i
    for i in range(n - 1, -1, -1):                 # right-to-left pass
        out[i] *= right                            # multiply by everything right
        right *= nums[i]                           # include nums[i] for next index
    return out                                     # result

# ============================================
# TEST CASES
# ============================================
print(product_except_self_brute([1, 2, 3, 4]))     # [24, 12, 8, 6]
print(product_except_self([1, 2, 3, 4]))           # [24, 12, 8, 6]
print(product_except_self([-1, 1, 0, -3, 3]))      # [0, 0, 9, 0, 0]  (one zero)
print(product_except_self([0, 0, 2]))              # [0, 0, 0]        (two zeros)
print(product_except_self([5]))                    # [1]              (empty product)
print(product_except_self([2, 3]))                 # [3, 2]
```

---

## 🔍 Why It Works
```
nums  = [1,  2,  3,  4]
left  = [1,  1,  2,  6]    (product before i)
right = [24, 12, 4,  1]    (product after i)
ans   = [24, 12, 8,  6]
```
हिंदी: Left pass में prefix products, right pass में suffix products multiply — zero भी सही handle होता है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Prefix/suffix: Time O(n) | Space O(1) extra  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: With division (fails with zeros unless handled)
def with_division(nums: list[int]) -> list[int]:
    total = 1                                      # product of non-zero values
    zeros = nums.count(0)                          # how many zeros
    for n in nums:                                 # compute product ignoring zeros
        if n != 0:                                 # skip zero
            total *= n                             # multiply
    if zeros > 1:                                  # two zeros -> everything is 0
        return [0] * len(nums)                     # all zeros
    if zeros == 1:                                 # one zero -> only that slot is non-zero
        return [total if n == 0 else 0 for n in nums]  # fill accordingly
    return [total // n for n in nums]              # no zeros -> safe to divide

print(with_division([1, 2, 3, 4]))                 # [24, 12, 8, 6]
print(with_division([-1, 1, 0, -3, 3]))            # [0, 0, 9, 0, 0]

# VARIANT 2: itertools.accumulate for prefix/suffix
from itertools import accumulate                   # running products
import operator                                    # operator.mul
def with_accumulate(nums: list[int]) -> list[int]:
    pre = [1] + list(accumulate(nums[:-1], operator.mul))              # left products
    suf = list(accumulate(reversed(nums[1:]), operator.mul))[::-1] + [1]  # right products
    return [a * b for a, b in zip(pre, suf)]       # combine

print(with_accumulate([1, 2, 3, 4]))               # [24, 12, 8, 6]

# VARIANT 3: Sum of array except self -> total - nums[i] (trivial, O(n))
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: dividing total product by nums[i] crashes when a zero is present
nums = [1, 0, 3]                                   # contains a zero
total = 1                                          # product accumulator
for n in nums:                                     # multiply everything
    total *= n                                     # becomes 0
try:                                               # naive division
    print([total // n for n in nums])              # divides by zero at index 1
except ZeroDivisionError as e:                     # error caught
    print("ZeroDivisionError:", e)                 # integer division or modulo by zero

# ✅ Correct: prefix/suffix products need no division (see product_except_self)
```

---

## 🎯 Interview Tip
State the constraint ("no division") then explain left x right products. Say the output list does not count as extra space, so the two-pass version is O(1) extra. Mention zero handling comes for free.

---

## 🔗 Related Problems
→ D005 (Maximum Subarray) | D014 (Trapping Rain Water) | D001 (Two Sum)
