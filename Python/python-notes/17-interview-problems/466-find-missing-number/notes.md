---

# 466. Find Missing Number
# हिंदी में: गायब संख्या खोजना

Full runnable solution (sum, XOR, set, range variant, random tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
You get `n` distinct numbers taken from `0..n`, so exactly one number is missing. Find it. The fastest ways are the Gauss sum formula or XOR, both O(n) time and O(1) space.

## 🔵 सरल परिभाषा (Hindi)
`0..n` में से `n` अलग-अलग numbers दिए गए हैं, यानी ठीक एक number गायब है। उसे खोजना है। सबसे तेज़ तरीके Gauss का sum formula या XOR हैं, दोनों O(n) time और O(1) space।

---

## 🔴 Problem it Solves
Sorting then scanning costs O(n log n). A set costs O(n) memory. Math tricks solve it in one pass with constant memory. This pattern is used to find a missing invoice number, a lost packet sequence or a gap in IDs.

## 🔴 यह क्यों बना? (Hindi)
Sort करके scan करने में O(n log n) लगता है। Set में O(n) memory लगती है। Math tricks एक pass और constant memory में हल करते हैं। यही pattern गायब invoice number, खोए packet sequence या IDs की gap खोजने में काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → n = len(nums); numbers should be 0..n
Step 2 → Expected sum = n * (n + 1) // 2
Step 3 → Actual sum = sum(nums)
Step 4 → Missing = expected - actual
XOR way: xor of all nums ^ xor of 0..n  (pairs cancel, missing remains)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → n = len(nums); numbers 0..n होने चाहिए
Step 2 → अपेक्षित जोड़ = n * (n + 1) // 2
Step 3 → असली जोड़ = sum(nums)
Step 4 → गायब = अपेक्षित - असली
XOR तरीका: सब nums का xor ^ 0..n का xor (जोड़ी कट जाती है, गायब बचता है)
```

---

## 🟡 Real World Example
Razorpay invoices are numbered 1 to N and one invoice number is missing from an export. The finance script finds it in one pass. Network code finds a dropped packet sequence number the same way.

## 🟡 Real Example Hindi mein
Razorpay के invoices 1 से N तक numbered हैं और एक export में एक invoice number गायब है। Finance script एक pass में उसे खोज लेती है। Network code में dropped packet का sequence number भी ऐसे ही निकलता है।

---

## 💻 Code Example — Basic
```python
# Basic: Gauss formula
def missing_number(nums: list[int]) -> int:  # nums holds 0..n with one value missing
    n: int = len(nums)  # the largest possible value is n
    expected: int = n * (n + 1) // 2  # sum of 0..n
    actual: int = sum(nums)  # sum of what we have
    return expected - actual  # difference is the missing number


print(missing_number([3, 0, 1]))  # n=3, missing 2
# Output: 2
print(missing_number([0, 1]))  # last value missing
# Output: 2
print(missing_number([1]))  # first value missing
# Output: 0
```

## 💻 Code Example — Advanced
```python
# Production style: XOR, set approach and a range variant
from functools import reduce  # fold a list into one value
from operator import xor  # XOR as a function
from typing import List  # type hints


def missing_xor(nums: List[int]) -> int:
    """x ^ x == 0 and x ^ 0 == x, so equal pairs cancel."""
    n: int = len(nums)  # size
    return reduce(xor, nums, 0) ^ reduce(xor, range(n + 1), 0)  # leftover is the missing one


def missing_set(nums: List[int]) -> int:
    """Clear but uses O(n) memory."""
    return (set(range(len(nums) + 1)) - set(nums)).pop()  # the only value left


def missing_in_range(nums: List[int], lo: int, hi: int) -> int:
    """One value missing from lo..hi inclusive."""
    return (lo + hi) * (hi - lo + 1) // 2 - sum(nums)  # arithmetic series


print(missing_xor([9, 6, 4, 2, 3, 5, 7, 0, 1]))  # n=9, missing 8
# Output: 8
print(missing_set([3, 0, 1]))  # same answer via sets
# Output: 2
print(missing_in_range([1, 2, 4, 5], 1, 5))  # invoices 1..5, 3 missing
# Output: 3
print(5 ^ 5, 5 ^ 0)  # why XOR works
# Output: 0 5
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: big integers never overflow
n = 10**6
total = n * (n + 1) // 2         # exact integer
missing = total - sum(nums)
```

```javascript
// JavaScript: numbers are 64-bit floats, sums above 2**53 lose precision
const n = nums.length;
const total = (n * (n + 1)) / 2;
const missing = total - nums.reduce((a, b) => a + b, 0);
// XOR in JS works on 32-bit signed integers only
```

Key difference: Python integers have unlimited size, so the sum method never overflows. In C, Java or JS (above 2^53) the sum can overflow or lose precision, which is why interviewers also ask for XOR.

---

## 🟠 FastAPI Connection
An endpoint that accepts a list of received IDs and reports the missing one. Validate that numbers are in range.

```python
# FastAPI: find missing id (pip install fastapi)
from fastapi import FastAPI, HTTPException  # app and errors

app: FastAPI = FastAPI()  # create app


@app.post("/missing")  # POST /missing with body [3, 0, 1]
def missing(nums: list[int]) -> dict[str, int]:
    n: int = len(nums)  # expected range is 0..n
    if len(set(nums)) != n or any(x < 0 or x > n for x in nums):  # duplicates or out of range
        raise HTTPException(status_code=422, detail="need distinct numbers in 0..n")  # reject
    return {"missing": n * (n + 1) // 2 - sum(nums)}  # Gauss formula
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong range for the formula
```python
# Wrong - values are 0..n but formula uses n-1:
# expected = n * (n - 1) // 2

# Correct - n is len(nums), values go up to n: n * (n + 1) // 2
```

❌ Mistake 2: Using `/` instead of `//`
```python
# Wrong - returns a float:
print(3 * 4 / 2)    # 6.0

# Correct:
print(3 * 4 // 2)   # 6
```

❌ Mistake 3: Using it with duplicates or more than one missing
```python
# Wrong - [0, 0, 2] (n=3): expected 6 - actual 2 = 4, nonsense

# Correct - validate the input first, or use a Counter/set for general cases
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
nums = [0, 1, 3]
n = len(nums)
print(n * (n + 1) / 2 - sum(nums))
print(n * (n + 1) // 2 - sum(nums))
print(0 ^ 1 ^ 3 ^ 0 ^ 1 ^ 2 ^ 3)
```

**Answer**:
```
2.0
2
2
```
`/` always gives a float, even when the result is whole. `//` stays an integer. The XOR line is the XOR of the list `[0, 1, 3]` and the full range `0..3`; everything cancels except `2`.

---

## ⚫ Interview Questions + Answers

Q1: Which approach is best?
A1: Sum or XOR: O(n) time, O(1) space. Sorting is O(n log n). A set is O(n) space but very readable.

Q2: Why does XOR work?
A2: `a ^ a = 0` and `a ^ 0 = a`, and XOR is commutative. All present numbers cancel with their partners from `0..n`.

Q3: Can the sum method overflow?
A3: Not in Python. In fixed-width integer languages it can, so XOR is safer there.

Q4: What if two numbers are missing?
A4: Use the sum and the sum of squares, or XOR with a split by a set bit, or a set difference.

Q5: What if the list is sorted?
A5: Use binary search on `nums[i] == i` for O(log n).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Exactly one number is missing from a known range
- You want O(1) extra space

❌ Avoid when:
- Several numbers are missing or duplicates exist (use a set or Counter)
- The data is not integers

---

## 📊 Visual Diagram

```
nums = [3, 0, 1]      n = 3     full range = 0 1 2 3

expected sum = 0+1+2+3 = 6
actual   sum = 3+0+1   = 4
missing      = 6 - 4   = 2

XOR: (3^0^1) ^ (0^1^2^3) = 2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gauss formula | Sum 1..n = n(n+1)/2 | 1 से n का जोड़ |
| XOR | Bitwise exclusive or | bitwise XOR |
| Overflow | Number too big for its type | संख्या का सीमा से बड़ा होना |
| Distinct | All different | सब अलग-अलग |
| O(1) space | Constant extra memory | स्थिर extra memory |

---

## ⚡ 3-Line Summary
English: Expected sum `n(n+1)//2` minus actual sum gives the missing number. XOR of the list with XOR of `0..n` does the same without overflow worries. Both are O(n) time and O(1) space.
Hindi: अपेक्षित जोड़ `n(n+1)//2` में से असली जोड़ घटाओ तो गायब number मिलता है। List के XOR को `0..n` के XOR से XOR करने पर भी वही मिलता है। दोनों O(n) time और O(1) space।

---

## ➡️ Next Topic
**467. Count Word Frequency** — count items with dict, defaultdict and Counter.
