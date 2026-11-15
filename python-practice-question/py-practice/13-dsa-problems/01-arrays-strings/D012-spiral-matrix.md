---

# D012. Spiral Matrix
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #54

---

## ❓ Problem
Given an `m x n` matrix, return all elements in spiral order (clockwise, starting at the top-left).

```
Input:  matrix = [[1,2,3],[4,5,6],[7,8,9]]
Output: [1,2,3,6,9,8,7,4,5]
```

---

## 💡 Quick Concept (2 lines only)
Keep four boundaries (top, bottom, left, right). Walk right along the top row, down the right column, left along the bottom row, up the left column, shrinking the boundary after each side.
हिंदी: चार boundaries रखो; हर side चलने के बाद उस boundary को अंदर खिसकाओ, और बीच में check करो कि rows/cols बचे हैं या नहीं।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — visited matrix + direction changes
# O(m*n) time, O(m*n) space
# ============================================
def spiral_visited(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:                      # empty matrix
        return []                                        # nothing to walk
    m, n = len(matrix), len(matrix[0])                   # dimensions
    seen = [[False] * n for _ in range(m)]               # visited flags
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]            # right, down, left, up
    r = c = d = 0                                        # position and direction index
    out: list[int] = []                                  # result
    for _ in range(m * n):                               # exactly m*n steps
        out.append(matrix[r][c])                         # take current cell
        seen[r][c] = True                                # mark it
        nr, nc = r + dirs[d][0], c + dirs[d][1]          # try to continue straight
        if not (0 <= nr < m and 0 <= nc < n) or seen[nr][nc]:  # wall or visited?
            d = (d + 1) % 4                              # turn clockwise
            nr, nc = r + dirs[d][0], c + dirs[d][1]      # step in the new direction
        r, c = nr, nc                                    # move
    return out                                           # spiral order


# ============================================
# APPROACH 2: Shrinking boundaries ✅ PREFERRED
# O(m*n) time, O(1) extra space (besides output)
# ============================================
def spiral_order(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:                      # empty matrix
        return []                                        # nothing to walk
    top, bottom = 0, len(matrix) - 1                     # row boundaries
    left, right = 0, len(matrix[0]) - 1                  # column boundaries
    out: list[int] = []                                  # result
    while top <= bottom and left <= right:               # while a ring remains
        for c in range(left, right + 1):                 # top row, left -> right
            out.append(matrix[top][c])                   # take cell
        top += 1                                         # top row done
        for r in range(top, bottom + 1):                 # right column, top -> bottom
            out.append(matrix[r][right])                 # take cell
        right -= 1                                       # right column done
        if top <= bottom:                                # still a bottom row left?
            for c in range(right, left - 1, -1):         # bottom row, right -> left
                out.append(matrix[bottom][c])            # take cell
            bottom -= 1                                  # bottom row done
        if left <= right:                                # still a left column left?
            for r in range(bottom, top - 1, -1):         # left column, bottom -> top
                out.append(matrix[r][left])              # take cell
            left += 1                                    # left column done
    return out                                           # spiral order


# ============================================
# TEST CASES
# ============================================
m1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
m2 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
print(spiral_visited(m1))                                # [1, 2, 3, 6, 9, 8, 7, 4, 5]
print(spiral_order(m1))                                  # [1, 2, 3, 6, 9, 8, 7, 4, 5]
print(spiral_order(m2))                                  # [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
print(spiral_visited(m2))                                # [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
print(spiral_order([[1, 2, 3]]))                         # [1, 2, 3]       (single row)
print(spiral_order([[1], [2], [3]]))                     # [1, 2, 3]       (single column)
print(spiral_order([[7]]))                               # [7]
print(spiral_order([]))                                  # []
```

---

## 🔍 Why It Works
```
1 2 3 4        pass 1: top row   1 2 3 4        top=1
5 6 7 8   ->           right col 8 12           right=2
9 10 11 12             bottom    11 10 9        bottom=1
                       left col  5              left=1
                pass 2: top row  6 7  (then bottom<top / ring ends)
```
हिंदी: हर चक्कर में एक "ring" निकलती है; `if top <= bottom` और `if left <= right` वाले checks single row/column में दोबारा गिनने से रोकते हैं।

---

## 📊 Complexity
```
Visited matrix: Time O(m*n) | Space O(m*n)
Boundaries:     Time O(m*n) | Space O(1) extra  ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Pythonic peel-the-top-row-and-rotate (O(m*n*min(m,n)) but 4 lines)
def spiral_pythonic(matrix: list[list[int]]) -> list[int]:
    m = [row[:] for row in matrix]                       # copy so input is untouched
    out: list[int] = []                                  # result
    while m:                                             # while rows remain
        out += m.pop(0)                                  # take the top row
        m = [list(col) for col in zip(*m)][::-1]         # rotate remaining matrix counter-clockwise
    return out                                           # spiral order

print(spiral_pythonic([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))  # [1, 2, 3, 6, 9, 8, 7, 4, 5]

# VARIANT 2: Spiral Matrix II (#59) -> fill an n x n matrix with 1..n^2 using the same boundaries
# VARIANT 3: Rotate Image (#48) -> transpose + reverse each row
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no `top <= bottom` / `left <= right` guards -> single row/column gets traversed twice
bad = [[1, 2, 3]]
# without the guards the bottom row pass would append 3,2,1 again -> [1,2,3,3,2,1]

# ❌ Wrong: matrix[0] on an empty matrix -> IndexError

# ✅ Correct: guard empty input and re-check boundaries before the 3rd and 4th passes
```

---

## 🎯 Interview Tip
Say: "Four shrinking boundaries; after the top and right passes I re-check `top <= bottom` and `left <= right` so a single row or column isn't traversed twice." Walk through a 3x4 example.

---

## 🔗 Related Problems
→ D013 (Set Matrix Zeroes) | D010 (Rotate Array) | D014 (Trapping Rain Water)
