---

# D113. Spiral Matrix
# Category: DSA — Arrays & Strings (Matrix)
# Difficulty: ⭐⭐ Medium | LeetCode #54 | Asked: Microsoft, Amazon, Google, Walmart

---

## ❓ Problem
Given an m × n matrix, return all elements in spiral order (clockwise from top-left).

```
Input:  [[1,2,3],
         [4,5,6],
         [7,8,9]]
Output: [1,2,3,6,9,8,7,4,5]
```

---

## 💡 Quick Concept (2 lines only)
Maintain four boundaries (top, bottom, left, right). Walk right, down, left, up; after each side shrink that boundary and stop when they cross.
हिंदी: चार boundaries रखो — right, down, left, up चलो और हर side के बाद boundary अंदर करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Visited matrix + direction vectors — O(m·n) time, O(m·n) space
// ============================================

function spiralVisited(matrix) {
  if (!matrix.length) return [];                     // empty matrix
  const m = matrix.length, n = matrix[0].length;     // dimensions
  const seen = Array.from({ length: m }, () => new Array(n).fill(false)); // visited grid
  const dr = [0, 1, 0, -1];                          // row steps: right, down, left, up
  const dc = [1, 0, -1, 0];                          // col steps
  const res = [];                                    // output
  let r = 0, c = 0, d = 0;                           // position and direction index
  for (let i = 0; i < m * n; i++) {                  // visit every cell once
    res.push(matrix[r][c]);                          // record value
    seen[r][c] = true;                               // mark visited
    const nr = r + dr[d], nc = c + dc[d];            // next cell in this direction
    if (nr < 0 || nr >= m || nc < 0 || nc >= n || seen[nr][nc]) { // blocked?
      d = (d + 1) % 4;                               // turn clockwise
    }
    r += dr[d]; c += dc[d];                          // step forward
  }
  return res;
}

// ============================================
// APPROACH 2: Shrinking boundaries — O(m·n) time, O(1) extra space ✅ PREFERRED
// ============================================

function spiralOrder(matrix) {
  const res = [];                                    // output
  if (!matrix.length) return res;                    // empty matrix
  let top = 0, bottom = matrix.length - 1;           // row boundaries
  let left = 0, right = matrix[0].length - 1;        // column boundaries
  while (top <= bottom && left <= right) {           // while a ring remains
    for (let c = left; c <= right; c++) res.push(matrix[top][c]);     // top row →
    top++;                                           // top row done
    for (let r = top; r <= bottom; r++) res.push(matrix[r][right]);   // right column ↓
    right--;                                         // right column done
    if (top <= bottom) {                             // bottom row still exists?
      for (let c = right; c >= left; c--) res.push(matrix[bottom][c]); // bottom row ←
      bottom--;                                      // bottom row done
    }
    if (left <= right) {                             // left column still exists?
      for (let r = bottom; r >= top; r--) res.push(matrix[r][left]);   // left column ↑
      left++;                                        // left column done
    }
  }
  return res;                                        // spiral order
}

// ============================================
// TEST CASES
// ============================================

console.log(spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]));
// [ 1, 2, 3, 6, 9, 8, 7, 4, 5 ]
console.log(spiralOrder([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]));
// [ 1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7 ]
console.log(spiralOrder([[1], [2], [3]]));           // [ 1, 2, 3 ]
console.log(spiralOrder([[1, 2, 3]]));               // [ 1, 2, 3 ]
console.log(spiralVisited([[1, 2], [3, 4]]));        // [ 1, 2, 4, 3 ]
console.log(spiralOrder([]));                        // []
```

---

## 🔍 Why It Works
```
1 2 3      top row   → 1 2 3   (top=1)
4 5 6      right col → 6 9     (right=1)
7 8 9      bottom    → 8 7     (bottom=1)
           left col  → 4       (left=1)
           inner ring → 5
```
The two `if` checks stop duplicate visits when only one row or column remains.
हिंदी: आख़िर में single row/column बचे तो `if` check duplicate रोकता है।

---

## 📊 Complexity
```
Visited grid: Time O(m·n) | Space O(m·n)
Boundaries:   Time O(m·n) | Space O(1) extra ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Spiral Matrix II (LeetCode #59) — generate n×n matrix filled 1..n²
function generateMatrix(n) {
  const mat = Array.from({ length: n }, () => new Array(n).fill(0)); // empty grid
  let top = 0, bottom = n - 1, left = 0, right = n - 1, num = 1;     // boundaries and counter
  while (top <= bottom && left <= right) {           // each ring
    for (let c = left; c <= right; c++) mat[top][c] = num++;     // top row
    top++;
    for (let r = top; r <= bottom; r++) mat[r][right] = num++;   // right col
    right--;
    for (let c = right; c >= left && top <= bottom; c--) mat[bottom][c] = num++; // bottom row
    bottom--;
    for (let r = bottom; r >= top && left <= right; r--) mat[r][left] = num++;   // left col
    left++;
  }
  return mat;
}
console.log(generateMatrix(3));                      // [ [ 1, 2, 3 ], [ 8, 9, 4 ], [ 7, 6, 5 ] ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: skipping the `top <= bottom` / `left <= right` guards
//          → single row/column matrices get elements pushed twice
// ✅ Correct: guard the bottom and left passes
```

---

## 🎯 Interview Tip
Say: "Four boundaries that shrink after each side; guards prevent double-counting for non-square inputs." Test with a 1×n and n×1 matrix before finishing.

---

## 🔗 Related Problems
→ D114 (Set Matrix Zeroes) | D104 (Rotate Array) | D115 (Trapping Rain Water)
