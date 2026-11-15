---

# 470. Pascal's Triangle
# हिंदी में: पास्कल का त्रिभुज

Full runnable solution (full triangle, single row, pretty print, `math.comb` cross-check): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Pascal's triangle is a triangle of numbers where each row starts and ends with 1 and every inner number is the sum of the two numbers above it. Row `k` holds the binomial coefficients `C(k, 0) ... C(k, k)`.

## 🔵 सरल परिभाषा (Hindi)
Pascal's triangle संख्याओं का त्रिभुज है जिसमें हर row 1 से शुरू और 1 पर खत्म होती है और बीच की हर संख्या ऊपर की दो संख्याओं का जोड़ होती है। Row `k` में binomial coefficients `C(k, 0) ... C(k, k)` होते हैं।

---

## 🔴 Problem it Solves
It teaches 2D dynamic programming (build each row from the previous row), and gives combinations "n choose k" without computing big factorials. Probability, expansion of `(a+b)^n` and counting paths all use it.

## 🔴 यह क्यों बना? (Hindi)
यह 2D dynamic programming सिखाता है (हर row पिछली row से बनती है) और बड़े factorials निकाले बिना "n choose k" देता है। Probability, `(a+b)^n` का expansion और रास्तों की गिनती सब में काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Row 0 is [1]
Step 2 → New row starts with 1
Step 3 → Each inner cell = previous_row[c-1] + previous_row[c]
Step 4 → New row ends with 1
Step 5 → Repeat for the number of rows asked
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Row 0 है [1]
Step 2 → नई row 1 से शुरू
Step 3 → हर बीच का cell = पिछली_row[c-1] + पिछली_row[c]
Step 4 → नई row 1 पर खत्म
Step 5 → जितनी rows चाहिए उतनी बार दोहराओ
```

---

## 🟡 Real World Example
A probability service for a game: "chance of exactly 3 heads in 5 flips" is `C(5, 3) / 2^5`, and row 5 of Pascal's triangle gives all `C(5, k)` at once. A Razorpay-style split calculator counts the ways to choose which k of n people pay.

## 🟡 Real Example Hindi mein
Game की probability service में "5 सिक्कों में ठीक 3 heads" की संभावना `C(5, 3) / 2^5` है, और Pascal की row 5 एक साथ सारे `C(5, k)` देती है। Split calculator गिनता है कि n लोगों में से k कौन भुगतान करें, इसके कितने तरीके हैं।

---

## 💻 Code Example — Basic
```python
# Basic: build the whole triangle row by row
def pascal(rows: int) -> list[list[int]]:  # returns `rows` rows
    tri: list[list[int]] = []  # all rows so far
    for r in range(rows):  # row index 0, 1, 2 ...
        row: list[int] = [1] * (r + 1)  # edges are 1, row r has r+1 cells
        for c in range(1, r):  # inner cells only
            row[c] = tri[r - 1][c - 1] + tri[r - 1][c]  # sum of the two cells above
        tri.append(row)  # store this row
    return tri  # the triangle


for line in pascal(5):  # print each row
    print(line)  # one row per line
# Output:
# [1]
# [1, 1]
# [1, 2, 1]
# [1, 3, 3, 1]
# [1, 4, 6, 4, 1]
print(pascal(0), pascal(1))  # edge cases
# Output: [] [[1]]
```

## 💻 Code Example — Advanced
```python
# Production style: single row in O(k) space, centered output, math.comb check
from math import comb  # binomial coefficient (Python 3.8+)
from typing import List  # type hints


def pascal_row(k: int) -> List[int]:
    """Return row k (0-indexed) using only O(k) memory."""
    if k < 0:  # invalid input
        raise ValueError("row index must be >= 0")  # clear message
    row: List[int] = [1]  # row 0
    for _ in range(k):  # build up to row k
        row = [1] + [a + b for a, b in zip(row, row[1:])] + [1]  # neighbour sums with 1 on each edge
    return row  # row k


def pretty(rows: int) -> str:
    """Centered text triangle."""
    tri: List[List[int]] = [pascal_row(i) for i in range(rows)]  # all rows
    width: int = len(" ".join(map(str, tri[-1])))  # last row is the widest
    return "\n".join(" ".join(map(str, r)).center(width) for r in tri)  # center each line


