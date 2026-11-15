---

# 462. Binary Search
# हिंदी में: Binary Search (आधा-आधा करके खोजना)

Full runnable solution (iterative, recursive, lower bound, tests against `bisect`): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Binary search finds a value in a sorted list by checking the middle item and throwing away half of the list each time. It takes O(log n) time instead of O(n).

## 🔵 सरल परिभाषा (Hindi)
Binary search sorted list में value खोजता है: बीच का item देखो और हर बार आधी list छोड़ दो। Time O(log n) लगता है, O(n) नहीं।

---

## 🔴 Problem it Solves
A linear scan over 10 million sorted IDs needs up to 10 million checks. Binary search needs about 24. Sorted data is common (indexes, timestamps, prices), so this saves huge time.

## 🔴 यह क्यों बना? (Hindi)
1 करोड़ sorted IDs में linear scan में 1 करोड़ तक checks लगते हैं। Binary search में करीब 24। Sorted data हर जगह है (index, timestamp, price), इसलिए बहुत समय बचता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → lo = 0, hi = len - 1 (window is inclusive)
Step 2 → mid = lo + (hi - lo) // 2
Step 3 → nums[mid] == target → return mid
Step 4 → nums[mid] < target → lo = mid + 1 (search right)
Step 5 → nums[mid] > target → hi = mid - 1 (search left)
Step 6 → lo > hi → not found, return -1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → lo = 0, hi = len - 1
Step 2 → mid निकालो
Step 3 → बराबर मिले तो index लौटाओ
Step 4 → mid का item छोटा हो तो दाईं तरफ खोजो (lo = mid + 1)
Step 5 → mid का item बड़ा हो तो बाईं तरफ खोजो (hi = mid - 1)
Step 6 → lo > hi हो जाए तो नहीं मिला, -1
```

---

## 🟡 Real World Example
A Zomato price filter: restaurants are sorted by price and the app finds the first restaurant above 500 rupees with `bisect`. Databases use the same idea inside B-tree indexes. `git bisect` uses it to find the commit that introduced a bug.

## 🟡 Real Example Hindi mein
Zomato के price filter में restaurants price से sorted हैं और app `bisect` से 500 रुपये से ऊपर वाला पहला restaurant खोजता है। Database के B-tree index में भी यही idea है। `git bisect` इसी से बग वाला commit ढूँढता है।

---

## 💻 Code Example — Basic
```python
# Basic iterative binary search
def binary_search(nums: list[int], target: int) -> int:  # nums must be sorted
    lo: int = 0  # left edge of the window
    hi: int = len(nums) - 1  # right edge (inclusive)
    while lo <= hi:  # window still has items
        mid: int = lo + (hi - lo) // 2  # middle index
        if nums[mid] == target:  # found it
            return mid  # return the index
        if nums[mid] < target:  # target is on the right
            lo = mid + 1  # drop the left half
        else:  # target is on the left
            hi = mid - 1  # drop the right half
    return -1  # window is empty, not found


data: list[int] = [1, 3, 5, 7, 9, 11]  # sorted input
print(binary_search(data, 7))  # present
# Output: 3
print(binary_search(data, 4))  # absent
# Output: -1
print(binary_search([], 1))  # empty list
# Output: -1
```

## 💻 Code Example — Advanced
```python
# Production style: insertion points, first/last occurrence, bisect module
from bisect import bisect_left, bisect_right  # stdlib binary search
from typing import List  # type hints


def lower_bound(nums: List[int], target: int) -> int:
    """First index i with nums[i] >= target (also the insert position)."""
    lo, hi = 0, len(nums)  # half-open window [lo, hi)
    while lo < hi:  # until empty
        mid = (lo + hi) // 2  # middle
        if nums[mid] < target:  # too small
            lo = mid + 1  # go right
        else:  # mid could be the answer
            hi = mid  # keep it in the window
    return lo  # insertion point


def count_of(nums: List[int], target: int) -> int:
    """How many times target appears, in O(log n)."""
    return bisect_right(nums, target) - bisect_left(nums, target)  # right edge - left edge


data: List[int] = [1, 2, 2, 2, 3, 5]  # duplicates are fine
print(lower_bound(data, 2), bisect_left(data, 2))  # first 2
# Output: 1 1
print(bisect_right(data, 2))  # one past the last 2
# Output: 4
print(count_of(data, 2), count_of(data, 4))  # counts
# Output: 3 0
print(lower_bound(data, 4))  # where 4 would be inserted
# Output: 5
print(bisect_left(data, 3, lo=0, hi=3))  # restrict the search window
# Output: 3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: bisect is built in
from bisect import bisect_left
i = bisect_left(nums, target)
found = i < len(nums) and nums[i] == target
```

```javascript
// JavaScript: no built-in, write it yourself
function lowerBound(nums, target) {
  let lo = 0, hi = nums.length;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);   // Math.floor needed, / gives a float
    if (nums[mid] < target) lo = mid + 1; else hi = mid;
  }
  return lo;
}
```

Key difference: in Python use `//` for integer division. Python integers never overflow, so `(lo + hi) // 2` is safe, but `lo + (hi - lo) // 2` is a good habit for interviews in C/Java.

