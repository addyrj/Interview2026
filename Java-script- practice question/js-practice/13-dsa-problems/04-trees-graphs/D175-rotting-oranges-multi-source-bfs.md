---

# D175. Rotting Oranges (Multi-Source BFS)
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #994 | Asked: Amazon, Microsoft, Google, Walmart, Adobe

---

## ❓ Problem
Grid cells: `0` empty, `1` fresh orange, `2` rotten orange. Each minute, every fresh orange 4-directionally adjacent to a rotten one becomes rotten. Return the minimum minutes until no fresh orange remains, or `-1` if impossible.

```
Grid:           After 1 min:      ... After 4 min:
2 1 1           2 2 1             2 2 2
1 1 0           2 1 0             2 2 0
0 1 1           0 1 1             0 2 2

Output: 4
```

---

## 💡 Quick Concept (2 lines only)
Start BFS from ALL rotten oranges at once (multi-source). Each BFS level equals one minute; fresh oranges reached get rotten and join the queue.
हिंदी: सभी rotten oranges से एक साथ BFS शुरू करो; हर level = 1 मिनट।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1 (Brute force): simulate minute by minute scanning the whole grid
// Time: O((m*n)^2) worst | Space: O(m*n)
// ============================================
function orangesRottingBrute(grid) {
  const g = grid.map(r => [...r]);                // work on a copy
  const rows = g.length, cols = g[0].length;
  let minutes = 0;
  while (true) {
    const toRot = [];                             // fresh cells that rot this minute
    for (let r = 0; r < rows; r++)
      for (let c = 0; c < cols; c++)
        if (g[r][c] === 1 &&
            [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dr, dc]) => {
              const nr = r + dr, nc = c + dc;     // neighbour
              return nr >= 0 && nc >= 0 && nr < rows && nc < cols && g[nr][nc] === 2;
            })) toRot.push([r, c]);               // has a rotten neighbour
    if (!toRot.length) break;                     // nothing changes -> stop
    for (const [r, c] of toRot) g[r][c] = 2;      // rot them all simultaneously
    minutes++;                                    // one minute passed
  }
  return g.flat().includes(1) ? -1 : minutes;     // fresh left -> impossible
}

// ============================================
// APPROACH 2: Multi-source BFS (Optimal)
// Time: O(m*n) | Space: O(m*n)
// ============================================
function orangesRotting(grid) {
  const rows = grid.length, cols = grid[0].length;
  const g = grid.map(r => [...r]);                // avoid mutating input
  const queue = [];                               // all rotten oranges (level 0)
  let fresh = 0;                                  // count of fresh oranges
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (g[r][c] === 2) queue.push([r, c]);      // source
      else if (g[r][c] === 1) fresh++;            // to be infected
    }
  }
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  let minutes = 0;
  let head = 0;                                   // index pointer (avoids O(n) shift)
  while (head < queue.length && fresh > 0) {
    const size = queue.length - head;             // nodes in current minute
    for (let i = 0; i < size; i++) {
      const [r, c] = queue[head++];               // dequeue
      for (const [dr, dc] of dirs) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nc >= 0 && nr < rows && nc < cols && g[nr][nc] === 1) {
          g[nr][nc] = 2;                          // infect
          fresh--;                                // one less fresh
          queue.push([nr, nc]);                   // spreads next minute
        }
      }
    }
    minutes++;                                    // a full minute elapsed
  }
  return fresh === 0 ? minutes : -1;              // leftover fresh -> unreachable
}

// ============================================
// TEST CASES
// ============================================
console.log(orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]));  // 4
console.log(orangesRotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]));  // -1
console.log(orangesRotting([[0, 2]]));                           // 0
console.log(orangesRotting([[0]]));                              // 0
console.log(orangesRotting([[1]]));                              // -1
console.log(orangesRottingBrute([[2, 1, 1], [1, 1, 0], [0, 1, 1]])); // 4
console.log(orangesRottingBrute([[2, 1, 1], [0, 1, 1], [1, 0, 1]])); // -1
console.log(orangesRotting([[2, 1, 1, 1, 2]]));                  // 2
```

---

## 🔍 Why It Works
BFS expands in waves; starting from all rotten cells together means each fresh orange is reached by its nearest rotten source at its shortest time. The wave count when the last fresh orange rots is the answer, and unreachable oranges stay fresh -> -1.
हिंदी: सबसे नज़दीकी rotten source से सबसे जल्दी पहुँचते हैं; बचे fresh = -1।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Simulation | O((m*n)^2) worst | O(m*n) |
| Multi-source BFS | O(m*n) | O(m*n) |

---

## ⚡ Variations

```javascript
// VARIANT 1: 01 Matrix (LeetCode #542) — distance to nearest 0: multi-source BFS from all zeros
function updateMatrix(mat) {
  const R = mat.length, C = mat[0].length, q = [];
  const d = mat.map(r => r.map(() => -1));        // -1 = unvisited
  for (let r = 0; r < R; r++)
    for (let c = 0; c < C; c++) if (mat[r][c] === 0) { d[r][c] = 0; q.push([r, c]); }
  for (let h = 0; h < q.length; h++) {
    const [r, c] = q[h];
    for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nc >= 0 && nr < R && nc < C && d[nr][nc] === -1) {
        d[nr][nc] = d[r][c] + 1;                  // one step further
        q.push([nr, nc]);
      }
    }
  }
  return d;
}
console.log(JSON.stringify(updateMatrix([[0, 0, 0], [0, 1, 0], [1, 1, 1]]))); // [[0,0,0],[0,1,0],[1,2,1]]

// VARIANT 2: Walls and Gates (#286), Map of Highest Peak (#1765) — same pattern
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: running BFS separately from each rotten orange and taking max/min
//    — rotting happens simultaneously, so one combined queue is needed

// ❌ Wrong: returning `minutes` without checking fresh === 0 (misses -1 case)

// ❌ Wrong: counting an extra minute after the last orange rots
//    (loop condition includes `fresh > 0` to avoid the off-by-one)
```

---

## 🎯 Interview Tip
Say: "Simultaneous spread = multi-source BFS; put every rotten orange in the initial queue; level count = minutes; leftover fresh = -1." Watch the off-by-one: do not count the final empty level.

---

## 🔗 Related Problems
→ D172 (Number of Islands) | D176 (Word Ladder) | D167 (Level Order) | D174 (Course Schedule)
