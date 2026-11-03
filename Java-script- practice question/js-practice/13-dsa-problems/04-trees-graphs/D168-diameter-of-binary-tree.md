---

# D168. Diameter of Binary Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #543 | Asked: Facebook, Amazon, Google, Microsoft

---

## ❓ Problem
Return the length of the diameter of a binary tree — the number of EDGES on the longest path between any two nodes. The path may or may not pass through the root.

```
Tree:       1
           / \
          2   3
         / \
        4   5

Longest path: 4 -> 2 -> 1 -> 3 (or 5 -> 2 -> 1 -> 3) = 3 edges
Output: 3
```

---

## 💡 Quick Concept (2 lines only)
For each node, the longest path THROUGH it = height(left) + height(right). Compute heights bottom-up and track the maximum of that sum.
हिंदी: हर node से गुज़रने वाला सबसे लंबा path = left height + right height; इनमें से max रखो।

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
// APPROACH 1 (Brute force): at every node compute heights again
// Time: O(n^2) worst case (skewed) | Space: O(h)
// ============================================
function height(n) {
  if (!n) return 0;                               // empty height
  return 1 + Math.max(height(n.left), height(n.right)); // standard height
}
function diameterBrute(root) {
  if (!root) return 0;                            // empty tree
  const through = height(root.left) + height(root.right); // path via this node
  const inLeft = diameterBrute(root.left);        // best in left subtree
  const inRight = diameterBrute(root.right);      // best in right subtree
  return Math.max(through, inLeft, inRight);      // best overall
}

// ============================================
// APPROACH 2: Single-pass DFS computing height + updating best (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function diameterOfBinaryTree(root) {
  let best = 0;                                   // longest path seen (in edges)
  function depth(node) {
    if (!node) return 0;                          // empty subtree height 0
    const l = depth(node.left);                   // height of left side
    const r = depth(node.right);                  // height of right side
    best = Math.max(best, l + r);                 // path bending at this node
    return 1 + Math.max(l, r);                    // height reported to parent
  }
  depth(root);                                    // run DFS
  return best;
}

// ============================================
// TEST CASES
// ============================================
const t = buildTree([1, 2, 3, 4, 5]);
console.log(diameterOfBinaryTree(t));                       // 3
console.log(diameterBrute(t));                              // 3
console.log(diameterOfBinaryTree(buildTree([1, 2])));       // 1
console.log(diameterOfBinaryTree(buildTree([1])));          // 0
console.log(diameterOfBinaryTree(null));                    // 0
// Diameter not through the root:
const deep = buildTree([1, 2, null, 3, 4, 5, null, null, 6]);
console.log(diameterOfBinaryTree(deep));                    // 4
console.log(diameterBrute(deep));                           // 4
```

---

## 🔍 Why It Works
Any path has a highest node (its "bend"). The longest path whose bend is node X has length leftHeight + rightHeight. The diameter is the maximum over all X. Computing heights bottom-up gives both values in one pass.
हिंदी: हर path का एक सबसे ऊँचा node होता है; वहाँ l + r निकालो और सबमें से max लो।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Recompute heights | O(n^2) worst | O(h) |
| Single pass | O(n) | O(h) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Diameter counted in NODES -> best + 1 (for non-empty tree)
const diameterNodes = root => (root ? diameterOfBinaryTree(root) + 1 : 0);
console.log(diameterNodes(t));                    // 4

// VARIANT 2: Binary Tree Maximum Path Sum (LeetCode #124) — same pattern with values
function maxPathSum(root) {
  let best = -Infinity;                           // best path sum
  function gain(n) {
    if (!n) return 0;                             // nothing to add
    const l = Math.max(0, gain(n.left));          // ignore negative branches
    const r = Math.max(0, gain(n.right));
    best = Math.max(best, n.val + l + r);         // bend here
    return n.val + Math.max(l, r);                // extend one branch upward
  }
  gain(root);
  return best;
}
console.log(maxPathSum(buildTree([-10, 9, 20, null, null, 15, 7]))); // 42
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming the diameter passes through the root
return height(root.left) + height(root.right);

// ❌ Wrong: returning l + r as the height to the parent
return l + r;               // the parent can only extend ONE branch
// ✅ Correct: return 1 + Math.max(l, r) and store l + r in a global/closure variable
```

---

## 🎯 Interview Tip
Say: "Brute force is O(n^2) because heights are recomputed; I fold the diameter update into one height DFS for O(n)." Clarify edges vs nodes. This "return one thing, record another" trick reappears in max path sum.

---

## 🔗 Related Problems
→ D160 (Max Depth) | D166 (LCA) | D169 (Path Sum) | D025 (Traversals)