---

## 🟠 FastAPI Connection
Look up a price tier or rate-limit bucket from sorted thresholds with `bisect`.

```python
# FastAPI: tier lookup with bisect (pip install fastapi)
from bisect import bisect_right  # binary search
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app
LIMITS: list[int] = [1000, 5000, 20000]  # sorted spend thresholds
TIERS: list[str] = ["bronze", "silver", "gold", "platinum"]  # one more than limits


@app.get("/tier/{spend}")  # GET /tier/7000
def tier(spend: int) -> dict[str, str]:
    return {"tier": TIERS[bisect_right(LIMITS, spend)]}  # 7000 -> index 2 -> "gold"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using it on unsorted data
```python
# Wrong - result is meaningless:
print(binary_search([5, 1, 4], 4))   # can return -1 even though 4 exists

# Correct - sort first (O(n log n)) or use a different method
```

❌ Mistake 2: Infinite loop from bad bounds
```python
# Wrong - lo = mid never moves when lo + 1 == hi:
# lo = mid

# Correct - lo = mid + 1 and hi = mid - 1 (closed window)
```

❌ Mistake 3: `while lo < hi` with `hi = len - 1`
```python
# Wrong - misses a window with one item (lo == hi)
# Correct - use lo <= hi with closed window, or lo < hi with hi = len(nums)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from bisect import bisect_left, bisect_right

a = [1, 2, 2, 2, 3]
print(bisect_left(a, 2), bisect_right(a, 2))
print(bisect_left(a, 10), bisect_right(a, 0))
print(bisect_left([3, 1, 2], 2))
```

**Answer**:
```
1 4
5 0
2
```
`bisect_left` gives the first insert position, `bisect_right` the one after the last equal item. Missing values give `len(a)` or `0`. The last line is a trap: the list is not sorted, so Python does not raise an error, it just returns a meaningless index.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: O(log n) time. O(1) space for the iterative version, O(log n) stack for the recursive one.

Q2: Why `mid = lo + (hi - lo) // 2`?
A2: In fixed-size integer languages `lo + hi` can overflow. In Python it cannot, but it shows you know the risk.

Q3: How do you find the first occurrence of a duplicate?
A3: Use `lower_bound` / `bisect_left`, then check `nums[i] == target`.

Q4: What does binary search need from the data?
A4: Sorted order and O(1) random access (arrays, not linked lists).

Q5: Can you binary search on an answer, not an array?
A5: Yes. If a yes/no check is monotonic (for example "can we ship in D days with capacity X?"), search on X.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Data is sorted and you have random access
- You need insert position, ranges or counts
- You search a monotonic condition (binary search on the answer)

❌ Avoid when:
- Data is unsorted and searched only once (a linear scan is cheaper than sorting)
- Data is small (a plain `in` check is fine)
- You use a dict or set (hash lookup is O(1))

---

## 📊 Visual Diagram

```
nums = [1, 3, 5, 7, 9, 11]   target = 9

lo=0 hi=5 mid=2 -> 5 < 9   lo=3
lo=3 hi=5 mid=4 -> 9 == 9  FOUND at index 4

[1  3  5 | 7  9  11]   first half thrown away
          lo    hi
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sorted | Items in order | क्रम में लगा हुआ |
| Window | Range still being searched | खोज की सीमा |
| Lower bound | First index >= target | पहला index जो target से बड़ा या बराबर |
| Logarithmic | Halves the work each step | हर step पर आधा काम |
| bisect | Stdlib binary search module | Python का built-in module |

---

## ⚡ 3-Line Summary
English: Binary search halves a sorted list each step, so it needs O(log n) time. Use `lo <= hi` with `mid + 1` / `mid - 1`, or the `bisect` module. It fails on unsorted data.
Hindi: Binary search हर step में sorted list आधी कर देता है, इसलिए O(log n)। `lo <= hi` के साथ `mid + 1` / `mid - 1` इस्तेमाल करो या `bisect` module। Unsorted data पर यह गलत चलता है।

---

## ➡️ Next Topic
**463. Bubble Sort** — the simplest sorting algorithm, to learn why O(n^2) is slow.
