---

# D177. Graph Valid Tree / Cycle Detection
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #261 (Premium) | Asked: Google, Amazon, Meta, LinkedIn, Pinterest

---

## ❓ Problem
Given `n` nodes labeled `0..n-1` and a list of undirected `edges`, decide whether the edges form a valid tree. Also learn how to detect a cycle in an undirected graph.

```
n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]  -> true
n = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]] -> false  (cycle 1-2-3)
n = 4, edges = [[0,1],[2,3]] -> false (disconnected)
```

---

## 💡 Quick Concept (2 lines only)
A graph is a tree iff it is connected and has no cycle — equivalently, it has exactly n - 1 edges AND is connected (or acyclic).
हिंदी: tree = connected + no cycle = exactly n-1 edges और सब nodes जुड़े हुए।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Union-Find (Optimal, clean)
// Time: O(E * α(n)) | Space: O(n)
// ============================================
function validTree(n, edges) {
  if (edges.length !== n - 1) return false;       // tree needs exactly n-1 edges
  const parent = Array.from({ length: n }, (_, i) => i); // each node its own set
  const find = x => {
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];              // path halving
      x = parent[x];
    }
    return x;
  };
  for (const [a, b] of edges) {
    const ra = find(a), rb = find(b);             // roots of both endpoints
    if (ra === rb) return false;                  // already connected -> cycle
    parent[ra] = rb;                              // union the two sets
  }
  return true;                                    // n-1 edges, no cycle -> connected tree
}

// ============================================
// APPROACH 2: DFS — check connectivity + cycle via parent tracking
// Time: O(n + E) | Space: O(n + E)
// ============================================
function validTreeDFS(n, edges) {
  if (edges.length !== n - 1) return false;       // quick reject
  const adj = Array.from({ length: n }, () => []);
  for (const [a, b] of edges) { adj[a].push(b); adj[b].push(a); } // undirected
  const seen = new Set();                         // visited nodes
  function dfs(node, par) {
    if (seen.has(node)) return false;             // reached again -> cycle
    seen.add(node);                               // mark visited
    for (const nb of adj[node]) {
      if (nb === par) continue;                   // skip the edge we came from
      if (!dfs(nb, node)) return false;           // cycle found deeper
    }
    return true;
  }
  return dfs(0, -1) && seen.size === n;           // no cycle AND all nodes reached
}

// ============================================
// APPROACH 3: BFS connectivity (with n-1 edges check)
// Time: O(n + E) | Space: O(n + E)
// ============================================
function validTreeBFS(n, edges) {
  if (edges.length !== n - 1) return false;       // n-1 edges required
  const adj = Array.from({ length: n }, () => []);
  for (const [a, b] of edges) { adj[a].push(b); adj[b].push(a); }
  const seen = new Set([0]), queue = [0];         // start from node 0
  while (queue.length) {
    const u = queue.shift();
    for (const v of adj[u]) {
      if (!seen.has(v)) { seen.add(v); queue.push(v); } // explore
    }
  }
  return seen.size === n;                         // n-1 edges + connected => tree
}

// ============================================
// TEST CASES
// ============================================
console.log(validTree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]));         // true
console.log(validTree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]])); // false
console.log(validTree(4, [[0, 1], [2, 3]]));                         // false
console.log(validTreeDFS(5, [[0, 1], [0, 2], [0, 3], [1, 4]]));      // true
console.log(validTreeDFS(4, [[0, 1], [1, 2], [2, 0]]));              // false
console.log(validTreeBFS(5, [[0, 1], [0, 2], [0, 3], [1, 4]]));      // true
console.log(validTreeBFS(4, [[0, 1], [2, 3], [2, 3]]));              // false
console.log(validTree(1, []));                                       // true
```

---

## 🔍 Why It Works
A connected graph with n nodes needs at least n - 1 edges; with exactly n - 1 it cannot contain a cycle. Union-Find detects a cycle the moment an edge joins two nodes already in the same set. With n - 1 edges and no cycle, the graph must also be connected.
हिंदी: n-1 edges और कोई cycle नहीं = automatically connected tree।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Union-Find | O(E * α(n)) | O(n) |
| DFS | O(n + E) | O(n + E) |
| BFS | O(n + E) | O(n + E) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Detect cycle in an undirected graph (any graph)
function hasCycleUndirected(n, edges) {
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = x => (parent[x] === x ? x : (parent[x] = find(parent[x]))); // path compression
  for (const [a, b] of edges) {
    const ra = find(a), rb = find(b);
    if (ra === rb) return true;                   // edge inside same component
    parent[ra] = rb;                              // union
  }
  return false;
}
console.log(hasCycleUndirected(4, [[0, 1], [1, 2], [2, 0]]));        // true
console.log(hasCycleUndirected(4, [[0, 1], [1, 2]]));                // false

// VARIANT 2: Number of Connected Components (LeetCode #323)
function countComponents(n, edges) {
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = x => (parent[x] === x ? x : (parent[x] = find(parent[x])));
  let comps = n;                                  // start with n singletons
  for (const [a, b] of edges) {
    const ra = find(a), rb = find(b);
    if (ra !== rb) { parent[ra] = rb; comps--; }  // merge reduces components
  }
  return comps;
}
console.log(countComponents(5, [[0, 1], [1, 2], [3, 4]]));           // 2

// VARIANT 3: Redundant Connection (#684) — return the edge that closes the cycle
// VARIANT 4: DIRECTED graph cycle detection -> see D174 (Course Schedule)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: DFS cycle check that does not skip the parent
//    undirected edge A-B looks like a cycle (B sees A as "visited")
// ✅ Correct: pass parent and skip it

// ❌ Wrong: checking only for a cycle — a forest (disconnected) has no cycle but is not a tree
// ❌ Wrong: using directed-graph (3-colour) logic for an undirected graph
```

---

## 🎯 Interview Tip
Say: "Tree <=> exactly n-1 edges and connected (or acyclic)." Start with the edge-count shortcut, then Union-Find. Distinguish undirected (parent skip / DSU) from directed cycle detection (D174).

---

## 🔗 Related Problems
→ D174 (Course Schedule) | D173 (Clone Graph) | D172 (Number of Islands) | D175 (Rotting Oranges)
