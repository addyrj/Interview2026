---

# D160. Maximum Depth of Binary Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #104 | Asked: Amazon, Microsoft, Google, Adobe

---

## ❓ Problem
Given the root of a binary tree, return its maximum depth — the number of nodes on the longest path from the root down to the farthest leaf.

```
Tree:     3
         / \
        9  20
           / \
          15  7

Output: 3
```

---

## 💡 Quick Concept (2 lines only)
Depth of a node = 1 + max(depth of left, depth of right); an empty tree has depth 0. Recursion (DFS) or level-by-level BFS both work.
हिंदी: depth = 1 + max(left depth, right depth); खाली tree की depth 0।

---

## ✅ Solution

```javascript
// TreeNode class
class TreeNode {
  constructor(val, left = null, right = null) {
    this.val = val; this.left = left; this.right = right; // store value and children
  }
}

// Build tree from level-order array (null = missing node)
function buildTree(arr) {
  if (!arr || !arr.length) return null;           // empty input -> empty tree
  const root = new TreeNode(arr[0]);              // first value is the root
  const queue = [root];                           // nodes waiting for children
  let i = 1;                                      // index of next value
  while (queue.length && i < arr.length) {
    const node = queue.shift();                   // take next parent
    if (arr[i] != null) {                         // left child exists?
      node.left = new TreeNode(arr[i]);
      queue.push(node.left);
    }
    i++;
    if (i < arr.length && arr[i] != null) {       // right child exists?
      node.right = new TreeNode(arr[i]);
      queue.push(node.right);
    }
    i++;
  }
  return root;
}

// ============================================
// APPROACH 1: Recursive DFS (Optimal, simplest)
// Time: O(n) | Space: O(h) recursion stack (h = height)
// ============================================
function maxDepth(root) {
  if (!root) return 0;                            // base case: empty tree
  const left = maxDepth(root.left);               // depth of left subtree
  const right = maxDepth(root.right);             // depth of right subtree
  return 1 + Math.max(left, right);               // count this node + deeper side
}

// ============================================
// APPROACH 2: Iterative BFS (level counting)
// Time: O(n) | Space: O(w) (w = max width)
// ============================================
function maxDepthBFS(root) {
  if (!root) return 0;                            // empty tree
  let depth = 0;                                  // levels seen so far
  const queue = [root];                           // start with root level
  while (queue.length) {
    const size = queue.length;                    // nodes in current level
    for (let i = 0; i < size; i++) {
      const node = queue.shift();                 // process one node
      if (node.left) queue.push(node.left);       // enqueue next level
      if (node.right) queue.push(node.right);
    }
    depth++;                                      // one full level done
  }
  return depth;
}

// ============================================
// APPROACH 3: Iterative DFS with explicit stack (avoids recursion limit)
// Time: O(n) | Space: O(h)
// ============================================
function maxDepthStack(root) {
  if (!root) return 0;                            // empty tree
  let best = 0;                                   // deepest seen
  const stack = [[root, 1]];                      // pairs of [node, depth]
  while (stack.length) {
    const [node, d] = stack.pop();                // take a node
    best = Math.max(best, d);                     // update answer
    if (node.left) stack.push([node.left, d + 1]);
    if (node.right) stack.push([node.right, d + 1]);
  }
  return best;
}

// ============================================
// TEST CASES
// ============================================
const t1 = buildTree([3, 9, 20, null, null, 15, 7]);
console.log(maxDepth(t1));                        // 3
console.log(maxDepthBFS(t1));                     // 3
console.log(maxDepthStack(t1));                   // 3
console.log(maxDepth(buildTree([1, null, 2])));   // 2
console.log(maxDepth(null));                      // 0
console.log(maxDepth(buildTree([1])));            // 1
```

---

## 🔍 Why It Works
Every root-to-leaf path passes through the root, so the best path goes through the deeper child. Solving the same question for children and adding 1 gives the answer. BFS counts levels directly.
हिंदी: गहरा वाला child चुनो और उसमें 1 जोड़ दो; BFS में हर level पर count बढ़ाओ।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Recursive DFS | O(n) | O(h) — O(n) skewed, O(log n) balanced |
| BFS | O(n) | O(w) |
| Iterative DFS | O(n) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Minimum depth (LeetCode #111) — nearest LEAF, not nearest null
function minDepth(root) {
  if (!root) return 0;                            // empty tree
  if (!root.left) return 1 + minDepth(root.right);   // only right child: must go right
  if (!root.right) return 1 + minDepth(root.left);   // only left child: must go left
  return 1 + Math.min(minDepth(root.left), minDepth(root.right)); // both: take shorter
}
console.log(minDepth(t1));                        // 2

// VARIANT 2: Check height-balanced tree (LeetCode #110)
function isBalanced(root) {
  function h(n) {
    if (!n) return 0;                             // empty height
    const l = h(n.left);                          // left height or -1
    if (l === -1) return -1;                      // already unbalanced
    const r = h(n.right);                         // right height or -1
    if (r === -1 || Math.abs(l - r) > 1) return -1; // unbalanced marker
    return 1 + Math.max(l, r);                    // normal height
  }
  return h(root) !== -1;
}
console.log(isBalanced(t1));                      // true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: minDepth as 1 + min(left, right) — a missing child counts as depth 0
//    so a node with one child wrongly returns 1 (it is not a leaf!)
// ✅ Correct: handle single-child nodes separately (see minDepth above)

// ❌ Wrong: returning 1 for empty tree
if (!root) return 1;
// ✅ Correct: empty tree depth is 0
if (!root) return 0;
```

---

## 🎯 Interview Tip
Say: "Recursive is 3 lines, O(n) time, O(h) space. For a skewed tree with 10^5 nodes recursion may overflow, so I'd mention the BFS or explicit-stack version." Clarify whether depth counts nodes or edges.

---

## 🔗 Related Problems
→ D161 (Invert Binary Tree) | D168 (Diameter) | D025 (Tree Traversals) | D167 (Level Order)
