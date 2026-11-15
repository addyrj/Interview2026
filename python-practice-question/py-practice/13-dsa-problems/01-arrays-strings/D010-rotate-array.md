---

# D010. Rotate Array
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #189

---

## ❓ Problem
Rotate an array to the right by `k` steps, **in place** (modify `nums`, return nothing). `k` may be larger than the length.

```
Input:  nums = [1,2,3,4,5,6,7], k = 3
Output: [5,6,7,1,2,3,4]
```

---

## 💡 Quick Concept (2 lines only)
Rotating right by k = move the last k items to the front. First do `k %= n`. Three reversals (whole, first k, rest) do it in O(1) extra space.
हिंदी: पहले `k %= n`; फिर पूरा array reverse, फिर पहले k reverse, फिर बाकी reverse — in-place rotation हो जाता है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — rotate one step at a time
# O(n * k) time, O(1) space
# ============================================
def rotate_brute(nums: list[int], k: int) -> None:
    n = len(nums)                                        # length
    if n == 0:                                           # nothing to rotate
        return                                           # done
    for _ in range(k % n):                               # repeat k (mod n) single steps
        last = nums.pop()                                # take the last item
        nums.insert(0, last)                             # put it in front (O(n))


# ============================================
# APPROACH 2: Extra array — place each item at (i + k) % n
# O(n) time, O(n) space
# ============================================
def rotate_extra(nums: list[int], k: int) -> None:
    n = len(nums)                                        # length
    if n == 0:                                           # empty list
        return                                           # nothing to do
    copy = nums[:]                                       # snapshot of original
    for i in range(n):                                   # each original index
        nums[(i + k) % n] = copy[i]                      # lands k places later (wraps around)


# ============================================
# APPROACH 3: Three reversals ✅ PREFERRED
# O(n) time, O(1) extra space
# ============================================
def _reverse(a: list[int], lo: int, hi: int) -> None:
    while lo < hi:                                       # until pointers meet
        a[lo], a[hi] = a[hi], a[lo]                      # swap ends
        lo += 1                                          # move left pointer in
        hi -= 1                                          # move right pointer in


def rotate(nums: list[int], k: int) -> None:
    n = len(nums)                                        # length
    if n == 0:                                           # empty list
        return                                           # nothing to do
    k %= n                                               # k can exceed n
    _reverse(nums, 0, n - 1)                             # [7,6,5,4,3,2,1]
    _reverse(nums, 0, k - 1)                             # [5,6,7,4,3,2,1]
    _reverse(nums, k, n - 1)                             # [5,6,7,1,2,3,4]


# ============================================
# TEST CASES
# ============================================
for fn in (rotate_brute, rotate_extra, rotate):          # same tests for every approach
    a = [1, 2, 3, 4, 5, 6, 7]                            # fresh input
    fn(a, 3)                                             # rotate right by 3
    print(fn.__name__, a)                                # [5, 6, 7, 1, 2, 3, 4]

b = [-1, -100, 3, 99]
rotate(b, 2)
print(b)                                                 # [3, 99, -1, -100]
c = [1, 2]
rotate(c, 5)                                             # k > n -> k % n == 1
print(c)                                                 # [2, 1]
d: list[int] = []
rotate(d, 3)
print(d)                                                 # []
e = [1, 2, 3]
rotate(e, 0)
print(e)                                                 # [1, 2, 3]
```

---

## 🔍 Why It Works
```
[1,2,3,4,5,6,7], k=3
reverse all      -> [7,6,5,4,3,2,1]
reverse first 3  -> [5,6,7,4,3,2,1]
reverse last 4   -> [5,6,7,1,2,3,4]
```
हिंदी: पूरा reverse करने से last k items आगे आ जाते हैं (उल्टे क्रम में); फिर दोनों हिस्सों को अलग-अलग सीधा कर दो।

---

## 📊 Complexity
```
Brute force:     Time O(n*k) | Space O(1)
Extra array:     Time O(n)   | Space O(n)
Three reversals: Time O(n)   | Space O(1)  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Pythonic slice assignment (in place, but builds temporaries -> O(n) space)
def rotate_slice(nums: list[int], k: int) -> None:
    if nums:                                             # avoid % 0
        k %= len(nums)                                   # normalise k
        nums[:] = nums[-k:] + nums[:-k] if k else nums   # `[:]=` keeps the SAME list object

x = [1, 2, 3, 4, 5, 6, 7]
rotate_slice(x, 3)
print(x)                                                 # [5, 6, 7, 1, 2, 3, 4]

# VARIANT 2: Rotate LEFT by k -> rotate right by n - k
# VARIANT 3: collections.deque.rotate(k) does a right rotation for you
from collections import deque                            # double-ended queue
dq = deque([1, 2, 3, 4, 5, 6, 7])
dq.rotate(3)                                             # positive = right
print(list(dq))                                          # [5, 6, 7, 1, 2, 3, 4]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: nums = nums[-k:] + nums[:-k]  -> rebinds a LOCAL name, caller's list is unchanged
def bad(nums: list[int], k: int) -> None:
    nums = nums[-k:] + nums[:-k]                         # does not modify the original

orig = [1, 2, 3]
bad(orig, 1)
print(orig)                                              # [1, 2, 3]  <- not rotated

# ❌ Wrong: forgetting k %= n  (k=5 on 2 items), or nums[:-0] when k == 0 -> empty list
print([1, 2, 3][:-0])                                    # []

# ✅ Correct: normalise k, and use nums[:] = ... or the 3-reversal method
```

---

## 🎯 Interview Tip
Say: "First `k %= n`. I'll show the O(n)/O(n) copy, then the three-reversal trick for O(1) space." Mention `nums[:] =` vs `nums =` for in-place semantics.

---

## 🔗 Related Problems
→ D011 (Move Zeroes) | D022 (Reverse String) | D085 (Search in Rotated Sorted Array)
