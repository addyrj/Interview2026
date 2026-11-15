---

# D093. N-Queens
# Category: DSA — Binary Search, Heap & Backtracking
# Difficulty: ⭐⭐⭐ Hard | LeetCode #51

---

## ❓ Problem
Place `n` queens on an `n x n` chessboard so that no two queens attack each other (same row, column, or diagonal). Return all distinct board configurations (`Q` = queen, `.` = empty).

```
Input:  n = 4
Output: [[".Q..","...Q","Q...","..Q."], ["..Q.","Q...","...Q",".Q.."]]
```

---

## 💡 Quick Concept (2 lines only)
Place one queen per row. For each row, try each column that is not under attack: track used columns and both diagonals (`row - col` and `row + col`) in sets.
हिंदी: हर row में एक queen रखो; column और दोनों diagonals (row-col, row+col) को sets में track करो और conflict होने पर वापस लौटो।

---

## ✅ Solution

```python
from itertools import permutations  # for the brute-force check


# ============================================
# APPROACH 1: Brute force — every column permutation, check diagonals, O(n! * n)
# (rows and columns are already unique in a permutation)
# ============================================
def solve_n_queens_brute(n: int) -> list[list[str]]:
    result: list[list[str]] = []  # valid boards
    for cols in permutations(range(n)):  # cols[r] = column of queen in row r
        if len({r + c for r, c in enumerate(cols)}) == n and len({r - c for r, c in enumerate(cols)}) == n:  # no shared diagonals
            result.append(["." * c + "Q" + "." * (n - c - 1) for c in cols])  # draw the board
    return result  # all solutions


# ============================================
# APPROACH 2: Backtracking with sets — ~O(n!) time, O(n) space ✅ PREFERRED
# ============================================
def solve_n_queens(n: int) -> list[list[str]]:
    result: list[list[str]] = []  # all valid boards
    cols: set[int] = set()  # occupied columns
    diag1: set[int] = set()  # occupied "\" diagonals (row - col constant)
    diag2: set[int] = set()  # occupied "/" diagonals (row + col constant)
    queens: list[int] = []  # queens[r] = column of the queen in row r

    def backtrack(row: int) -> None:
        if row == n:  # all rows filled
            result.append(["." * c + "Q" + "." * (n - c - 1) for c in queens])  # build board strings
            return  # solution recorded
        for col in range(n):  # try each column in this row
            if col in cols or (row - col) in diag1 or (row + col) in diag2:  # attacked?
                continue  # skip attacked squares
            cols.add(col); diag1.add(row - col); diag2.add(row + col)  # place queen
            queens.append(col)  # remember its column
            backtrack(row + 1)  # fill the next row
            queens.pop()  # remove queen
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)  # undo marks

    backtrack(0)  # start at row 0
    return result  # all boards


# ============================================
# APPROACH 3: Bitmask — fastest, counts solutions (LeetCode 52 style)
# ============================================
def total_n_queens(n: int) -> int:
    full = (1 << n) - 1  # n bits set: all columns

    def go(cols: int, d1: int, d2: int) -> int:
        if cols == full:  # every row has a queen
            return 1  # one solution
        count = 0  # solutions in this branch
        free = full & ~(cols | d1 | d2)  # bits = safe columns in this row
        while free:  # for each safe column
            bit = free & -free  # lowest set bit
            free ^= bit  # remove it from candidates
            count += go(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1)  # shift diagonals for next row
        return count  # total

    return go(0, 0, 0)  # start with an empty board


# ============================================
# TEST CASES
# ============================================
print(solve_n_queens(4))                                  # [['.Q..', '...Q', 'Q...', '..Q.'], ['..Q.', 'Q...', '...Q', '.Q..']]
print(solve_n_queens_brute(4) == solve_n_queens(4))       # True
print(solve_n_queens(1))                                  # [['Q']]
print(len(solve_n_queens(2)), len(solve_n_queens(3)))     # 0 0
print(len(solve_n_queens(6)))                             # 4
print(len(solve_n_queens(8)))                             # 92
print(total_n_queens(8))                                  # 92
```

---

## 🔍 Why It Works
```
n=4, queens = [1,3,0,2] (column per row):
. Q . .
. . . Q
Q . . .
. . Q .
Cells on the same "\" diagonal share row-col; on the same "/" diagonal share row+col.
```
हिंदी: एक ही diagonal के सभी cells का row-col (या row+col) बराबर होता है, इसलिए set में check करना O(1) में हो जाता है।

---

## 📊 Complexity
```
Brute force:  Time O(n! * n)  | Space O(n!)  (stores permutations lazily, O(n) at once)
Backtracking: Time ~O(n!)     | Space O(n)   ← preferred (heavy pruning in practice)
Bitmask:      Time ~O(n!)     | Space O(n)   (fastest constants)
```

---

## ⚡ Variations

```python
# VARIANT 1: N-Queens II — return only the count (bitmask version above)
# VARIANT 2: Sudoku Solver — same backtracking with row/col/box sets
# VARIANT 3: Find only the first solution — return True up the stack as soon as one is found
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: checking only columns -> queens attack along diagonals
# if col in cols: continue

# ❌ Wrong: forgetting to remove from diag sets on backtrack -> later rows see phantom attacks

# ✅ Correct: track cols, row-col, row+col and undo all three
```

---

## 🎯 Interview Tip
Say: "One queen per row, so only columns and two diagonals need tracking, each in O(1) with sets (row-col and row+col identify diagonals). Pruning makes it far faster than n!." Mention the bitmask optimisation.

---

## 🔗 Related Problems
→ D090 (Subsets) | D091 (Permutations) | D092 (Combination Sum)
