---

# D011. Move Zeroes
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #283

---

## ❓ Problem
Move all `0`s in `nums` to the end while keeping the relative order of the non-zero elements. Do it in place.

```
Input:  nums = [0,1,0,3,12]
Output: [1,3,12,0,0]
```

---

## 💡 Quick Concept (2 lines only)
Keep a write pointer `w` for the next spot of a non-zero value. Scan with a read pointer; copy each non-zero to `w` (swapping keeps zeros behind).
हिंदी: एक pointer पर non-zero values लिखते जाओ, बाकी जगह zero भर दो — order भी बना रहता है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — extra list
# O(n) time, O(n) space (not in place)
# ============================================
def move_zeroes_extra(nums: list[int]) -> None:
    non_zero = [x for x in nums if x != 0]               # keep order of non-zeros
    zeros = [0] * (len(nums) - len(non_zero))            # as many zeros as were removed
    nums[:] = non_zero + zeros                           # overwrite the same list object


# ============================================
# APPROACH 2: Two pointers, overwrite then fill zeros
# O(n) time, O(1) space
# ============================================
def move_zeroes_fill(nums: list[int]) -> None:
    w = 0                                                # next slot for a non-zero value
    for x in nums:                                       # read pointer
        if x != 0:                                       # keep this value
            nums[w] = x                                  # write it forward
            w += 1                                       # advance write slot
    for i in range(w, len(nums)):                        # everything after w
        nums[i] = 0                                      # becomes zero


# ============================================
# APPROACH 3: Two pointers with swap ✅ PREFERRED (single pass, minimal writes when few zeros)
# O(n) time, O(1) space
# ============================================
def move_zeroes(nums: list[int]) -> None:
    w = 0                                                # boundary: nums[:w] are non-zeros
    for r in range(len(nums)):                           # read pointer
        if nums[r] != 0:                                 # found a non-zero
            nums[w], nums[r] = nums[r], nums[w]          # swap it into the boundary
            w += 1                                       # grow the non-zero region


# ============================================
# TEST CASES
# ============================================
for fn in (move_zeroes_extra, move_zeroes_fill, move_zeroes):  # every approach
    a = [0, 1, 0, 3, 12]                                 # fresh input
    fn(a)                                                # run it
    print(fn.__name__, a)                                # [1, 3, 12, 0, 0]

b = [0]
move_zeroes(b)
print(b)                                                 # [0]
c = [1, 2, 3]
move_zeroes(c)
print(c)                                                 # [1, 2, 3]
d = [0, 0, 1]
move_zeroes(d)
print(d)                                                 # [1, 0, 0]
e: list[int] = []
move_zeroes(e)
print(e)                                                 # []
```

---

## 🔍 Why It Works
```
[0,1,0,3,12]   w=0
r=0: 0 skip
r=1: 1 -> swap(w=0,r=1) -> [1,0,0,3,12] w=1
r=2: 0 skip
r=3: 3 -> swap(w=1,r=3) -> [1,3,0,0,12] w=2
r=4: 12 -> swap(w=2,r=4) -> [1,3,12,0,0] w=3
```
हिंदी: `w` के पहले की सारी जगह non-zero values की है; हर non-zero मिलने पर उसे `w` से swap करो, zeros अपने-आप पीछे चले जाते हैं।

---

## 📊 Complexity
```
Extra list:    Time O(n) | Space O(n)
Overwrite+fill:Time O(n) | Space O(1)
Swap pointers: Time O(n) | Space O(1)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Move zeroes to the FRONT -> iterate from the right
def zeroes_front(nums: list[int]) -> None:
    w = len(nums) - 1                                    # next slot from the right
    for r in range(len(nums) - 1, -1, -1):               # scan right to left
        if nums[r] != 0:                                 # non-zero found
            nums[w], nums[r] = nums[r], nums[w]          # swap to the right boundary
            w -= 1                                       # shrink toward the left

x = [0, 1, 0, 3, 12]
zeroes_front(x)
print(x)                                                 # [0, 0, 1, 3, 12]

# VARIANT 2: Move a given value `val` to the end (generalised)
# VARIANT 3: Remove element in place (LeetCode #27) -> same write pointer, return w
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: removing items while iterating skips elements
nums = [0, 0, 1]
for x in nums:                                           # mutating the list we iterate
    if x == 0:
        nums.remove(x)
print(nums)                                              # [0, 1]  <- a zero is left behind

# ❌ Wrong: nums = sorted(nums, key=lambda x: x == 0) -> works (stable) but rebinds, not in place

# ✅ Correct: two pointers, or nums[:] = ... to keep the same list object
```

---

## 🎯 Interview Tip
Say: "One pass with a write pointer, O(1) space, order of non-zeros preserved." Mention the swap version does fewer writes when the array has few zeros.

---

## 🔗 Related Problems
→ D020 (Remove Duplicates from Sorted Array) | D021 (Sort Colors) | D010 (Rotate Array)
