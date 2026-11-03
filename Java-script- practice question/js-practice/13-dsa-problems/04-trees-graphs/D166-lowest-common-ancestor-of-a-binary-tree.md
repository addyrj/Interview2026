---

# D166. Lowest Common Ancestor of a Binary Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #236 | Asked: Amazon, Meta, Microsoft, Google, LinkedIn

---

## ❓ Problem
Given a binary tree (not necessarily a BST) and two nodes `p` and `q`, return their lowest common ancestor. A node may be an ancestor of itself.

```
Tree:        3
           /   \
          5     1
         / \   / \
        6   2 0   8
           / \
          7   4

LCA(5, 1) = 3
LCA(5, 4) = 5
LCA(7, 4) = 2
```

---

## 💡 Quick Concept (2 lines only)
Post-order DFS: return the node if it is p or q; if both left and right searches return non-null, current node is the LCA; else pass up whichever is non-null.
हिंदी: दोनों तरफ से कुछ मिले तो यही node LCA; वरना जो मिला उसे ऊपर भेजो।

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

// Find node by value (helper for tests)
function find(root, v) {
  if (!root) return null;                         // not here
  if (root.val === v) return root;                // found
  return find(root.left, v) || find(root.right, v); // search children
}

// ============================================
// APPROACH 1 (Brute force): root-to-node paths, last common node
// Time: O(n) | Space: O(n)
// ============================================
function findPath(root, target, path) {
  if (!root) return false;                        // dead end
  path.push(root);                                // tentatively add node
  if (root === target) return true;               // found target
  if (findPath(root.left, target, path) || findPath(root.right, target, path)) return true;
  path.pop();                                     // backtrack: not on this path
  return false;
}
function lcaPaths(root, p, q) {
  const a = [], b = [];                           // two paths
  findPath(root, p, a); findPath(root, q, b);     // fill both
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++; // common prefix
  return a[i - 1];                                // last shared node
}

// ============================================
// APPROACH 2: Single-pass post-order DFS (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function lowestCommonAncestor(root, p, q) {
  if (!root || root === p || root === q) return root; // found a target or hit null
  const left = lowestCommonAncestor(root.left, p, q);   // search left
  const right = lowestCommonAncestor(root.right, p, q); // search right
  if (left && right) return root;                 // targets on different sides: LCA
  return left || right;                           // otherwise bubble up non-null side
}

// ============================================
// APPROACH 3: Parent pointers + ancestor set
// Time: O(n) | Space: O(n)
// ============================================
function lcaParents(root, p, q) {
  const parent = new Map([[root, null]]);         // child -> parent
  const stack = [root];                           // traverse whole tree
  while (stack.length) {
    const n = stack.pop();
    for (const c of [n.left, n.right]) {
      if (c) { parent.set(c, n); stack.push(c); } // record parent
    }
  }
  const anc = new Set();                          // ancestors of p
  for (let x = p; x; x = parent.get(x)) anc.add(x);
  let y = q;                                      // climb from q
  while (!anc.has(y)) y = parent.get(y);          // first shared ancestor
  return y;
}

// ============================================
// TEST CASES
// ============================================
const root = buildTree([3, 5, 1, 6, 2, 0, 8, null, null, 7, 4]);
const n = v => find(root, v);
console.log(lowestCommonAncestor(root, n(5), n(1)).val); // 3
console.log(lowestCommonAncestor(root, n(5), n(4)).val); // 5
console.log(lowestCommonAncestor(root, n(7), n(4)).val); // 2
console.log(lcaPaths(root, n(6), n(4)).val);             // 5
console.log(lcaParents(root, n(0), n(8)).val);           // 1
console.log(lcaParents(root, n(6), n(8)).val);           // 3
```

---

## 🔍 Why It Works
The recursion returns "a target found in this subtree" (or null). If both children report a hit, p and q live in different subtrees, so the current node is the deepest node containing both. If only one side reports, both targets are on that side (or the returned node is an ancestor of the other target), so we pass it up. This assumes both nodes exist.
हिंदी: दोनों side से hit आए तो वहीं split है = LCA; एक ही side से आए तो उसे ऊपर पास करो।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Path comparison | O(n) | O(n) |
| Post-order DFS | O(n) | O(h) |
| Parent map | O(n) | O(n) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Nodes may be missing (LeetCode #1644) — count how many targets were found
function lcaMaybeMissing(root, p, q) {
  let found = 0;                                  // count of targets seen
  function dfs(node) {
    if (!node) return null;                       // empty
    const l = dfs(node.left), r = dfs(node.right); // search children first
    if (node === p || node === q) { found++; return node; } // count after children
    return l && r ? node : l || r;                // same logic as main solution
  }
  const res = dfs(root);
  return found === 2 ? res : null;                // both must exist
}
console.log(lcaMaybeMissing(root, n(5), new TreeNode(99))); // null

// VARIANT 2: LCA of deepest leaves (LeetCode #1123) — return (depth, node) pairs bottom-up
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing values instead of node references when values may repeat
if (root.val === p.val) ...   // fine if unique; compare references when unsure

// ❌ Wrong: forgetting to return when root is p or q — the other target may lie below it,
//   returning early is correct because root then IS the LCA

// ❌ Wrong: using the BST shortcut (value comparison) on a normal binary tree
```

---

## 🎯 Interview Tip
Say: "One post-order pass; return a node if it is p or q; split means LCA." State the assumption that both nodes exist and mention the parent-map alternative.

---

## 🔗 Related Problems
→ D165 (LCA of BST) | D168 (Diameter) | D025 (Traversals) | D169 (Path Sum)