print(pascal_row(4))  # row 4
# Output: [1, 4, 6, 4, 1]
print(pascal_row(5) == [comb(5, i) for i in range(6)])  # equals binomial coefficients
# Output: True
print(sum(pascal_row(10)), 2 ** 10)  # row sum is a power of two
# Output: 1024 1024
print(pascal_row(30)[15])  # big numbers are fine in Python
# Output: 155117520
print(pretty(4))  # drawn triangle (trailing spaces are part of the output)
# Output:
#    1
#   1 1
#  1 2 1
# 1 3 3 1
try:  # invalid input
    pascal_row(-1)  # raises
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message
# Output: ValueError: row index must be >= 0
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: zip pairs neighbours, big ints are exact
row = [1] + [a + b for a, b in zip(row, row[1:])] + [1]
```

```javascript
// JavaScript: no zip, and numbers above 2**53 lose precision
row = [1, ...row.slice(1).map((v, i) => v + row[i]), 1];
// for big rows use BigInt: 1n, v + row[i] with BigInt values
```

Key difference: Python integers never lose precision, so row 100 is exact. In JS, values above `Number.MAX_SAFE_INTEGER` (2^53 - 1) are wrong unless you use `BigInt`.

---

## 🟠 FastAPI Connection
An endpoint that returns one row. Limit `k` so users cannot request a giant computation.

```python
# FastAPI: pascal row endpoint (pip install fastapi)
from fastapi import FastAPI, Query  # app and validation

app: FastAPI = FastAPI()  # create app


@app.get("/pascal/{k}")  # GET /pascal/4
def pascal(k: int, as_string: bool = Query(False)) -> list[int]:
    if k < 0 or k > 1000:  # protect the server
        return []  # or raise HTTPException(422)
    row: list[int] = [1]  # row 0
    for _ in range(k):  # build up
        row = [1] + [a + b for a, b in zip(row, row[1:])] + [1]  # next row
    return row  # JSON list (huge ints are serialised exactly by Python, but JS clients may round them)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Off-by-one in the row count
```python
# Wrong - row r has r+1 cells, not r:
# row = [1] * r

# Correct:
# row = [1] * (r + 1)
```

❌ Mistake 2: Inner loop range includes the edges
```python
# Wrong - reads tri[r-1][-1] or an index that does not exist:
# for c in range(0, r + 1): ...

# Correct - for c in range(1, r)
```

❌ Mistake 3: Computing factorials for every cell
```python
# Wrong - very slow and wasteful for big rows:
# math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

# Correct - math.comb(n, k) or build rows by addition
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from math import comb

row = [1]
for _ in range(3):
    row = [1] + [a + b for a, b in zip(row, row[1:])] + [1]
print(row)
print([comb(3, k) for k in range(4)] == row)
print(comb(5, 7), comb(0, 0))
```

**Answer**:
```
[1, 3, 3, 1]
True
0 1
```
Row 3 is `[1, 3, 3, 1]`, which equals the binomial coefficients `C(3, k)`. `comb(5, 7)` is `0` (you cannot choose 7 from 5, and Python returns 0 instead of raising), and `comb(0, 0)` is `1`.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity of the full triangle?
A1: O(n^2) time and O(n^2) space. A single row needs O(k) space if you keep only the previous row.

Q2: How is Pascal's triangle linked to combinations?
A2: Cell `(n, k)` equals `C(n, k) = n! / (k! (n - k)!)`.

Q3: What is the sum of row n?
A3: `2^n`.

Q4: How do you get row k directly in O(k) time?
A4: Use `C(k, i + 1) = C(k, i) * (k - i) // (i + 1)` to walk across the row.

Q5: Which DP idea does this show?
A5: Each cell depends only on the previous row, so you can drop older rows to save space.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need many binomial coefficients at once
- Teaching 2D DP and recurrence relations

❌ Avoid when:
- You need only one `C(n, k)` (use `math.comb`)
- n is huge and you need results modulo a number (use factorial tables with modular inverses)

---

## 📊 Visual Diagram

```
        1
       1 1
      1 2 1
     1 3 3 1
    1 4 6 4 1

  3 = 1 + 2     (cell = left parent + right parent)
  6 = 3 + 3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Binomial coefficient | C(n, k), ways to choose k of n | n में से k चुनने के तरीके |
| Row | One level of the triangle | त्रिभुज की एक पंक्ति |
| Dynamic programming | Reuse earlier results | पिछले परिणामों का दोबारा उपयोग |
| Recurrence | Rule that builds the next value | अगला मान बनाने का नियम |
| Edge | First and last cell of a row | row का पहला और आख़िरी cell |

---

## ⚡ 3-Line Summary
English: Each row starts and ends with 1 and every inner cell is the sum of the two cells above. Row k equals `C(k, i)` and sums to `2^k`. Build it in O(n^2) time, or one row in O(k) space.
Hindi: हर row 1 से शुरू और खत्म होती है और बीच का हर cell ऊपर के दो cells का जोड़ है। Row k में `C(k, i)` होते हैं और जोड़ `2^k` होता है। पूरा त्रिभुज O(n^2) में, एक row O(k) space में।

---

## ➡️ Next Topic
**471. Implement Stack** — build a LIFO stack with a list and a linked list.
