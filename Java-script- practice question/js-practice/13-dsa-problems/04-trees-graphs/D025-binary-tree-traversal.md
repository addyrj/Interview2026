---

# D025. Binary Tree Traversals
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | Asked: Amazon, Microsoft, Goldman Sachs, Atlassian

---

## ❓ Problem
Implement all three DFS traversals (inorder, preorder, postorder) and BFS (level order) traversal for a binary tree — both recursive and iterative.

```
Tree:     1
         / \
        2   3
       / \   \
      4   5   6

InOrder:    [4, 2, 5, 1, 3, 6]  (Left → Root → Right)
PreOrder:   [1, 2, 4, 5, 3, 6]  (Root → Left → Right)
PostOrder:  [4, 5, 2, 6, 3, 1]  (Left → Right → Root)
LevelOrder: [[1], [2,3], [4,5,6]]
```

---

## 💡 Quick Concept (2 lines only)
DFS uses recursion or a stack. BFS uses a queue. InOrder of BST gives sorted order — very useful property. Level order uses queue: process row by row.
हिंदी: DFS = recursion/stack; BFS = queue। BST का InOrder sorted होता है — यह important property है।

---

## ✅ Solution

```javascript
// ============================================
// TreeNode class
// ============================================

class TreeNode {
  constructor(val, left = null, right = null) {
    this.val = val; this.left = left; this.right = right;
  }
}

// Build tree from array (level-order):
function buildTree(arr) {
  if (!arr || !arr.length) return null;
  const root = new TreeNode(arr[0]);
  const queue = [root];
  let i = 1;
  while (queue.length && i < arr.length) {
    const node = queue.shift();
    if (arr[i] != null) { node.left = new TreeNode(arr[i]); queue.push(node.left); }
    i++;
    if (i < arr.length && arr[i] != null) { node.right = new TreeNode(arr[i]); queue.push(node.right); }
    i++;
  }
  return root;
}

// ============================================
// 1. INORDER: Left → Root → Right
// ============================================

// Recursive:
function inorder(root) {
  if (!root) return [];
  return [...inorder(root.left), root.val, ...inorder(root.right)];
}

// Iterative (stack):
function inorderIterative(root) {
  const result = [], stack = [];
  let curr = root;
  
  while (curr || stack.length) {
    while (curr) {           // go as left as possible
      stack.push(curr);
      curr = curr.left;
    }
    curr = stack.pop();      // process node
    result.push(curr.val);
    curr = curr.right;       // move to right subtree
  }
  
  return result;
}

// ============================================
// 2. PREORDER: Root → Left → Right
// ============================================

function preorder(root) {
  if (!root) return [];
  return [root.val, ...preorder(root.left), ...preorder(root.right)];
}

function preorderIterative(root) {
  if (!root) return [];
  const result = [], stack = [root];
  
  while (stack.length) {
    const node = stack.pop();
    result.push(node.val);
    if (node.right) stack.push(node.right);  // push right FIRST (LIFO)
    if (node.left) stack.push(node.left);    // left processed first
  }
  
  return result;
}

// ============================================
// 3. POSTORDER: Left → Right → Root
// ============================================

function postorder(root) {
  if (!root) return [];
  return [...postorder(root.left), ...postorder(root.right), root.val];
}

function postorderIterative(root) {
  if (!root) return [];
  const result = [], stack = [root];
  
  while (stack.length) {
    const node = stack.pop();
    result.unshift(node.val);              // prepend (reverse preorder trick)
    if (node.left) stack.push(node.left);
    if (node.right) stack.push(node.right);
  }
  
  return result;
}

// ============================================
// 4. LEVEL ORDER (BFS): Row by row
// ============================================

function levelOrder(root) {
  if (!root) return [];
  const result = [], queue = [root];
  
  while (queue.length) {
    const levelSize = queue.length;   // nodes in current level
    const level = [];
    
    for (let i = 0; i < levelSize; i++) {
      const node = queue.shift();
      level.push(node.val);
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
    
    result.push(level);
  }
  
  return result;
}

// ============================================
// TEST CASES
// ============================================

const root = buildTree([1, 2, 3, 4, 5, null, 6]);
//       1
//      / \
//     2   3
//    / \    \
//   4   5    6

console.log(inorder(root));          // [4, 2, 5, 1, 3, 6]
console.log(preorder(root));         // [1, 2, 4, 5, 3, 6]
console.log(postorder(root));        // [4, 5, 2, 6, 3, 1]
console.log(levelOrder(root));       // [[1],[2,3],[4,5,6]]

// Verify iterative matches recursive:
console.log(inorderIterative(root)); // [4, 2, 5, 1, 3, 6] ✅
console.log(preorderIterative(root));// [1, 2, 4, 5, 3, 6] ✅
```

---

## 🔍 Key Properties
```
InOrder of BST = sorted ascending order ← VERY important
PreOrder = serialization of tree structure
PostOrder = used for deletion (delete children before parent)
LevelOrder = shortest path, BFS problems

When to use:
  Find kth smallest in BST → InOrder
  Clone a tree → PreOrder
  Delete a tree → PostOrder
  Minimum depth, connect level nodes → LevelOrder (BFS)
```
हिंदी: BST का InOrder = sorted; tree copy = PreOrder; tree delete = PostOrder; shortest path = LevelOrder।

---

## ⚡ Variations

```javascript
// VARIANT 1: Maximum depth of binary tree (LeetCode #104)
function maxDepth(root) {
  if (!root) return 0;
  return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}

// VARIANT 2: Symmetric tree / mirror (LeetCode #101)
function isSymmetric(root) {
  function isMirror(left, right) {
    if (!left && !right) return true;
    if (!left || !right) return false;
    return left.val === right.val &&
           isMirror(left.left, right.right) &&
           isMirror(left.right, right.left);
  }
  return isMirror(root.left, root.right);
}

// VARIANT 3: Binary tree right side view (LeetCode #199)
function rightSideView(root) {
  if (!root) return [];
  const result = [], queue = [root];
  while (queue.length) {
    const size = queue.length;
    for (let i = 0; i < size; i++) {
      const node = queue.shift();
      if (i === size - 1) result.push(node.val);  // last node in level
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
  }
  return result;
}
console.log(rightSideView(root));  // [1, 3, 6]

// VARIANT 4: Path sum (LeetCode #112)
function hasPathSum(root, target) {
  if (!root) return false;
  if (!root.left && !root.right) return root.val === target;  // leaf
  return hasPathSum(root.left, target - root.val) ||
         hasPathSum(root.right, target - root.val);
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: InOrder iterative — losing track of curr
while (stack.length) {       // wrong: misses case where curr has value but stack empty
  curr = stack.pop();
  // ...
}

// ✅ Correct: condition is curr OR stack.length
while (curr || stack.length) { ... }

// ❌ Wrong: LevelOrder without tracking level size
while (queue.length) {
  const node = queue.shift();
  // Can't tell where one level ends and next begins!
}
// ✅ Correct: capture queue.length BEFORE the inner for loop
const levelSize = queue.length;  // how many nodes are in this level
```

---

## 🎯 Interview Tip
Say: "Know all 4 traversals — recursive (2 lines each) AND iterative. InOrder of BST = sorted is frequently tested. Level order (BFS) is asked for: right side view, zigzag, connect level nodes, min depth."

---

## 🔗 Related Problems
→ D026 (BST Validate) | D027 (LCA) | D028 (Serialize/Deserialize) | D029 (Binary Tree Paths)
