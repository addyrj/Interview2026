---

# D170. Kth Smallest Element in a BST
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #230 | Asked: Amazon, Microsoft, Google, Uber, Meta

---

## ❓ Problem
Given the root of a BST and an integer `k`, return the k-th smallest value (1-indexed) among all node values.

```
BST:      3
         / \
        1   4
         \
          2

k = 1 -> 1
k = 3 -> 3
```

---

## 💡 Quick Concept (2 lines only)
Inorder traversal of a BST visits values in ascending order. Stop as soon as you have visited k nodes.
हिंदी: BST का inorder sorted होता है; k-वें node पर रुक जाओ।

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
// APPROACH 1 (Brute force): full inorder array, then index k-1
// Time: O(n) | Space: O(n)
// ============================================
function kthSmallestBrute(root, k) {
  const arr = [];                                 // all values sorted
  function inorder(n) {
    if (!n) return;                               // nothing
    inorder(n.left);                              // smaller values first
    arr.push(n.val);                              // current
    inorder(n.right);                             // larger values after
  }
  inorder(root);
  return arr[k - 1];                              // 1-indexed -> 0-indexed
}

// ============================================
// APPROACH 2: Iterative inorder with early stop (Optimal)
// Time: O(h + k) | Space: O(h)
// ============================================
function kthSmallest(root, k) {
  const stack = [];                               // explicit stack
  let curr = root;                                // current pointer
  while (curr || stack.length) {
    while (curr) { stack.push(curr); curr = curr.left; } // dive to smallest
    curr = stack.pop();                           // next smallest value
    if (--k === 0) return curr.val;               // k-th visited -> answer
    curr = curr.right;                            // continue with right subtree
  }
  return undefined;                               // k larger than size
}

// ============================================
// APPROACH 3: Recursive with early exit
// Time: O(h + k) | Space: O(h)
// ============================================
function kthSmallestRec(root, k) {
  let count = 0, ans;                             // visited so far, answer
  function dfs(n) {
    if (!n || count >= k) return;                 // stop when found
    dfs(n.left);                                  // smaller first
    count++;                                      // visit current
    if (count === k) { ans = n.val; return; }     // found
    dfs(n.right);                                 // then larger
  }
  dfs(root);
  return ans;
}

// ============================================
// TEST CASES
// ============================================
const a = buildTree([3, 1, 4, null, 2]);
console.log(kthSmallest(a, 1));                   // 1
console.log(kthSmallest(a, 3));                   // 3
console.log(kthSmallest(a, 4));                   // 4
const b = buildTree([5, 3, 6, 2, 4, null, null, 1]);
console.log(kthSmallest(b, 3));                   // 3
console.log(kthSmallestRec(b, 6));                // 6
console.log(kthSmallestBrute(b, 1));              // 1
console.log(kthSmallest(a, 10));                  // undefined
```

---

## 🔍 Why It Works
Left subtree < node < right subtree for every node, so inorder emits an ascending sequence. We only descend until the k-th emission, so we avoid visiting the whole tree when k is small.
हिंदी: inorder = ascending order, इसलिए k-वाँ visit ही k-वाँ सबसे छोटा है।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Full inorder array | O(n) | O(n) |
| Iterative early stop | O(h + k) | O(h) |
| Recursive early stop | O(h + k) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Kth LARGEST — reverse inorder (right, node, left)
function kthLargest(root, k) {
  const stack = [];
  let curr = root;
  while (curr || stack.length) {
    while (curr) { stack.push(curr); curr = curr.right; } // go to largest
    curr = stack.pop();
    if (--k === 0) return curr.val;               // k-th largest
    curr = curr.left;
  }
}
console.log(kthLargest(b, 2));                    // 5

// VARIANT 2 (Follow-up): BST with frequent inserts/deletes and many kth queries
//   Store subtree size in each node -> O(h) per query:
//   if k <= leftSize -> go left; if k == leftSize+1 -> node; else go right with k-leftSize-1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: sort all values after a generic traversal — ignores the BST property (O(n log n))

// ❌ Wrong: treating k as 0-indexed
return arr[k];            // off by one
// ✅ Correct: arr[k - 1]

// ❌ Wrong: forgetting to stop early and continuing the full traversal
```

---

## 🎯 Interview Tip
Say: "Inorder gives sorted order, so I stop at the k-th node — O(h + k)." For the follow-up with frequent updates, propose augmenting nodes with subtree sizes (order-statistic tree).

---

## 🔗 Related Problems
→ D164 (Validate BST) | D165 (LCA of BST) | D025 (Traversals) | D167 (Level Order)
