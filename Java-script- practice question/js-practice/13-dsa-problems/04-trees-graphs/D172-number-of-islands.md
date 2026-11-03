---

# D172. Number of Islands
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #200 | Asked: Amazon, Google, Microsoft, Meta, Uber, Bloomberg

---

## ❓ Problem
Given an m x n grid of `'1'` (land) and `'0'` (water), count the islands. An island is formed by connecting adjacent land cells horizontally or vertically (not diagonally).

```
Grid:
1 1 0 0 0
1 1 0 0 0
0 0 1 0 0
0 0 0 1 1

Output: 3
```

---

## 💡 Quick Concept (2 lines only)
Scan every cell; when you find unvisited land, count one island and flood-fill (DFS/BFS) all connected land so it is never counted again.
हिंदी: land मिले तो count+1 करो और उससे जुड़ी पूरी land को flood-fill से mark कर दो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: DFS flood fill (mutates the grid copy)
// Time: O(m*n) | Space: O(m*n) recursion worst case
// ============================================
function numIslands(grid) {
  if (!grid.length) return 0;                     // empty grid
  const g = grid.map(r => [...r]);                // copy so input is not destroyed
  const rows = g.length, cols = g[0].length;      // dimensions
  let count = 0;                                  // number of islands

  function dfs(r, c) {
    if (r < 0 || c < 0 || r >= rows || c >= cols) return; // out of bounds
    if (g[r][c] !== "1") return;                  // water or already visited
    g[r][c] = "0";                                // mark visited (sink the land)
    dfs(r + 1, c); dfs(r - 1, c);                 // down, up
    dfs(r, c + 1); dfs(r, c - 1);                 // right, left
  }

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (g[r][c] === "1") {                      // found a new island
        count++;                                  // count it
        dfs(r, c);                                // erase the whole island
      }
    }
  }
  return count;
}

// ============================================
// APPROACH 2: BFS flood fill with a visited set (no mutation)
// Time: O(m*n) | Space: O(min(m,n)) queue frontier
// ============================================
function numIslandsBFS(grid) {
  if (!grid.length) return 0;                     // empty grid
  const rows = grid.length, cols = grid[0].length;
  const seen = Array.from({ length: rows }, () => Array(cols).fill(false)); // visited matrix
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]]; // 4 directions
  let count = 0;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] !== "1" || seen[r][c]) continue; // skip water / visited
      count++;                                    // new island
      seen[r][c] = true;                          // mark start
      const queue = [[r, c]];                     // BFS queue
      while (queue.length) {
        const [x, y] = queue.shift();             // current cell
        for (const [dx, dy] of dirs) {
          const nx = x + dx, ny = y + dy;         // neighbour
          if (nx >= 0 && ny >= 0 && nx < rows && ny < cols &&
              grid[nx][ny] === "1" && !seen[nx][ny]) {
            seen[nx][ny] = true;                  // mark when enqueuing (avoids duplicates)
            queue.push([nx, ny]);
          }
        }
      }
    }
  }
  return count;
}

// ============================================
// APPROACH 3: Union-Find (good for dynamic follow-up)
// Time: O(m*n*α) | Space: O(m*n)
// ============================================
function numIslandsUF(grid) {
  if (!grid.length) return 0;
  const rows = grid.length, cols = grid[0].length;
  const parent = Array.from({ length: rows * cols }, (_, i) => i); // each cell its own set
  let count = 0;                                  // components = land cells initially
  const find = x => (parent[x] === x ? x : (parent[x] = find(parent[x]))); // path compression
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) if (grid[r][c] === "1") count++; // count land cells
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (grid[r][c] !== "1") continue;
      for (const [dx, dy] of [[1, 0], [0, 1]]) {  // only right and down needed
        const nr = r + dx, nc = c + dy;
        if (nr < rows && nc < cols && grid[nr][nc] === "1") {
          const a = find(r * cols + c), b = find(nr * cols + nc); // roots
          if (a !== b) { parent[a] = b; count--; } // merge two islands -> one fewer
        }
      }
    }
  }
  return count;
}

// ============================================
// TEST CASES
// ============================================
const g1 = [
  ["1", "1", "0", "0", "0"],
  ["1", "1", "0", "0", "0"],
  ["0", "0", "1", "0", "0"],
  ["0", "0", "0", "1", "1"],
];
console.log(numIslands(g1));                      // 3
console.log(numIslandsBFS(g1));                   // 3
console.log(numIslandsUF(g1));                    // 3
console.log(numIslands([["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]])); // 1
console.log(numIslands([["0", "0"], ["0", "0"]])); // 0
console.log(numIslands([["1", "0", "1"], ["0", "1", "0"], ["1", "0", "1"]])); // 5 (diagonals not connected)
console.log(numIslands([]));                      // 0
```

---

## 🔍 Why It Works
Every island is a connected component of land cells. Flood fill visits exactly one component fully and marks it, so a later scan cell inside the same island is skipped. The count equals the number of times a fresh, unmarked land cell is found.
हिंदी: हर island एक connected component है; flood fill उसे एक बार में पूरा mark कर देता है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| DFS | O(m*n) | O(m*n) worst recursion |
| BFS | O(m*n) | O(min(m,n)) frontier + O(m*n) visited |
| Union-Find | O(m*n*α) | O(m*n) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Max Area of Island (LeetCode #695) — DFS returns size
function maxAreaOfIsland(grid) {
  const g = grid.map(r => [...r]);
  function dfs(r, c) {
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] !== 1) return 0;
    g[r][c] = 0;                                  // mark visited
    return 1 + dfs(r + 1, c) + dfs(r - 1, c) + dfs(r, c + 1) + dfs(r, c - 1);
  }
  let best = 0;
  for (let r = 0; r < g.length; r++)
    for (let c = 0; c < g[0].length; c++) best = Math.max(best, dfs(r, c));
  return best;
}
console.log(maxAreaOfIsland([[1, 1, 0], [0, 1, 0], [0, 0, 1]])); // 3

// VARIANT 2: Number of Islands II (LeetCode #305) — add land online -> Union-Find
// VARIANT 3: Surrounded Regions (#130), Pacific Atlantic Water Flow (#417) — border DFS
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not marking cells visited -> infinite recursion
// ❌ Wrong: comparing number 1 with string "1" — LeetCode grid holds characters
// ❌ Wrong: BFS marking visited on dequeue — same cell enqueued many times (slow)
// ✅ Correct: mark on enqueue / entry

// ❌ Wrong: counting diagonal neighbours as connected
```

---

## 🎯 Interview Tip
Say: "Treat the grid as an implicit graph; each flood fill removes one component." Ask if mutating the input is allowed, and mention recursion depth risk (use BFS) for large grids.

---

## 🔗 Related Problems
→ D173 (Clone Graph) | D175 (Rotting Oranges) | D177 (Graph Valid Tree) | D174 (Course Schedule)
