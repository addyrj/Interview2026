---

# D173. Clone Graph
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #133 | Asked: Meta, Amazon, Google, Microsoft, Bloomberg

---

## ❓ Problem
Given a reference to a node in a connected undirected graph, return a deep copy (clone) of the graph. Each node has a value and a list of neighbors.

```
Adjacency list: [[2,4],[1,3],[2,4],[1,3]]

1 --- 2
|     |
4 --- 3

Output: a brand-new graph with the same shape (no node shared with the original)
```

---

## 💡 Quick Concept (2 lines only)
Keep a map old -> clone. Traverse (DFS/BFS); create the clone the first time you see a node, and reuse it afterwards — this also breaks cycles.
हिंदी: old -> clone का map रखो; पहली बार node मिले तो clone बनाओ, दोबारा मिले तो वही दे दो।

---

## ✅ Solution

```javascript
// Graph node
class Node {
  constructor(val, neighbors = []) {
    this.val = val; this.neighbors = neighbors;   // value + adjacent nodes
  }
}

// Build graph from adjacency list (1-indexed like LeetCode); returns node 1
function buildGraph(adj) {
  if (!adj.length) return null;                   // empty graph
  const nodes = adj.map((_, i) => new Node(i + 1)); // create all nodes first
  adj.forEach((list, i) => {
    nodes[i].neighbors = list.map(v => nodes[v - 1]); // wire neighbours
  });
  return nodes[0];
}

// Convert graph back to adjacency list (sorted by val) to inspect it
function toAdj(start) {
  if (!start) return [];                          // empty
  const seen = new Map(), stack = [start];        // val -> neighbours values
  seen.set(start.val, start);
  while (stack.length) {
    const n = stack.pop();
    for (const nb of n.neighbors) {
      if (!seen.has(nb.val)) { seen.set(nb.val, nb); stack.push(nb); } // discover
    }
  }
  return [...seen.values()]
    .sort((a, b) => a.val - b.val)                // order by value
    .map(n => n.neighbors.map(x => x.val));       // neighbour values
}

// ============================================
// APPROACH 1: DFS + HashMap (Optimal, common)
// Time: O(V + E) | Space: O(V)
// ============================================
function cloneGraph(node) {
  if (!node) return null;                         // empty graph
  const map = new Map();                          // original -> clone
  function dfs(n) {
    if (map.has(n)) return map.get(n);            // already cloned (handles cycles)
    const copy = new Node(n.val);                 // create clone
    map.set(n, copy);                             // register BEFORE recursing
    for (const nb of n.neighbors) copy.neighbors.push(dfs(nb)); // clone neighbours
    return copy;
  }
  return dfs(node);
}

// ============================================
// APPROACH 2: BFS + HashMap
// Time: O(V + E) | Space: O(V)
// ============================================
function cloneGraphBFS(node) {
  if (!node) return null;                         // empty graph
  const map = new Map([[node, new Node(node.val)]]); // start with clone of root
  const queue = [node];                           // BFS queue of originals
  while (queue.length) {
    const cur = queue.shift();                    // original node
    for (const nb of cur.neighbors) {
      if (!map.has(nb)) {                         // first visit
        map.set(nb, new Node(nb.val));            // create clone
        queue.push(nb);                           // explore later
      }
      map.get(cur).neighbors.push(map.get(nb));   // link clones
    }
  }
  return map.get(node);
}

// ============================================
// TEST CASES
// ============================================
const g = buildGraph([[2, 4], [1, 3], [2, 4], [1, 3]]);
const c1 = cloneGraph(g);
console.log(JSON.stringify(toAdj(c1)));           // [[2,4],[1,3],[2,4],[1,3]]
console.log(c1 !== g, c1.neighbors[0] !== g.neighbors[0]); // true true  (deep copy)
const c2 = cloneGraphBFS(g);
console.log(JSON.stringify(toAdj(c2)));           // [[2,4],[1,3],[2,4],[1,3]]
console.log(JSON.stringify(toAdj(cloneGraph(buildGraph([[]]))))); // [[]]
console.log(cloneGraph(buildGraph([])));          // null
console.log(JSON.stringify(toAdj(cloneGraph(buildGraph([[2], [1]]))))); // [[2],[1]]
```

---

## 🔍 Why It Works
The map guarantees one clone per original node, so cycles cannot cause infinite recursion and shared neighbours point to the same clone. Registering the clone BEFORE exploring its neighbours is what stops the loop.
हिंदी: हर original का सिर्फ एक clone; recursion से पहले map में डालना ज़रूरी है ताकि cycle न फँसे।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| DFS + map | O(V + E) | O(V) map + O(V) recursion |
| BFS + map | O(V + E) | O(V) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Copy List with Random Pointer (LeetCode #138) — same old->clone map idea
// VARIANT 2: Clone N-ary tree / Clone binary tree with random pointer (#1485)
// VARIANT 3: Count nodes reachable (sanity check) — use the same traversal
function countNodes(start) { return toAdj(start).length; }
console.log(countNodes(g));                       // 4
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no visited map -> infinite recursion on cycles
// ❌ Wrong: storing the clone in the map AFTER the recursive calls
const copy = new Node(n.val);
for (const nb of n.neighbors) copy.neighbors.push(dfs(nb)); // may revisit n before it is in map
map.set(n, copy);

// ❌ Wrong: pushing ORIGINAL neighbours into the clone (shallow copy)
// ✅ Correct: map.set(n, copy) first, then clone neighbours
```

---

## 🎯 Interview Tip
Say: "HashMap from original to clone doubles as the visited set." Mention both DFS and BFS, handle the null / single-node cases, and verify no cloned node references an original.

---

## 🔗 Related Problems
→ D172 (Number of Islands) | D174 (Course Schedule) | D177 (Graph Valid Tree) | D176 (Word Ladder)
