---

# 469. Matrix Rotation
# हिंदी में: Matrix को 90 डिग्री घुमाना

Full runnable solution (new matrix, in-place, counter-clockwise, tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Rotate a 2D grid by 90 degrees clockwise. The Python trick: reverse the rows, then transpose with `zip(*rows)`. For in-place on a square matrix: transpose, then reverse each row.

## 🔵 सरल परिभाषा (Hindi)
2D grid को 90 डिग्री clockwise घुमाना है। Python की trick: rows को उलटो, फिर `zip(*rows)` से transpose करो। Square matrix में in-place: transpose करो, फिर हर row उलटो।

---

## 🔴 Problem it Solves
Images, game boards, seat maps and tables are 2D grids. Rotating them needs correct index mapping: the item at `(r, c)` moves to `(c, n-1-r)`. Doing this by hand with indexes is error prone, so the "transpose + reverse" idea gives a simple, safe recipe.

## 🔴 यह क्यों बना? (Hindi)
Images, game boards, seat maps और tables 2D grids होते हैं। इन्हें घुमाने में सही index mapping चाहिए: `(r, c)` का item `(c, n-1-r)` पर जाता है। हाथ से indexes लगाने में गलती होती है, इसलिए "transpose + reverse" एक आसान और सुरक्षित तरीका है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clockwise = reverse the order of rows
Step 2 → Transpose: rows become columns (zip(*matrix))
Step 3 → Convert each zipped tuple back to a list
In place (N x N): transpose by swapping across the diagonal, then reverse each row
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Clockwise = rows का क्रम उलटो
Step 2 → Transpose: rows columns बन जाती हैं (zip(*matrix))
Step 3 → हर tuple को वापस list बनाओ
In place (N x N): diagonal के आर-पार swap से transpose, फिर हर row उलटो
```

---

## 🟡 Real World Example
A photo app rotates a pixel grid when the phone turns sideways. A cinema booking API (BookMyShow style) stores a seat map as rows and columns, and the admin panel rotates it for a different screen orientation.

## 🟡 Real Example Hindi mein
Photo app phone घुमाने पर pixel grid rotate करता है। BookMyShow जैसी booking API seat map को rows-columns में रखती है और admin panel उसे दूसरी screen orientation के लिए घुमाता है।

---

## 💻 Code Example — Basic
```python
# Basic: rotate 90 degrees clockwise with zip
grid: list[list[int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 3 x 3 input

reversed_rows = grid[::-1]  # step 1: last row first
print(reversed_rows)  # intermediate result
# Output: [[7, 8, 9], [4, 5, 6], [1, 2, 3]]

rotated: list[list[int]] = [list(row) for row in zip(*reversed_rows)]  # step 2: transpose
print(rotated)  # final result
# Output: [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

print([list(r) for r in zip(*[[1, 2, 3], [4, 5, 6]])])  # transpose of a 2 x 3 matrix
# Output: [[1, 4], [2, 5], [3, 6]]
```

## 💻 Code Example — Advanced
```python
# Production style: in-place, counter-clockwise, 180, and a validity check
from typing import List  # type hints

Matrix = List[List[int]]  # alias for readability


def rotate_cw(m: Matrix) -> Matrix:
    """New matrix, works for any rectangle."""
    return [list(row) for row in zip(*m[::-1])]  # reverse rows, then transpose


def rotate_ccw(m: Matrix) -> Matrix:
    """Counter-clockwise: transpose, then reverse the row order."""
    return [list(row) for row in zip(*m)][::-1]  # columns, bottom-up


def rotate_inplace(m: Matrix) -> None:
    """Square matrix only, O(1) extra space."""
    n: int = len(m)  # size
    if any(len(row) != n for row in m):  # not square
        raise ValueError("in-place rotation needs a square matrix")  # explain
    for i in range(n):  # transpose
        for j in range(i + 1, n):  # upper triangle only
            m[i][j], m[j][i] = m[j][i], m[i][j]  # swap across the diagonal
    for row in m:  # reverse every row
        row.reverse()  # in place


g: Matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # input
print(rotate_cw(g))  # clockwise
# Output: [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
print(rotate_ccw(g))  # counter-clockwise
# Output: [[3, 6, 9], [2, 5, 8], [1, 4, 7]]
print(rotate_cw([[1, 2, 3], [4, 5, 6]]))  # rectangle 2 x 3 becomes 3 x 2
# Output: [[4, 1], [5, 2], [6, 3]]
rotate_inplace(g)  # mutates g
print(g)  # same as rotate_cw result
# Output: [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
try:  # non-square in place
    rotate_inplace([[1, 2, 3], [4, 5, 6]])  # fails
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message
# Output: ValueError: in-place rotation needs a square matrix
print(rotate_cw(rotate_cw(g)) == rotate_ccw(rotate_ccw(g)))  # 180 degrees either way
# Output: True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: zip(*) transposes
rotated = [list(r) for r in zip(*m[::-1])]
```

```javascript
// JavaScript: no zip, use map on the first row
const rotated = m[0].map((_, c) => m.map(row => row[c]).reverse());
```

Key difference: Python's `zip(*matrix)` is a one-line transpose. JS needs `map` over column indexes. Also, `[[0]*3]*3` in Python is a classic trap (see mistakes), the same as `new Array(3).fill([])` in JS where all rows share one array.

---

## 🟠 FastAPI Connection
Accept a grid in the request body and return it rotated. Pydantic checks that every row has the same length.

```python
# FastAPI: rotate endpoint (pip install fastapi)
from fastapi import FastAPI, HTTPException  # app and errors

app: FastAPI = FastAPI()  # create app


@app.post("/rotate")  # POST /rotate with [[1,2],[3,4]]
def rotate(grid: list[list[int]]) -> list[list[int]]:
    if not grid or len({len(r) for r in grid}) != 1:  # empty or jagged
        raise HTTPException(status_code=422, detail="grid must be rectangular")  # reject
    return [list(r) for r in zip(*grid[::-1])]  # clockwise rotation
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building a grid with shared rows
```python
# Wrong - all rows are the same list object:
g = [[0] * 3] * 3
g[0][0] = 1
print(g)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]

# Correct:
g = [[0] * 3 for _ in range(3)]
```

❌ Mistake 2: Forgetting `list(...)` after zip
```python
# Wrong - rows are tuples, not lists:
print(list(zip(*[[1, 2], [3, 4]])))   # [(1, 3), (2, 4)]

# Correct - [list(r) for r in zip(*m)]
```

❌ Mistake 3: Swapping the full matrix when transposing in place
```python
# Wrong - for j in range(n) swaps every pair twice and restores the original

# Correct - for j in range(i + 1, n)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
m = [[1, 2], [3, 4]]
print(list(zip(*m)))
print(list(zip(*m[::-1])))
m2 = [[0] * 2] * 2
m2[0][0] = 9
print(m2)
```

**Answer**:
```
[(1, 3), (2, 4)]
[(3, 1), (4, 2)]
[[9, 0], [9, 0]]
```
`zip(*m)` transposes and yields tuples. Reversing the rows first gives the clockwise rotation. The last line shows that `[[0] * 2] * 2` repeats the same inner list, so changing one row changes both.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: O(n*m) time. New-matrix version uses O(n*m) space, in-place square version uses O(1).

Q2: Where does the item at `(r, c)` go after a clockwise rotation of an N x N matrix?
A2: To `(c, N - 1 - r)`.

Q3: How do you rotate counter-clockwise in place?
A3: Transpose, then reverse the order of the rows (or reverse each row first, then transpose).

Q4: Why does `zip(*m)` work?
A4: `*m` unpacks the rows as separate arguments, and `zip` groups the first items, then the second items, and so on, which are the columns.

Q5: Can you rotate a non-square matrix in place?
A5: Not with the swap method, because the shape changes. Create a new matrix.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Rotating small to medium grids (boards, seat maps, tables)
- You want short, readable code (`zip`)

❌ Avoid when:
- Large images or numeric arrays (use `numpy.rot90` or Pillow)
- Memory is critical and the matrix is square (use the in-place version)

---

## 📊 Visual Diagram

```
 1 2 3        7 4 1
 4 5 6   -->  8 5 2     clockwise 90
 7 8 9        9 6 3

step 1 reverse rows:  7 8 9 / 4 5 6 / 1 2 3
step 2 transpose:     7 4 1 / 8 5 2 / 9 6 3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transpose | Swap rows and columns | rows और columns की अदला-बदली |
| Clockwise | Direction of a clock | घड़ी की दिशा में |
| In place | Change the same matrix | उसी matrix में बदलाव |
| Unpacking `*` | Spread a list as arguments | list को arguments में खोलना |
| Jagged | Rows of different lengths | अलग-अलग लंबाई की rows |

---

## ⚡ 3-Line Summary
English: Clockwise rotation is "reverse the rows, then transpose": `[list(r) for r in zip(*m[::-1])]`. For a square matrix in place, transpose then reverse each row. It is O(n*m) time.
Hindi: Clockwise rotation यानी "rows उलटो, फिर transpose": `[list(r) for r in zip(*m[::-1])]`। Square matrix में in place: transpose करो फिर हर row उलटो। Time O(n*m)।

---

## ➡️ Next Topic
**470. Pascal's Triangle** — build a triangle where each number is the sum of the two above it.
