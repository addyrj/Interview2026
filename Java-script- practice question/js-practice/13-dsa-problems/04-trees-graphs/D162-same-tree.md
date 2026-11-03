---

# D162. Same Tree
# Category: DSA — Trees & Graphs
# Difficulty: ⭐ Easy | LeetCode #100 | Asked: Amazon, Microsoft, Bloomberg, Adobe

---

## ❓ Problem
Given the roots of two binary trees `p` and `q`, return true if they are structurally identical and every pair of corresponding nodes has the same value.

```
p:   1       q:   1        -> true
    / \          / \
   2   3        2   3

p:   1       q:   1        -> false (different structure)
    /             \
   2               2
```

---

## 💡 Quick Concept (2 lines only)
Walk both trees together. Both null -> equal; one null -> different; values differ -> different; else both subtrees must match.
हिंदी: दोनों trees साथ-साथ चलाओ - दोनों null = same, एक null = different, value अलग = different।

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
// APPROACH 1 (Brute force): Serialize both and compare strings
// Time: O(n) | Space: O(n)  — works, but uses extra memory
// ============================================
function serialize(root) {
  if (!root) return "#";                          // marker for null (keeps structure)
  return root.val + "(" + serialize(root.left) + "," + serialize(root.right) + ")";
}
function isSameTreeSerialize(p, q) {
  return serialize(p) === serialize(q);           // equal strings = equal trees
}

// ============================================
// APPROACH 2: Recursive DFS (Optimal)
// Time: O(n) | Space: O(h)
// ============================================
function isSameTree(p, q) {
  if (!p && !q) return true;                      // both empty -> same
  if (!p || !q) return false;                     // only one empty -> different
  if (p.val !== q.val) return false;              // values differ -> different
  return isSameTree(p.left, q.left) &&            // left subtrees match
         isSameTree(p.right, q.right);            // and right subtrees match
}

// ============================================
// APPROACH 3: Iterative (queue of pairs)
// Time: O(n) | Space: O(w)
// ============================================
function isSameTreeIter(p, q) {
  const queue = [[p, q]];                         // pairs to compare
  while (queue.length) {
    const [a, b] = queue.shift();                 // next pair
    if (!a && !b) continue;                       // both null: fine
    if (!a || !b || a.val !== b.val) return false; // mismatch found
    queue.push([a.left, b.left]);                 // compare left children
    queue.push([a.right, b.right]);               // compare right children
  }
  return true;                                    // no mismatch
}

// ============================================
// TEST CASES
// ============================================
console.log(isSameTree(buildTree([1, 2, 3]), buildTree([1, 2, 3])));        // true
console.log(isSameTree(buildTree([1, 2]), buildTree([1, null, 2])));        // false
console.log(isSameTree(buildTree([1, 2, 1]), buildTree([1, 1, 2])));        // false
console.log(isSameTree(null, null));                                        // true
console.log(isSameTreeIter(buildTree([1, 2, 3]), buildTree([1, 2, 3])));    // true
console.log(isSameTreeIter(buildTree([1, 2]), buildTree([1, null, 2])));    // false
console.log(isSameTreeSerialize(buildTree([1, 2, 3]), buildTree([1, 2, 3]))); // true
```

---

## 🔍 Why It Works
Two trees are equal exactly when their roots match and both pairs of subtrees are equal. Checking null cases first guarantees we never read `.val` of null. Short-circuit `&&` stops at the first mismatch.
हिंदी: root बराबर + left बराबर + right बराबर = same tree; null पहले check करो।

---

## 📊 Complexity

| Approach | Time | Space |
|---|---|---|
| Serialize | O(n) | O(n) |
| Recursive | O(n) | O(h) |
| Iterative | O(n) | O(w) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Subtree of Another Tree (LeetCode #572)
function isSubtree(root, sub) {
  if (!root) return !sub;                         // empty root only matches empty sub
  if (isSameTree(root, sub)) return true;         // match starting here
  return isSubtree(root.left, sub) || isSubtree(root.right, sub); // try children
}
console.log(isSubtree(buildTree([3, 4, 5, 1, 2]), buildTree([4, 1, 2]))); // true

// VARIANT 2: Symmetric tree = isSameTree(root.left, mirror of root.right) -> D163
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: compare only values, ignore shape
if (p.val !== q.val) return false;   // crashes if p or q is null

// ❌ Wrong: comparing traversals without null markers
// [1,2] and [1,null,2] have the same inorder/preorder values but different shape

// ✅ Correct: handle null cases first, then compare val, then recurse
```

---

## 🎯 Interview Tip
Say: "Three-way base case: both null, one null, values differ." Then mention the follow-up Subtree of Another Tree, which reuses this function.

---

## 🔗 Related Problems
→ D161 (Invert) | D163 (Symmetric Tree) | D160 (Max Depth) | D171 (Serialize Tree)
