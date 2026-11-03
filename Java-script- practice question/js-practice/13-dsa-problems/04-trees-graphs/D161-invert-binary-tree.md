---

# D161. Invert Binary Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #226 | Asked: Google, Amazon, Microsoft, Apple

---

## ❓ Problem
Given the root of a binary tree, invert (mirror) it — swap left and right children at every node — and return the root.

```
Input:       4                Output:      4
           /   \                         /   \
          2     7                       7     2
         / \   / \                     / \   / \
        1   3 6   9                   9   6 3   1
```

---

## 💡 Quick Concept (2 lines only)
At every node swap its two children, then recurse (or loop) into both subtrees. Order of swap vs recursion does not matter.
हिंदी: हर node पर left और right बदलो, फिर दोनों subtrees में यही दोहराओ।

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

// Level-order array (for printing); trims trailing nulls
function toArray(root) {
  const out = [], queue = [root];                 // BFS including nulls
  while (queue.length) {
    const n = queue.shift();                      // next slot
    if (n) { out.push(n.val); queue.push(n.left, n.right); } // real node
    else out.push(null);                          // missing node
  }
  while (out.length && out[out.length - 1] === null) out.pop(); // trim trailing nulls
  return out;
}

// ============================================
// APPROACH 1: Recursive DFS (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function invertTree(root) {
  if (!root) return null;                         // base case
  const left = invertTree(root.left);             // invert left subtree
  const right = invertTree(root.right);           // invert right subtree
  root.left = right;                              // swap: left gets inverted right
  root.right = left;                              // right gets inverted left
  return root;
}

// ============================================
// APPROACH 2: Iterative BFS (queue)
// Time: O(n) | Space: O(w)
// ============================================
function invertTreeBFS(root) {
  if (!root) return null;                         // empty tree
  const queue = [root];                           // start from root
  while (queue.length) {
    const node = queue.shift();                   // process node
    [node.left, node.right] = [node.right, node.left]; // swap children
    if (node.left) queue.push(node.left);         // continue with children
    if (node.right) queue.push(node.right);
  }
  return root;
}

// ============================================
// APPROACH 3: Iterative DFS (stack)
// Time: O(n) | Space: O(h)
// ============================================
function invertTreeStack(root) {
  if (!root) return null;                         // empty tree
  const stack = [root];                           // LIFO stack
  while (stack.length) {
    const node = stack.pop();                     // take node
    const tmp = node.left;                        // classic swap
    node.left = node.right;
    node.right = tmp;
    if (node.left) stack.push(node.left);         // visit children later
    if (node.right) stack.push(node.right);
  }
  return root;
}

// ============================================
// TEST CASES
// ============================================
console.log(toArray(invertTree(buildTree([4, 2, 7, 1, 3, 6, 9]))));      // [4,7,2,9,6,3,1]
console.log(toArray(invertTreeBFS(buildTree([4, 2, 7, 1, 3, 6, 9]))));   // [4,7,2,9,6,3,1]
console.log(toArray(invertTreeStack(buildTree([4, 2, 7, 1, 3, 6, 9])))); // [4,7,2,9,6,3,1]
console.log(toArray(invertTree(buildTree([2, 1, 3]))));                  // [2,3,1]
console.log(toArray(invertTree(buildTree([1, 2]))));                     // [1,null,2]
console.log(invertTree(null));                                           // null
```

---

## 🔍 Why It Works
A mirror image of a tree is: swap the two children, and mirror each child as well. This definition is itself recursive, so each node needs only O(1) work.
हिंदी: Mirror की परिभाषा ही recursive है - हर node पर O(1) swap।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Recursive | O(n) | O(h) |
| BFS | O(n) | O(w) |
| Iterative DFS | O(n) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Check if two trees are mirror images of each other
function isMirror(a, b) {
  if (!a && !b) return true;                      // both empty
  if (!a || !b) return false;                     // shape differs
  return a.val === b.val &&                       // same value
         isMirror(a.left, b.right) &&             // outer pair
         isMirror(a.right, b.left);               // inner pair
}
console.log(isMirror(buildTree([1, 2, 3]), buildTree([1, 3, 2]))); // true

// VARIANT 2: Flip binary tree upside down (LeetCode #156, premium) — same swap idea
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: overwriting left before saving it
root.left = invertTree(root.right);
root.right = invertTree(root.left);   // root.left is already the NEW left!

// ✅ Correct: save both results first, then assign
const left = invertTree(root.left);
const right = invertTree(root.right);
root.left = right; root.right = left;
```

---

## 🎯 Interview Tip
Say: "Swap children at every node, recursing both sides; O(n) time, O(h) space." Famous because even strong engineers are expected to solve this instantly — write it cleanly and mention the iterative BFS alternative.

---

## 🔗 Related Problems
→ D160 (Max Depth) | D162 (Same Tree) | D163 (Symmetric Tree) | D025 (Tree Traversals)
