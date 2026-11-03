---

# D167. Binary Tree Level Order Traversal
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #102 | Asked: Amazon, Microsoft, Meta, Google, Apple

---

## ❓ Problem
Given the root of a binary tree, return the level order traversal of its nodes' values (left to right, level by level).

```
Tree:     3
         / \
        9  20
           / \
          15  7

Output: [[3], [9, 20], [15, 7]]
```

---

## 💡 Quick Concept (2 lines only)
BFS with a queue. At each round, take a snapshot of the queue length — that many nodes form exactly one level.
हिंदी: BFS + queue; हर round में queue की current length = उस level के nodes की संख्या।

---

## ✅ Solution

```javascript
// TreeNode class
class TreeNode {
  constructor(val, left = null, right = null) {
    this.val = val; this.left = left; this.right = right; // value + children
  }
}

// Build tree from level-order array
function buildTree(arr) {
  if (!arr || !arr.length) return null;           // empty tree
  const root = new TreeNode(arr[0]);              // root node
  const queue = [root];                           // parents waiting for children
  let i = 1;                                      // next value index
  while (queue.length && i < arr.length) {
    const node = queue.shift();                   // next parent
    if (arr[i] != null) { node.left = new TreeNode(arr[i]); queue.push(node.left); }
    i++;
    if (i < arr.length && arr[i] != null) { node.right = new TreeNode(arr[i]); queue.push(node.right); }
    i++;
  }
  return root;
}

// ============================================
// APPROACH 1 (Brute force-ish): DFS with depth, push into result[depth]
// Time: O(n) | Space: O(h) + output
// ============================================
function levelOrderDFS(root) {
  const result = [];                              // result[d] = values at depth d
  function dfs(node, d) {
    if (!node) return;                            // nothing to do
    if (result.length === d) result.push([]);     // first time reaching depth d
    result[d].push(node.val);                     // add value to its level
    dfs(node.left, d + 1);                        // left first keeps left-to-right order
    dfs(node.right, d + 1);
  }
  dfs(root, 0);
  return result;
}

// ============================================
// APPROACH 2: BFS with level size snapshot (Optimal / standard)
// Time: O(n) | Space: O(w)
// ============================================
function levelOrder(root) {
  if (!root) return [];                           // empty tree
  const result = [], queue = [root];              // queue starts with root
  while (queue.length) {
    const size = queue.length;                    // nodes in this level
    const level = [];                             // values for this level
    for (let i = 0; i < size; i++) {
      const node = queue.shift();                 // pop next node
      level.push(node.val);                       // record value
      if (node.left) queue.push(node.left);       // enqueue next level
      if (node.right) queue.push(node.right);
    }
    result.push(level);                           // level finished
  }
  return result;
}

// ============================================
// TEST CASES
// ============================================
const t = buildTree([3, 9, 20, null, null, 15, 7]);
console.log(JSON.stringify(levelOrder(t)));       // [[3],[9,20],[15,7]]
console.log(JSON.stringify(levelOrderDFS(t)));    // [[3],[9,20],[15,7]]
console.log(JSON.stringify(levelOrder(buildTree([1]))));       // [[1]]
console.log(JSON.stringify(levelOrder(null)));                 // []
console.log(JSON.stringify(levelOrder(buildTree([1, 2, 3, 4, 5])))); // [[1],[2,3],[4,5]]
```

---

## 🔍 Why It Works
A queue processes nodes in FIFO order, so all nodes of depth d leave before any of depth d+1. Reading `queue.length` before the inner loop freezes the boundary between the current level and the children being added.
हिंदी: FIFO की वजह से level-by-level order मिलता है; size पहले ले लो ताकि boundary पता रहे।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| DFS with depth | O(n) | O(h) |
| BFS | O(n) | O(w) |

Note: `Array.shift()` is O(n) in theory; use an index pointer for very large trees.

---

## ⚡ Variations

```javascript
// VARIANT 1: Zigzag level order (LeetCode #103)
function zigzag(root) {
  const res = levelOrder(root);                   // normal levels
  return res.map((lvl, i) => (i % 2 ? lvl.reverse() : lvl)); // reverse odd levels
}
console.log(JSON.stringify(zigzag(t)));           // [[3],[20,9],[15,7]]

// VARIANT 2: Right side view (LeetCode #199) — last of each level
const rightView = root => levelOrder(root).map(l => l[l.length - 1]);
console.log(rightView(t));                        // [3, 20, 7]

// VARIANT 3: Bottom-up level order (LeetCode #107)
console.log(JSON.stringify(levelOrder(t).reverse())); // [[15,7],[9,20],[3]]

// VARIANT 4: Average of each level (LeetCode #637)
const avg = root => levelOrder(root).map(l => l.reduce((a, b) => a + b, 0) / l.length);
console.log(avg(t));                              // [3, 14.5, 11]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: loop `i < queue.length` — length changes as children are pushed
for (let i = 0; i < queue.length; i++) { ... }

// ✅ Correct: freeze the size first
const size = queue.length;
for (let i = 0; i < size; i++) { ... }

// ❌ Wrong: forgetting the empty-root check -> queue = [null] and crash on node.val
```

---

## 🎯 Interview Tip
Say: "BFS, snapshot the queue size per level." This single template solves zigzag, right-side view, averages, min depth, and connect-next-pointers — mention that to show pattern recognition.

---

## 🔗 Related Problems
→ D025 (Traversals) | D160 (Max Depth) | D175 (Rotting Oranges - BFS) | D176 (Word Ladder - BFS)
