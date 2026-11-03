---

# D165. Lowest Common Ancestor of a BST
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #235 | Asked: Amazon, Microsoft, Facebook, Google

---

## ❓ Problem
Given a BST and two nodes `p` and `q`, find their lowest common ancestor — the lowest node that has both p and q as descendants (a node can be a descendant of itself).

```
BST:        6
          /   \
         2     8
        / \   / \
       0   4 7   9
          / \
         3   5

LCA(2, 8) = 6
LCA(2, 4) = 2   (node can be its own descendant)
```

---

## 💡 Quick Concept (2 lines only)
Use the BST order: if both values are smaller than the node go left; if both larger go right; otherwise the current node is the split point = LCA.
हिंदी: दोनों छोटे तो left, दोनों बड़े तो right, वरना यही node LCA है।

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

// Find node by value in BST (helper for tests)
function find(root, v) {
  while (root && root.val !== v) root = v < root.val ? root.left : root.right; // BST search
  return root;
}

// ============================================
// APPROACH 1 (Brute force): store root-to-node paths, find last common
// Time: O(h) | Space: O(h)
// ============================================
function pathTo(root, target) {
  const path = [];                                // nodes on the way
  let cur = root;
  while (cur) {
    path.push(cur);                               // record node
    if (cur.val === target.val) break;            // reached target
    cur = target.val < cur.val ? cur.left : cur.right; // follow BST order
  }
  return path;
}
function lcaPaths(root, p, q) {
  const a = pathTo(root, p), b = pathTo(root, q); // two paths from root
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++; // walk while same
  return a[i - 1];                                // last shared node
}

// ============================================
// APPROACH 2: Iterative BST walk (Optimal)
// Time: O(h) | Space: O(1)
// ============================================
function lowestCommonAncestor(root, p, q) {
  let cur = root;                                 // start at root
  while (cur) {
    if (p.val < cur.val && q.val < cur.val) cur = cur.left;       // both in left
    else if (p.val > cur.val && q.val > cur.val) cur = cur.right; // both in right
    else return cur;                              // split (or equal): this is LCA
  }
  return null;                                    // not found
}

// ============================================
// APPROACH 3: Recursive version
// Time: O(h) | Space: O(h)
// ============================================
function lcaRecursive(root, p, q) {
  if (p.val < root.val && q.val < root.val) return lcaRecursive(root.left, p, q);   // go left
  if (p.val > root.val && q.val > root.val) return lcaRecursive(root.right, p, q);  // go right
  return root;                                    // split point
}

// ============================================
// TEST CASES
// ============================================
const root = buildTree([6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]);
console.log(lowestCommonAncestor(root, find(root, 2), find(root, 8)).val); // 6
console.log(lowestCommonAncestor(root, find(root, 2), find(root, 4)).val); // 2
console.log(lowestCommonAncestor(root, find(root, 3), find(root, 5)).val); // 4
console.log(lcaRecursive(root, find(root, 0), find(root, 5)).val);         // 2
console.log(lcaPaths(root, find(root, 7), find(root, 9)).val);             // 8
console.log(lcaPaths(root, find(root, 3), find(root, 9)).val);             // 6
```

---

## 🔍 Why It Works
In a BST everything left of a node is smaller and everything right is larger. The first node whose value lies between p and q (inclusive) separates them into different subtrees (or equals one of them), so no lower node can contain both.
हिंदी: जहाँ p और q अलग-अलग तरफ जाने लगें (या एक बराबर हो), वहीं LCA है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Path comparison | O(h) | O(h) |
| Iterative walk | O(h) | O(1) |
| Recursive | O(h) | O(h) |

h = O(log n) balanced, O(n) skewed.

---

## ⚡ Variations

```javascript
// VARIANT 1: Distance between two nodes in a BST = depth(p) + depth(q) - 2*depth(lca)
function depth(root, node) {
  let d = 0, cur = root;
  while (cur !== node) { cur = node.val < cur.val ? cur.left : cur.right; d++; } // count steps
  return d;
}
function distance(root, p, q) {
  const l = lowestCommonAncestor(root, p, q);     // find LCA
  return depth(l, p) + depth(l, q);               // steps from LCA to each
}
console.log(distance(root, find(root, 3), find(root, 9))); // 5
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using the general binary-tree LCA (O(n)) and ignoring BST order
// ❌ Wrong: stopping only when cur equals p or q — misses the split case
// ✅ Correct: any node not strictly on one side of both is the LCA
```

---

## 🎯 Interview Tip
Say: "BST property lets me discard half the tree each step: O(h) time, O(1) space iteratively." Always clarify that a node may be its own ancestor.

---

## 🔗 Related Problems
→ D166 (LCA of Binary Tree) | D164 (Validate BST) | D170 (Kth Smallest in BST) | D025 (Traversals)
