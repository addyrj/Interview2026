---

# D174. Course Schedule (Topological Sort)
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #207 | Asked: Amazon, Google, Microsoft, Meta, Uber

---

## ❓ Problem
There are `numCourses` courses labeled `0..n-1`. `prerequisites[i] = [a, b]` means you must take course `b` before `a`. Return true if you can finish all courses (i.e. the dependency graph has no cycle).

```
numCourses = 2, prerequisites = [[1,0]]       -> true   (0 -> 1)
numCourses = 2, prerequisites = [[1,0],[0,1]] -> false  (cycle)
```

---

## 💡 Quick Concept (2 lines only)
Courses are nodes, prerequisites are directed edges. All courses can be finished iff the directed graph is acyclic — check with Kahn's BFS (in-degrees) or DFS colouring.
हिंदी: directed graph में cycle नहीं होनी चाहिए; Kahn's (in-degree) या DFS से check करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Kahn's algorithm (BFS topological sort) — Optimal
// Time: O(V + E) | Space: O(V + E)
// ============================================
function canFinish(numCourses, prerequisites) {
  const adj = Array.from({ length: numCourses }, () => []); // adj[b] = courses unlocked by b
  const indeg = Array(numCourses).fill(0);        // number of unmet prerequisites
  for (const [a, b] of prerequisites) {
    adj[b].push(a);                               // edge b -> a
    indeg[a]++;                                   // a has one more prerequisite
  }
  const queue = [];                               // courses ready to take
  for (let i = 0; i < numCourses; i++) if (indeg[i] === 0) queue.push(i); // no prerequisites
  let taken = 0;                                  // courses completed
  while (queue.length) {
    const c = queue.shift();                      // take a ready course
    taken++;                                      // count it
    for (const nxt of adj[c]) {
      if (--indeg[nxt] === 0) queue.push(nxt);    // prerequisite satisfied -> maybe ready
    }
  }
  return taken === numCourses;                    // all taken <=> no cycle
}

// ============================================
// APPROACH 2: DFS with 3 states (0=unvisited, 1=visiting, 2=done)
// Time: O(V + E) | Space: O(V + E)
// ============================================
function canFinishDFS(numCourses, prerequisites) {
  const adj = Array.from({ length: numCourses }, () => []);
  for (const [a, b] of prerequisites) adj[b].push(a); // edge b -> a
  const state = Array(numCourses).fill(0);        // visit state per node
  function hasCycle(u) {
    if (state[u] === 1) return true;              // back edge to node on current path
    if (state[u] === 2) return false;             // already proven safe
    state[u] = 1;                                 // mark: on current path
    for (const v of adj[u]) if (hasCycle(v)) return true; // explore
    state[u] = 2;                                 // finished: no cycle through u
    return false;
  }
  for (let i = 0; i < numCourses; i++) if (hasCycle(i)) return false;
  return true;
}

// ============================================
// APPROACH 3 (Brute force): repeatedly remove nodes with no prerequisites
// Time: O(V * (V + E)) | Space: O(V + E)
// ============================================
function canFinishBrute(numCourses, prerequisites) {
  let edges = [...prerequisites];                 // remaining dependencies
  const removed = new Set();                      // finished courses
  let progress = true;
  while (progress) {
    progress = false;
    for (let c = 0; c < numCourses; c++) {
      if (removed.has(c)) continue;
      if (!edges.some(([a]) => a === c)) {        // no remaining prerequisite for c
        removed.add(c);                           // take c
        edges = edges.filter(([, b]) => b !== c); // c no longer blocks anyone
        progress = true;
      }
    }
  }
  return removed.size === numCourses;
}

// ============================================
// TEST CASES
// ============================================
console.log(canFinish(2, [[1, 0]]));                          // true
console.log(canFinish(2, [[1, 0], [0, 1]]));                  // false
console.log(canFinish(4, [[1, 0], [2, 1], [3, 2]]));          // true
console.log(canFinish(3, [[0, 1], [1, 2], [2, 0]]));          // false
console.log(canFinishDFS(2, [[1, 0], [0, 1]]));               // false
console.log(canFinishDFS(5, [[1, 0], [2, 0], [3, 1], [3, 2]])); // true
console.log(canFinishBrute(2, [[1, 0], [0, 1]]));             // false
console.log(canFinish(1, []));                                // true
```

---

## 🔍 Why It Works
A course can only be taken once all its prerequisites are done, i.e. its in-degree hits 0. If a cycle exists, those nodes never reach in-degree 0, so the processed count stays below n. DFS detects the same cycle as a back edge to a node still on the recursion path.
हिंदी: cycle वाले nodes का in-degree कभी 0 नहीं होता, इसलिए count n से कम रह जाता है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Kahn's BFS | O(V + E) | O(V + E) |
| DFS 3-state | O(V + E) | O(V + E) |
| Repeated removal | O(V * (V + E)) | O(V + E) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Course Schedule II (LeetCode #210) — return the actual order
function findOrder(n, prerequisites) {
  const adj = Array.from({ length: n }, () => []);
  const indeg = Array(n).fill(0);
  for (const [a, b] of prerequisites) { adj[b].push(a); indeg[a]++; }
  const queue = [], order = [];
  for (let i = 0; i < n; i++) if (indeg[i] === 0) queue.push(i);
  while (queue.length) {
    const c = queue.shift();
    order.push(c);                                // record order
    for (const nx of adj[c]) if (--indeg[nx] === 0) queue.push(nx);
  }
  return order.length === n ? order : [];         // empty if cycle
}
console.log(findOrder(4, [[1, 0], [2, 0], [3, 1], [3, 2]])); // [0, 1, 2, 3]
console.log(findOrder(2, [[1, 0], [0, 1]]));                  // []

// VARIANT 2: Alien Dictionary (#269), Parallel Courses (#1136), Minimum Height Trees (#310)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: reversing the edge direction inconsistently ([a,b] means b -> a)
// ❌ Wrong: DFS with a plain visited set — flags diamond shapes as cycles
//    (A->B, A->C, B->D, C->D is NOT a cycle)
// ✅ Correct: use 3 states, or track the current recursion path separately

// ❌ Wrong: only starting DFS from node 0 — graph may be disconnected
```

---

## 🎯 Interview Tip
Say: "Cycle detection in a directed graph = topological sort feasibility." Present Kahn's algorithm first (easy to explain), then DFS colouring. Mention Course Schedule II returns the order.

---

## 🔗 Related Problems
→ D177 (Graph Valid Tree / Cycle Detection) | D173 (Clone Graph) | D172 (Number of Islands) | D176 (Word Ladder)
