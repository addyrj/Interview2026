---

# D013. Set Matrix Zeroes
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #73

---

## ❓ Problem
Given an `m x n` matrix, if an element is `0`, set its entire row and column to `0`. Do it **in place**.

```
Input:  [[1,1,1],[1,0,1],[1,1,1]]
Output: [[1,0,1],[0,0,0],[1,0,1]]
```

---

## 💡 Quick Concept (2 lines only)
Do not zero cells while scanning, or new zeros will spread wrongly. First record which rows/columns hold a zero, then zero them. For O(1) space, use the first row and first column as the markers.
हिंदी: पहले zero की positions note करो, फिर बाद में row/column zero करो; O(1) space के लिए पहली row/column को ही marker बना लो।

---

## ✅ Solution

```python
from copy import deepcopy  # used only to reuse the same input in tests

# ============================================
# APPROACH 1: Brute force — extra row/col sets
# O(m*n) time, O(m+n) space
# ============================================
def set_zeroes_sets(matrix: list[list[int]]) -> None:
    rows: set[int] = set()  # rows that contain a zero
    cols: set[int] = set()  # columns that contain a zero
    for i, row in enumerate(matrix):  # scan every row
        for j, val in enumerate(row):  # scan every cell
            if val == 0:  # found a zero
                rows.add(i)  # remember its row
                cols.add(j)  # remember its column
    for i, row in enumerate(matrix):  # second pass: apply zeroes
        for j in range(len(row)):  # every column index
            if i in rows or j in cols:  # row or column was marked
                row[j] = 0  # zero the cell

# ============================================
# APPROACH 2: Optimal — first row/col as markers
# O(m*n) time, O(1) space ✅ PREFERRED
# ============================================
def set_zeroes(matrix: list[list[int]]) -> None:
    m, n = len(matrix), len(matrix[0])  # dimensions
    first_row_zero = any(matrix[0][j] == 0 for j in range(n))  # does row 0 need zeroing?
    first_col_zero = any(matrix[i][0] == 0 for i in range(m))  # does col 0 need zeroing?
    for i in range(1, m):  # skip row 0 and col 0 (they are the markers)
        for j in range(1, n):  # inner cells only
            if matrix[i][j] == 0:  # found a zero
                matrix[i][0] = 0  # mark its row in column 0
                matrix[0][j] = 0  # mark its column in row 0
    for i in range(1, m):  # apply markers to inner cells
        for j in range(1, n):  # inner cells only
            if matrix[i][0] == 0 or matrix[0][j] == 0:  # row or column marked
                matrix[i][j] = 0  # zero the cell
    if first_row_zero:  # handle first row last (it held markers)
        for j in range(n):  # whole first row
            matrix[0][j] = 0  # zero it
    if first_col_zero:  # handle first column last
        for i in range(m):  # whole first column
            matrix[i][0] = 0  # zero it

# ============================================
# TEST CASES
# ============================================
a = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]  # classic example
b = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]  # zeroes in first row
c = [[1, 2], [0, 3]]  # zero in first column
for case in (a, b, c):  # run both approaches on each case
    x, y = deepcopy(case), deepcopy(case)  # independent copies
    set_zeroes_sets(x)  # brute force
    set_zeroes(y)  # optimal
    print(x == y)  # True
set_zeroes(a)  # mutate a in place
print(a)  # [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
set_zeroes(b)  # mutate b in place
print(b)  # [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
set_zeroes(c)  # mutate c in place
print(c)  # [[0, 2], [0, 0]]
```

---

## 🔍 Why It Works
```
Row 0 / col 0 store "this row/col must be zeroed".
Their own zero status is saved in two booleans first,
so markers are never confused with real zeros.
Apply to the inner cells first, row 0 / col 0 last.
```
हिंदी: पहली row/column में flags रखते हैं, उनके अपने zero होने की जानकारी अलग bool में; पहले अंदर के cells, आखिर में पहली row/column zero करो।

---

## 📊 Complexity
```
Sets approach: Time O(m*n) | Space O(m+n)
Marker approach: Time O(m*n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Pythonic, O(m+n) space using zip to find zero columns
def set_zeroes_pythonic(matrix: list[list[int]]) -> None:
    zero_rows = [i for i, row in enumerate(matrix) if 0 in row]  # rows holding a zero
    zero_cols = [j for j, col in enumerate(zip(*matrix)) if 0 in col]  # columns holding a zero
    for i in zero_rows:  # zero whole rows
        matrix[i] = [0] * len(matrix[0])  # replace row with zeros
    for row in matrix:  # zero whole columns
        for j in zero_cols:  # each marked column
            row[j] = 0  # zero the cell

d = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]  # same as case b
set_zeroes_pythonic(d)  # run alternative
print(d)  # [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
# VARIANT 2: Set cells to -1 first (marker value) then convert — O(1) space but needs a value outside input range
# VARIANT 3: Count how many cells became zero without changing the matrix (only record sets)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: zero immediately while scanning -> new zeros trigger more zeroing
for i in range(m):
    for j in range(n):
        if matrix[i][j] == 0:
            for k in range(n): matrix[i][k] = 0   # these fresh zeros will be seen later!

# ❌ Wrong: [[0] * n] * m style copies share rows (aliasing) when building test matrices

# ✅ Correct: record first, then apply; handle row 0 / col 0 last
```

---

## 🎯 Interview Tip
Say: "Brute force uses O(m+n) sets. To get O(1) I reuse the first row and column as markers, and save their own zero status in two booleans first." Follow-up: why handle the first row/col last.

---

## 🔗 Related Problems
→ D012 (Spiral Matrix) | D010 (Rotate Array) | D011 (Move Zeroes)
