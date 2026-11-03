---

# D114. Set Matrix Zeroes
# Category: DSA — Arrays & Strings (Matrix)
# Difficulty: ⭐⭐ Medium | LeetCode #73 | Asked: Amazon, Microsoft, Facebook, Adobe

---

## ❓ Problem
If an element in an m × n matrix is 0, set its entire row and column to 0. Do it in place.

```
Input:  [[1,1,1],        Output: [[1,0,1],
         [1,0,1],                 [0,0,0],
         [1,1,1]]                 [1,0,1]]
```

---

## 💡 Quick Concept (2 lines only)
Record which rows and columns contain a zero, then zero them. To get O(1) space, use the first row and first column as the markers.
हिंदी: पहले zero की जगह note करो, फिर उन row/column को zero करो — marker के लिए पहली row/column इस्तेमाल करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Row/column sets — O(m·n) time, O(m+n) space
// ============================================

function setZeroesSets(matrix) {
  const rows = new Set(), cols = new Set();          // rows and cols that must become 0
  const m = matrix.length, n = matrix[0].length;     // dimensions
  for (let i = 0; i < m; i++) {                      // find all zeros
    for (let j = 0; j < n; j++) {
      if (matrix[i][j] === 0) { rows.add(i); cols.add(j); } // remember row & col
    }
  }
  for (let i = 0; i < m; i++) {                      // apply zeros
    for (let j = 0; j < n; j++) {
      if (rows.has(i) || cols.has(j)) matrix[i][j] = 0; // row or column marked
    }
  }
  return matrix;
}

// ============================================
// APPROACH 2: First row/col as markers — O(m·n) time, O(1) space ✅ PREFERRED
// ============================================

function setZeroes(matrix) {
  const m = matrix.length, n = matrix[0].length;     // dimensions
  let firstRowZero = false, firstColZero = false;    // do first row/col need zeroing?
  for (let j = 0; j < n; j++) if (matrix[0][j] === 0) firstRowZero = true; // check first row
  for (let i = 0; i < m; i++) if (matrix[i][0] === 0) firstColZero = true; // check first col

  for (let i = 1; i < m; i++) {                      // use first row/col as flags
    for (let j = 1; j < n; j++) {
      if (matrix[i][j] === 0) {                      // zero found
        matrix[i][0] = 0;                            // mark its row
        matrix[0][j] = 0;                            // mark its column
      }
    }
  }
  for (let i = 1; i < m; i++) {                      // zero cells using the flags
    for (let j = 1; j < n; j++) {
      if (matrix[i][0] === 0 || matrix[0][j] === 0) matrix[i][j] = 0; // flagged
    }
  }
  if (firstRowZero) for (let j = 0; j < n; j++) matrix[0][j] = 0; // zero first row
  if (firstColZero) for (let i = 0; i < m; i++) matrix[i][0] = 0; // zero first column
  return matrix;
}

// ============================================
// TEST CASES
// ============================================

console.log(JSON.stringify(setZeroes([[1, 1, 1], [1, 0, 1], [1, 1, 1]])));
// [[1,0,1],[0,0,0],[1,0,1]]
console.log(JSON.stringify(setZeroes([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]])));
// [[0,0,0,0],[0,4,5,0],[0,3,1,0]]
console.log(JSON.stringify(setZeroes([[1, 2], [3, 4]])));
// [[1,2],[3,4]]
console.log(JSON.stringify(setZeroes([[0]])));      // [[0]]
console.log(JSON.stringify(setZeroesSets([[1, 0], [1, 1]]))); // [[0,0],[1,0]]
```

---

## 🔍 Why It Works
```
Step 1: remember if first row / first column had a zero (they are about to be used as flags)
Step 2: for every zero at (i,j) in the inner matrix → flag matrix[i][0], matrix[0][j]
Step 3: zero inner cells whose row-flag or column-flag is 0
Step 4: finally zero first row / column if they originally had zeros
```
Zeroing the flags last avoids corrupting information while still reading it.
हिंदी: पहली row/column को सबसे आख़िर में zero करो, वरना markers खराब हो जाएँगे।

---

## 📊 Complexity
```
Sets:    Time O(m·n) | Space O(m+n)
Markers: Time O(m·n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Rotate image 90° clockwise (LeetCode #48) — transpose then reverse each row
function rotateImage(matrix) {
  const n = matrix.length;                           // square matrix size
  for (let i = 0; i < n; i++) {                      // transpose
    for (let j = i + 1; j < n; j++) {
      [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]]; // swap across diagonal
    }
  }
  for (const row of matrix) row.reverse();           // reverse each row
  return matrix;
}
console.log(JSON.stringify(rotateImage([[1, 2], [3, 4]]))); // [[3,1],[4,2]]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: zeroing as soon as you find a 0 → new zeros trigger more zeros (whole matrix becomes 0)
// ✅ Correct: mark first, apply later
```

---

## 🎯 Interview Tip
Say: "Start with O(m+n) sets, then optimise by reusing the first row and column as flags, remembering to track them separately." Interviewers care about the order of final zeroing.

---

## 🔗 Related Problems
→ D113 (Spiral Matrix) | D104 (Rotate Array) | D105 (Move Zeroes)
