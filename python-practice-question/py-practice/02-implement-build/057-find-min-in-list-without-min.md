---

# Q057. Find Min in List Without min()
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `find_min(nums)` that returns the smallest number in a list **without** using `min()`.
Raise `ValueError` for an empty list (just like `min([])` does).

```python
find_min([4, 2, 9, -1, 7])  # -1
```

---

## 💡 Quick Concept (2 lines only)
Keep a "smallest so far" variable, start it with the FIRST element (not 0), and update it while scanning once. O(n) time, O(1) space.
हिंदी: पहले element से शुरू करो, हर element की तुलना करो और छोटा वाला रखते जाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def find_min(nums: list[float]) -> float:
    if not nums:                                        # Step 1: guard against empty list
        raise ValueError("find_min() arg is an empty list")  # same behaviour as min([])
    smallest = nums[0]                                  # Step 2: start with the first element
    for n in nums[1:]:                                  # Step 3: scan the remaining elements
        if n < smallest:                                # Step 4: found something smaller?
            smallest = n                                # Step 5: update the champion
    return smallest                                     # Step 6: return the final champion

# ============================================
# TEST CASES
# ============================================

print(find_min([4, 2, 9, -1, 7]))   # Expected: -1
print(find_min([5]))                # Expected: 5
print(find_min([3.5, 3.4]))         # Expected: 3.4
try:
    find_min([])                    # empty list -> error
except ValueError as e:
    print(e)                        # Expected: find_min() arg is an empty list
```

---

## 🔍 Why This Works (3 lines max)
`smallest` always holds the minimum of the elements seen so far, so after the last element it is the global minimum. Starting from `nums[0]` (not `0`) makes it work for all-positive lists too.
हिंदी: `smallest` हमेशा अब तक का सबसे छोटा रखता है, इसलिए आखिर में वही answer होता है।

---

## ⚡ Alternative Solution
```python
from functools import reduce  # import reduce for folding the list

nums = [4, 2, 9, -1]                                    # sample data
print(reduce(lambda a, b: a if a < b else b, nums))     # Expected: -1 (fold keeps the smaller one)
print(sorted(nums)[0])                                  # Expected: -1 (works, but O(n log n) - wasteful)

# With a key function, like min(key=...):
def find_min_key(items, key=None):                      # optional key like the built-in
    k = key or (lambda x: x)                            # identity if no key given
    return reduce(lambda a, b: a if k(a) <= k(b) else b, items)  # <= keeps the first on ties

print(find_min_key(["pear", "fig", "apple"], key=len))  # Expected: fig
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: initialising with 0 (or a magic number) - all-positive lists break
def bad(nums):
    smallest = 0                    # 0 is smaller than every positive number!
    for n in nums:
        if n < smallest:
            smallest = n
    return smallest
print(bad([5, 3, 8]))               # 0  <- wrong, 0 is not in the list (verified)

# ✅ Correct: start with nums[0] (or float("inf") / math.inf)
```

---

## 🎯 Interview Tip (1 line)
Say: "Initialise with the first element, handle the empty list explicitly, one pass O(n) - and mention `min()` is the real-world answer."

---

## 🔗 Related Questions
→ Q056 (max) | Q069 (unique values) | Q113 (sorted with key)
