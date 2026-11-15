---

# D046. Next Greater Element
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #496 (variant: #503 circular)

---

## ❓ Problem
For each element of an array, find the next element to its right that is strictly greater. If none exists, use `-1`.

```
Input:  [4, 5, 2, 25]
Output: [5, 25, 25, -1]
```

---

## 💡 Quick Concept (2 lines only)
Scan right to left with a stack of candidates. Pop everything not greater than the current value; the stack top (if any) is the answer; then push the current value.
हिंदी: दाईं तरफ से चलो, छोटे/बराबर elements pop करो, बचा हुआ top ही next greater है, फिर current को push करो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — scan right for each element
# O(n^2) time, O(1) extra space
# ============================================
def nge_brute(nums: list[int]) -> list[int]:
    res = [-1] * len(nums)                      # default -1
    for i in range(len(nums)):                  # each element
        for j in range(i + 1, len(nums)):       # look to the right
            if nums[j] > nums[i]:               # first greater
                res[i] = nums[j]                # record value
                break                           # stop at the first
    return res                                  # result


# ============================================
# APPROACH 2: Monotonic stack (right to left) — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def next_greater(nums: list[int]) -> list[int]:
    res = [-1] * len(nums)                      # default -1
    stack: list[int] = []                       # candidate greater values
    for i in range(len(nums) - 1, -1, -1):      # right to left
        while stack and stack[-1] <= nums[i]:   # candidates not greater are useless
            stack.pop()                         # discard them
        if stack:                               # a greater element exists
            res[i] = stack[-1]                  # nearest one is on top
        stack.append(nums[i])                   # current is a candidate for the left
    return res                                  # result


# ============================================
# APPROACH 3: Circular array (LeetCode #503) — loop twice
# ============================================
def next_greater_circular(nums: list[int]) -> list[int]:
    n = len(nums)                               # length
    res = [-1] * n                              # default -1
    stack: list[int] = []                       # indices waiting for a greater value
    for i in range(2 * n):                      # pass over the array twice
        while stack and nums[stack[-1]] < nums[i % n]:  # current resolves waiting ones
            res[stack.pop()] = nums[i % n]      # set their answer
        if i < n:                               # only push in the first pass
            stack.append(i)                     # wait for a greater value
    return res                                  # result


# ============================================
# TEST CASES
# ============================================
print(nge_brute([4, 5, 2, 25]))                 # [5, 25, 25, -1]
print(next_greater([4, 5, 2, 25]))              # [5, 25, 25, -1]
print(next_greater([13, 7, 6, 12]))             # [-1, 12, 12, -1]
print(next_greater([3, 3, 3]))                  # [-1, -1, -1]
print(next_greater([]))                         # []
print(next_greater_circular([1, 2, 1]))         # [2, -1, 2]
```

---

## 🔍 Why It Works
```
nums = [4, 5, 2, 25], go right to left
25: stack empty -> -1, push 25        stack [25]
2 : top 25 > 2  -> 25, push 2         stack [25, 2]
5 : pop 2 (<=5), top 25 -> 25, push 5 stack [25, 5]
4 : top 5 > 4   -> 5, push 4
```
हिंदी: जो element current से छोटा है वो बाईं तरफ किसी के काम नहीं आएगा, इसलिए उसे हटाना सुरक्षित है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1) extra
Stack:       Time O(n)   | Space O(n) ← preferred
Circular:    Time O(n)   | Space O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: LeetCode #496 — nums1 is a subset of nums2: build a dict of next-greater for nums2
def nge_subset(nums1: list[int], nums2: list[int]) -> list[int]:
    nxt: dict[int, int] = {}                    # value -> next greater
    stack: list[int] = []                       # values waiting
    for x in nums2:                             # left to right
        while stack and stack[-1] < x:          # x resolves waiting values
            nxt[stack.pop()] = x                # record answer
        stack.append(x)                         # x waits
    return [nxt.get(x, -1) for x in nums1]      # lookup, default -1
print(nge_subset([4, 1, 2], [1, 3, 4, 2]))      # [-1, 3, -1]

# VARIANT 2: Next smaller element — flip the comparison
# VARIANT 3: Previous greater element — scan left to right
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: popping only when stack[-1] < nums[i] (strict) while searching "strictly greater"
#    leaves equal values on the stack -> [3, 3] returns [3, -1] instead of [-1, -1]
# ✅ Correct: pop while stack[-1] <= nums[i] when scanning right to left
```

---

## 🎯 Interview Tip
Say: "A monotonic stack discards candidates that can never be the nearest greater for anything further left, so each element is pushed and popped once — O(n)." Clarify strict vs non-strict and circular.

---

## 🔗 Related Problems
→ D045 (Daily Temperatures) | D048 (Largest Rectangle in Histogram) | D043 (Min Stack)
