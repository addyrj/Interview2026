---

# D164. Validate Binary Search Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #98 | Asked: Amazon, Microsoft, Meta, Google, Bloomberg

---

## ❓ Problem
Given the root of a binary tree, determine whether it is a valid BST: for every node, all values in its left subtree are strictly smaller and all values in its right subtree are strictly larger (and both subtrees are BSTs).

```
Valid:     2        Invalid:    5
          / \                  / \
         1   3                1   6
                                 / \
                                3   7   <- 3 is in right subtree of 5 but < 5
```

---

## 💡 Quick Concept (2 lines only)
Carry an allowed (min, max) range down the tree; each node must lie strictly inside it. Alternative: inorder traversal must be strictly increasing.
हिंदी: हर node के लिए (min, max) range रखो; या inorder sorted (strictly increasing) होना चाहिए।

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
// APPROACH 1 (Brute force / WRONG idea shown): check only parent-child
// Fails for tree [5,1,6,null,null,3,7] -> returns true incorrectly
// ============================================
function isValidBSTWrong(root) {
  if (!root) return true;                         // empty ok
  if (root.left && root.left.val >= root.val) return false;   // only local check
  if (root.right && root.right.val <= root.val) return false; // misses deep violations
  return isValidBSTWrong(root.left) && isValidBSTWrong(root.right);
}

// ============================================
// APPROACH 2: Range (min/max) recursion (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function isValidBST(root, min = -Infinity, max = Infinity) {
  if (!root) return true;                         // empty subtree is valid
  if (root.val <= min || root.val >= max) return false; // outside allowed range
  return isValidBST(root.left, min, root.val) &&  // left must be < this node
         isValidBST(root.right, root.val, max);   // right must be > this node
}

// ============================================
// APPROACH 3: Iterative inorder, values must strictly increase
// Time: O(n) | Space: O(h)
// ============================================
function isValidBSTInorder(root) {
  const stack = [];                               // explicit stack
  let curr = root, prev = -Infinity;              // prev = last visited value
  while (curr || stack.length) {
    while (curr) { stack.push(curr); curr = curr.left; } // go far left
    curr = stack.pop();                           // visit node
    if (curr.val <= prev) return false;           // not strictly increasing
    prev = curr.val;                              // remember value
    curr = curr.right;                            // go right
  }
  return true;
}

// ============================================
// TEST CASES
// ============================================
const valid = buildTree([2, 1, 3]);
const invalid = buildTree([5, 1, 6, null, null, 3, 7]);
console.log(isValidBST(valid));                 // true
console.log(isValidBST(invalid));               // false
console.log(isValidBSTInorder(valid));          // true
console.log(isValidBSTInorder(invalid));        // false
console.log(isValidBSTWrong(invalid));          // true  (WRONG answer — shows why local check fails)
console.log(isValidBST(buildTree([2, 2, 2])));  // false (duplicates not allowed)
console.log(isValidBST(buildTree([5, 4, 6, null, null, 3, 7]))); // false
console.log(isValidBST(null));                  // true
```

---

## 🔍 Why It Works
A node's valid values are constrained by ALL its ancestors, not just its parent. Going left tightens the upper bound to the parent's value; going right tightens the lower bound. Inorder of a BST is strictly sorted, so any dip reveals a violation.
हिंदी: सिर्फ parent नहीं, सभी ancestors की limit लगती है - इसलिए range पास करते हैं।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Local check (wrong) | O(n) | O(h) |
| Range recursion | O(n) | O(h) |
| Inorder iterative | O(n) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Allow duplicates on the left (<=) — change comparisons accordingly
function isValidBSTDupLeft(root, min = -Infinity, max = Infinity) {
  if (!root) return true;                         // empty ok
  if (root.val <= min || root.val > max) return false; // left may equal parent (max inclusive)
  return isValidBSTDupLeft(root.left, min, root.val) &&
         isValidBSTDupLeft(root.right, root.val, max);
}
console.log(isValidBSTDupLeft(buildTree([2, 2])));  // true

// VARIANT 2: Recover BST with two swapped nodes (LeetCode #99) — inorder, find two dips
// VARIANT 3: Largest BST subtree (LeetCode #333) — return (isBST, size, min, max) bottom-up
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: compare node only with its direct children
if (root.left.val < root.val && root.right.val > root.val) ...

// ❌ Wrong: initial bounds as Number.MIN_VALUE (smallest POSITIVE number!) or INT_MIN
//    that breaks when a node equals the sentinel
// ✅ Correct: use -Infinity / Infinity (or null bounds)

// ❌ Wrong: using <= vs < inconsistently — decide how duplicates are handled
```

---

## 🎯 Interview Tip
Say: "A local parent-child check is not enough; I pass down a valid range." Mention the inorder-strictly-increasing alternative and ask how duplicates should be treated.

---

## 🔗 Related Problems
→ D165 (LCA of BST) | D170 (Kth Smallest in BST) | D025 (Traversals) | D166 (LCA Binary Tree)
